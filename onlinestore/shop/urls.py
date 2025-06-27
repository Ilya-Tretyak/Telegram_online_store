from django.urls import path
from . import views


urlpatterns = [
# urls для order
    path('order/checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_list, name='order_list'),
# urls для cart
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
# urls для product
    path('', views.product_list, name='product_list'),
    path('gender/<str:gender>/', views.product_list, name='product_list_by_gender'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<slug:category_slug>/<str:gender>/', views.product_list, name='product_list_by_category_gender'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
]