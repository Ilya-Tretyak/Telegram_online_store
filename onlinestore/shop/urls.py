from django.urls import path
from . import views


urlpatterns = [
# urls для order
    path('order/checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/', views.order_list, name='order_list'),
#urls для favorite
    path('favorites/', views.FavoriteListView.as_view(), name='favorites'),
    path('favorites/add/<int:product_id>/', views.AddToFavoriteView.as_view(), name='add_to_favorites'),
    path('favorites/remove/<int:product_id>/', views.RemoveFromFavoriteView.as_view(), name='remove_from_favorites'),

# urls для cart
    path('cart/', views.CartListViews.as_view(), name='cart_detail'),
    path('cart/add/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/<int:cart_item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
# urls для product
    path('', views.ProductListView.as_view(), name='product_list'),
    path('product/<int:id>/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('gender/<str:gender>/', views.ProductListView.as_view(), name='product_list_by_gender'),
    path('<slug:category_slug>/', views.ProductListView.as_view(), name='product_list_by_category'),
    path('<slug:category_slug>/gender/<str:gender>/', views.ProductListView.as_view(), name='product_list_by_category_gender'),
]