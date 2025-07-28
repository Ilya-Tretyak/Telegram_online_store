from aiogram.types import(
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="📦 Открыть магазин",
            web_app=WebAppInfo(url="Ссылка на miniapp")
        )]
    ]
)

"""Клавиатура просмотра заказов"""
orders_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Активные заказы", callback_data="active_orders")],
        [InlineKeyboardButton(text="✅ Завершённые заказы", callback_data="completed_orders")]
    ]
)
