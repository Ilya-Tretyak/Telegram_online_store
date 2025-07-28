from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import LabeledPrice
from shop.models import Order, TelegramUser
from bot.bot_instance import bot
from keyboards.main import main_menu, orders_menu

from django.core.exceptions import ObjectDoesNotExist

from asgiref.sync import sync_to_async


router = Router()


@sync_to_async
def get_order_and_tg_user(order_id):
    order = Order.objects.get(id=order_id)
    tg_user = TelegramUser.objects.get(user=order.user)
    return order, tg_user


@router.message(CommandStart())
async def handle_deeplink_start(message: types.Message):
    args = ""
    if message.text and " " in message.text:
        _, args = message.text.split(" ", 1)

    if args.startswith("pay_"):
        try:
            order_id = int(args.split("_")[1])
        except (IndexError, ValueError):
            await message.answer("❌ Некорректный параметр оплаты.")
            return

        try:
            order, tg_user = await get_order_and_tg_user(order_id)
        except ObjectDoesNotExist:
            await message.answer("❌ Заказ не найден.")
            return
        except Exception as e:
            await message.answer(f"❌ Ошибка получения данных заказа: {e}")
            return

        if message.from_user.id != tg_user.telegram_id:
            await message.answer("❌ Этот заказ не принадлежит вам.")
            return

        prices = [LabeledPrice(label="Сумма заказа", amount=int(order.total * 100))]

        try:
            await bot.send_invoice(
                chat_id=message.chat.id,
                title="Оплата заказа",
                description="Подтвердите и оплатите ваш заказ",
                payload=f"order_{order_id}",
                provider_token="1744374395:TEST:f97d353956b41ca1ae23",
                currency="RUB",
                prices=prices,
                start_parameter="order-payment"
            )
        except Exception as e:
            await message.answer(f"❌ Ошибка при отправке счета: {e}")
        return

    await message.answer(
        "Добро пожаловать в наш магазин! 👋\nВыберите действие:",
        reply_markup=main_menu
    )

@router.message(F.text == "📋 Мои заказы")
async def show_orders_menu(message: types.Message):
    await message.answer(
        "Выберите категорию заказов:",
        reply_markup=orders_menu
    )
