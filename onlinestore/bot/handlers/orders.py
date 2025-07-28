from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

async def get_active_orders(user_id):
    return [
        {"id": 1234, "status": "В пути"},
        {"id": 1235, "status": "Ожидает оплату"}
    ]

@router.callback_query(F.data == "active_orders")
async def show_active_orders(callback_query: types.CallbackQuery):
    orders = await get_active_orders(callback_query.from_user.id)

    if not orders:
        await callback_query.message.answer("У вас нет активных заказов.")
    else:
        text = "\n\n".join(
            [f"🛍 Заказ #{order['id']}\n📦 Статус: {order['status']}" for order in orders]
        )
        await callback_query.message.answer(text, parse_mode="HTML")

    # Убираем кнопки под сообщением (опционально)
    await callback_query.message.edit_reply_markup(reply_markup=None)

    await callback_query.answer()

