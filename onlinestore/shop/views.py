from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import Prefetch
from django.http import JsonResponse
from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView

from rest_framework.reverse import reverse_lazy

from .models import (
    Category,
    Product,
    Size,
    ProductSize,
    Favorite,
    FavoriteItem,
    Cart,
    CartItem,
    Order,
    OrderItem,
)
from .forms import OrderForm


class ProductListView(ListView):
    template_name = 'shop/product/catalog-list.html'
    model = Product
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        queryset = Product.objects.filter(available=True).select_related('category')
        category_slug = self.kwargs.get('category_slug')
        gender = self.kwargs.get('gender')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(category=category)

        if gender:
            queryset = queryset.filter(gender=gender)

        return queryset.prefetch_related(
            Prefetch('product_sizes', queryset=ProductSize.objects.filter(quantity__gt=0))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        user_favorites = []
        if self.request.user.is_authenticated:
            user_favorites = FavoriteItem.objects.filter(favorite__user=self.request.user).values_list('product_id', flat=True)
        context['user_favorites'] = user_favorites
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'shop/product/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'slug'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Product.objects.filter(available=True).prefetch_related(
            Prefetch('product_sizes',
                    queryset=ProductSize.objects.select_related('size').filter(quantity__gt=0))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['available_sizes'] = product.product_sizes.all()
        context['in_favorites'] = False

        if self.request.user.is_authenticated:
            context['in_favorites'] = FavoriteItem.objects.filter(
                favorite__user=self.request.user,
                product=product
            ).exists()

        return context

class FavoriteListView(LoginRequiredMixin, ListView):
    model = FavoriteItem
    template_name = 'shop/favorites/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return FavoriteItem.objects.filter(
            favorite__user=self.request.user
        ).select_related('product').prefetch_related('product__product_sizes')

class AddToFavoriteView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        favorite, _ = Favorite.objects.get_or_create(user=request.user)
        favorite_item, created = FavoriteItem.objects.get_or_create(
            favorite=favorite,
            product=product
        )

        return JsonResponse({
            'is_favorite': True,
            'product_id': product.id
        })

class RemoveFromFavoriteView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        favorite = get_object_or_404(Favorite, user=request.user)
        FavoriteItem.objects.filter(favorite=favorite, product=product_id).delete()
        return JsonResponse({
            'is_favorite': False,
            'product_id': product_id
        })


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Получаем количество из POST
        size_id = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))

        if size_id:
            try:
                size = Size.objects.get(id=int(size_id))
                product_size = ProductSize.objects.get(
                    product=product,
                    size=size,
                    quantity__gte=quantity
                )
            except (Size.DoesNotExist, ProductSize.DoesNotExist):
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Выбранный размер недоступен'
                    }, status=400)
                return redirect(product.get_absolute_url())
        else:
            size = None

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(
                {'success': True, 'message': 'Товар добавлен в корзину', 'quantity': cart_item.quantity})

        return redirect('cart_detail')


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
                    size = cart_item.size,
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


def miniapp_view(request):
    return render(request, "shop/miniapp.html")