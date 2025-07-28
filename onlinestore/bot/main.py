import sys
import os
import django
import asyncio


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlinestore.settings')

django.setup()


from bot_instance import bot, dp
from handlers import start, orders

dp.include_routers(
    start.router,
    orders.router,
)

if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
