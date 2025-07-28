import os

from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from django.conf import settings

User = get_user_model()


class Category(models.Model):
    """Модель для категорий"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель для товаров"""
    GENDER_CHOICES = (
        ('male', 'МУЖСКОЕ'),
        ('female', 'ЖЕНСКОЕ'),
        ('kid', 'ДЕТСКОЕ'),
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='female',
        verbose_name='Пол'
    )
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Цена'
    )
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Изображение"
    )
    available = models.BooleanField(default=True, verbose_name='Доступен')
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated = models.DateTimeField(auto_now=True, verbose_name='Обновлен')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.id, self.slug])

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении объекта
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)



class Size(models.Model):
    """Модель для размеров"""
    name = models.CharField(max_length=20, verbose_name='Название размера', default='temp_size')
    code = models.SlugField(unique=True, verbose_name='Код размера', default='temp_code')

    class Meta:
        verbose_name = 'Размер'
        verbose_name_plural = 'Размеры'

    def __str__(self):
        return f'{self.name}'


class ProductSize(models.Model):
    """Связующая модель для кол-ва товаров по размерам"""
    product = models.ForeignKey(
        Product,
        related_name='product_sizes',
        on_delete=models.CASCADE,
        verbose_name='Товар'
    )
    size = models.ForeignKey(
        Size,
        related_name='size_products',
        on_delete=models.CASCADE,
        verbose_name="Размер"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Колличество'
    )

    class Meta:
        verbose_name = 'Размер товара'
        verbose_name_plural = 'Размеры товаров'
        unique_together = ('product', 'size')

    def __str__(self):
        return f"{self.size.name}"

class Favorite(models.Model):
    """Модель для избранных товаров"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE, related_name='favorites',
    )

    def __str__(self):
        return f"Избранное пользователя: {self.user.username}"


class FavoriteItem(models.Model):
    """Модель для товара в избранном"""
    favorite = models.ForeignKey(Favorite, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.name


class Cart(models.Model):
    """Модель для корзин пользователей'"""
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE,
        related_name = 'cart',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Корзина пользователя: {self.user.username}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """Модель позиции в корзине пользователей"""
    cart = models.ForeignKey(
        Cart,
        on_delete = models.CASCADE,
        related_name = 'items'
    )
    product = models.ForeignKey(
        Product,
        on_delete = models.CASCADE,
        related_name = 'cart_items'
    )

    size = models.ForeignKey(
        Size,
        on_delete = models.CASCADE,
        verbose_name="Размер",
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product', 'size')

    def __str__(self):
        size_info = f" ({self.size.name})" if self.size else ""
        return f"{self.quantity} x {self.product.name}{size_info}"

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def is_available(self):
        """Проверяет доступность выбранного размера и количества"""
        if self.size:
            try:
                product_size = ProductSize.objects.get(
                    product=self.product,
                    size=self.size
                )
                return product_size.quantity >= self.quantity
            except ProductSize.DoesNotExist:
                return False
        return True


class Order(models.Model):
    """Модель заказов пользователей"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progres', 'В обработке'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE,
        related_name = 'orders',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id}"


class OrderItem(models.Model):
    """Модель позиций в заказе пользователей"""
    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        related_name = 'items',
    )
    product = models.ForeignKey(
        Product,
        on_delete = models.PROTECT
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        verbose_name="Размер",
        null=True,
        blank=True
    )

    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"




class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='telegram_user',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username or str(self.telegram_id)
