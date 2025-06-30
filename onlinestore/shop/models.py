import os

from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model

from django.conf import settings

User = get_user_model()


class Category(models.Model):
    """Модель для категорий"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель для товаров"""
    GENDER_CHOICES = (
        ('male', 'МУЖСКОЕ'),
        ('female', 'ЖЕНСКОЕ'),
        ('kid', 'ДЕТСКОЕ'),
    )

    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

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
    product = models.ForeignKey(Product, related_name='sizes', on_delete=models.CASCADE)
    value = models.CharField(max_length=20)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return f'{self.value}'


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
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.quantity * self.product.price


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
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
