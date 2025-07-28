import json
import logging

from django.conf import settings
from django.http.response import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authentication import SessionAuthentication

from shop.models import (
    Product, Cart, CartItem, ProductSize, Size,
    Order, OrderItem, TelegramUser
)
from .serializers import (
    ProductSerializer, CartItemSerializer
)

from .utils import safe_parse_webapp_init_data


logger = logging.getLogger(__name__)


# ---------- 🛒 Продукты ----------

class ProductListAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        products = Product.objects.filter(available=True)
        serializer = ProductSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)


class ProductDetailAPI(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, id):
        product = get_object_or_404(Product, id=id, available=True)
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)


# ---------- 🛍 Корзина ----------

class CartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        return Response(serializer.data)


class AddToCartAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        size_id = request.data.get('size_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id)
        size = get_object_or_404(ProductSize, id=size_id)

        product_size = get_object_or_404(ProductSize, product=product, size=size)
        if product_size.quantity < quantity:
            return Response({'message': 'Недостаточно товара'}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response({'success': True})


# ---------- 📦 Оформление заказа ----------

class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        # Отключаем CSRF-проверку
        logger.debug("CSRF check skipped")
        return

class CheckoutAPI(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logger.debug(f"POST /api/checkout/ от пользователя: {request.user} (аутентифицирован: {request.user.is_authenticated})")
        if not request.user.is_authenticated:
            logger.warning("Пользователь не аутентифицирован!")
            return Response({'message': 'Пользователь не аутентифицирован'}, status=status.HTTP_403_FORBIDDEN)

        try:
            cart = get_object_or_404(Cart, user=request.user)
        except Exception as e:
            logger.error(f"Корзина не найдена для пользователя {request.user}: {e}")
            return Response({'message': 'Корзина не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if not cart.items.exists():
            logger.info("Корзина пуста")
            return Response({'message': 'Корзина пуста'}, status=status.HTTP_400_BAD_REQUEST)

        comment = request.data.get('comment', '')
        logger.debug(f"Комментарий к заказу: {comment}")

        try:
            total = sum(item.product.price * item.quantity for item in cart.items.all())
            order = Order.objects.create(user=request.user, total=total, comment=comment)

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    quantity=item.quantity,
                    price=item.product.price
                )
            cart.items.all().delete()
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {e}")
            return Response({'message': 'Ошибка оформления заказа'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Заказ {order.id} успешно создан для пользователя {request.user}")
        return Response({'ok': True, 'order_id': order.id})



@method_decorator(csrf_exempt, name='dispatch')
class TelegramAuthView(View):
    def post(self, request, *args, **kwargs):
        print("POST /api/auth/ получен!")
        try:
            body = json.loads(request.body)
            init_data = body.get("init_data")
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        bot_token = settings.TELEGRAM_BOT_TOKEN

        try:
            parsed = safe_parse_webapp_init_data(bot_token, init_data, json.loads)
        except ValueError as e:
            print("Signature validation failed:", e)
            return JsonResponse({"error": "Invalid signature"}, status=403)

        user_data = parsed.get("user")
        telegram_id = user_data['id']
        username = user_data.get('username')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')

        tg_user, created = TelegramUser.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }
        )

        if tg_user.user is None:
            base_username = f"tg_{telegram_id}"
            user = User.objects.create_user(
                username=base_username,
                first_name=first_name,
                last_name=last_name,
                password=str(telegram_id) + last_name + str(telegram_id)
            )
            tg_user.user = user
            tg_user.save()
        else:
            user = tg_user.user

        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

        return JsonResponse({
            "ok": True,
            "user": parsed.get("user"),
            "redirect_url": "/"}
        )
