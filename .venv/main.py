import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from handlers import user_router

ALLOWED_UPDATES = ['message', 'callback_query']

logging.basicConfig(level = logging.INFO)

bot = Bot(token = '7693169019:AAEibxKj0eixEwpWv7GXsBwTAR_HBVITD3A')

dp = Dispatcher()
dp.include_router(user_router)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())
