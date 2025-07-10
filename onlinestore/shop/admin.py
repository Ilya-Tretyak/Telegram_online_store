from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from .models import Category, Product, Order, Size, ProductSize


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            output.append(
                f'<img src="{value.url}" style="max-height: 300px; display: block; margin-bottom: 10px; border-radius: 4px;"/>'
            )
        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(''.join(output))


class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1
    fields = ('size', 'quantity')
    verbose_name = "Доступный размер"
    verbose_name_plural = "Доступные размеры"
    autocomplete_fields = ['size']  # Добавляем поиск по размерам


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('display_thumbnail', 'name', 'price', 'category', 'gender', 'stock_status')
    list_display_links = ('display_thumbnail', 'name')
    list_filter = ('category', 'gender', 'available')
    search_fields = ('name', 'description')
    list_editable = ('price',)
    inlines = [ProductSizeInline]
    readonly_fields = ('display_image_preview',)
    autocomplete_fields = ['category']

    fieldsets = (
        (None, {
            'fields': ('category', 'gender', 'name', 'description', 'price', 'available')
        }),
        ('Изображение', {
            'fields': ('display_image_preview', 'image'),
            'classes': ('collapse', 'wide'),
        }),
    )

    def display_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 3px;"/>',
                obj.image.url
            )
        return "🖼️"

    display_thumbnail.short_description = 'Фото'

    def display_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 400px; border-radius: 5px; border: 1px solid #eee;"/>',
                obj.image.url
            )
        return "Изображение не загружено"

    display_image_preview.short_description = 'Превью'

    def stock_status(self, obj):
        total = sum(ps.quantity for ps in obj.product_sizes.all())
        if total > 10:
            return format_html('<span style="color: green;">✓ В наличии ({})</span>', total)
        elif total > 0:
            return format_html('<span style="color: orange;">Мало ({})</span>', total)
        return format_html('<span style="color: red;">Нет в наличии</span>')

    stock_status.short_description = 'Наличие'

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == 'image':
            kwargs['widget'] = AdminImageWidget
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')
    list_editable = ('code',)
    prepopulated_fields = {'code': ('name',)}


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'quantity', 'in_stock')
    list_filter = ('product__category', 'size')
    search_fields = ('product__name', 'size__name')
    list_editable = ('quantity',)
    autocomplete_fields = ['product', 'size']

    def in_stock(self, obj):
        if obj.quantity > 0:
            return format_html('<span style="color: green;">✓ {}</span>', obj.quantity)
        return format_html('<span style="color: red;">✗</span>')

    in_stock.short_description = 'В наличии'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'status', 'display_total')
    list_filter = ('status', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ('id', 'customer_info')

    def display_total(self, obj):
        # Предполагаем, что у Order есть связь с OrderItem через related_name='items'
        total = sum(item.price * item.quantity for item in obj.items.all())
        return f"{total} ₽"
    display_total.short_description = 'Сумма заказа'
