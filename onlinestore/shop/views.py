from itertools import product

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, TemplateView
from rest_framework.reverse import reverse_lazy

from .models import (
    Category,
    Product,
    Favorite,
    FavoriteItem,
    Cart,
    CartItem,
    Order,
    OrderItem
)
from .forms import OrderForm


class ProductListView(ListView):
    template_name = 'shop/product/catalog-list.html'
    model = Product
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.filter(available=True)
        category_slug = self.kwargs.get('category_slug')
        gender = self.kwargs.get('gender')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Product.objects.filter(available=True)

class FavoriteListView(LoginRequiredMixin, ListView):
    model = FavoriteItem
    template_name = 'shop/favorites/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        favorite, _ = Favorite.objects.get_or_create(user=self.request.user)
        return FavoriteItem.objects.filter(favorite=favorite).select_related('product')

class AddToFavoriteView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        favorite, _ = Favorite.objects.get_or_create(user=request.user)
        FavoriteItem.objects.get_or_create(favorite=favorite, product=product)
        return redirect('product_detail', id=product_id, slug=product.slug)


class RemoveFromFavoriteView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        favorite = get_object_or_404(Favorite, user=request.user)
        FavoriteItem.objects.filter(favorite=favorite, product=product_id).delete()
        return redirect('favorites')


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Получаем количество из POST, по умолчанию 1
        quantity = int(request.POST.get('quantity', 1))

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(
                {'success': True, 'message': 'Товар добавлен в корзину', 'quantity': cart_item.quantity})

        return redirect('product_list')


class RemoveFromCartView(LoginRequiredMixin, DeleteView):
    model = CartItem

    def get_object(self, queryset=None):
        return get_object_or_404(CartItem, id=self.kwargs['cart_item_id'], cart__user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('cart_detail')


@login_required
def cart_detail(request):
    """Получение корзины пользователя"""
    cart = get_object_or_404(Cart, user=request.user)
    total_price = cart.total_price
    print(total_price)
    return render(request, 'shop/cart/detail.html', {'cart': cart, 'total_price': total_price})


class CartListViews(LoginRequiredMixin, ListView):
    model = CartItem
    template_name = 'shop/cart/detail.html'
    context_object_name = 'items'

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart).select_related('product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.get(user=self.request.user)
        context['total_price'] = cart.total_price
        return context

@login_required
def checkout(request):
    """Оформление заказа пользователя"""
    cart = get_object_or_404(Cart, user=request.user)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                total=cart.total_price,
                comment=form.cleaned_data['comment']
            )

            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )

            cart.items.all().delete()
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()

    return render(request, 'shop/order/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_detail(request, order_id):
    """Получение конкретного заказа пользователя"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order/detail.html', {'order': order})


@login_required
def order_list(request):
    """Получение всех заказов пользователя"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order/list.html', {'orders': orders})
