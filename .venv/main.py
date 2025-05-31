import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.filters.command import Command
from handlers import user_router
from datetime import datetime, time, timedelta
from sheets_asyn import update_table
from db import init_db
from notification import send_notifications

ALLOWED_UPDATES = ['message', 'callback_query']

logging.basicConfig(level = logging.INFO)

bot = Bot(token = '7693169019:AAEibxKj0eixEwpWv7GXsBwTAR_HBVITD3A')

dp = Dispatcher()
dp.include_router(user_router)

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes = 1)
async def scheduled_notifications():
    now = datetime.now().time()
    start_time = time(6, 48)
    end_time = time(20, 20)
    if now >= start_time and now <= end_time:
        await send_notifications(bot)

@scheduler.scheduled_job('cron', hour=1, minute=00)
async def scheduled_update_table():
    await update_table()

async def main():
    await init_db()
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())
