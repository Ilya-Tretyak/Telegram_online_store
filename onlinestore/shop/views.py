from django.shortcuts import (
    render,
    get_object_or_404,
    redirect
)
from django.contrib.auth.decorators import login_required

from .models import (
    Category,
    Product,
    Cart,
    CartItem, Order, OrderItem
)
from .forms import OrderForm



'''Получение всех товаров'''
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    return render(
        request,
        'shop/product/list.html',
        {'category': category, 'categories': categories, 'products': products}
    )

'''Получение информации об определенном товаре'''
def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'shop/product/detail.html', {'product': product})


'''Добавление товара в корзину'''
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('product_list')

'''Удаления товара из корзины'''
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart_detail')

'''Получение корзины пользователя'''
@login_required
def cart_detail(request):
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, 'shop/cart/detail.html', {'cart': cart})

'''Оформление заказа пользователя'''
@login_required
def checkout(request):
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


'''Получение конкретного заказа пользователя'''
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order/detail.html', {'order': order})

'''Получение всех заказов пользователя'''
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/order/list.html', {'orders': orders})
