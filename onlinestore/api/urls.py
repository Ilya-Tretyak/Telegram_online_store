from django.urls import path
from .views import (ProductListAPI,
                    ProductDetailAPI,
                    CartAPI,
                    AddToCartAPI,
                    CheckoutAPI,
                    TelegramAuthView
                    )

urlpatterns = [
    path('products/', ProductListAPI.as_view(), name='api_product_list'),
    path('products/<int:pk>/', ProductDetailAPI.as_view(), name='api_product_detail'),
    path('cart/', CartAPI.as_view(), name='api_cart_list'),
    path('cart/add/', AddToCartAPI.as_view(), name='api_cart_add'),
    path('checkout/', CheckoutAPI.as_view(), name='api_checkout'),
    path('auth/', TelegramAuthView.as_view(), name='telegram-auth'),
]