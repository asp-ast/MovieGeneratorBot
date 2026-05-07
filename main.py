import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession#

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

from database.engine import session_maker
from app.middlewares import DataBaseSession
from app.handlers import router
from database.engine import create_db


session = AiohttpSession(proxy = os.getenv('PROXY_URL'))#

bot = Bot(token = os.getenv('TOKEN'), session = session)
dp = Dispatcher()


async def on_startup(bot):
    first_time_launch = False
    if first_time_launch:
        await create_db()

async def on_shutdown(bot):
    print('бот выключен')


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DataBaseSession(session_pool = session_maker))

    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
