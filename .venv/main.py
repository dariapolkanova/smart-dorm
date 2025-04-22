import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.filters.command import Command
from handlers import user_router
from datetime import datetime, time, timedelta
from sheets_asyn import update_table

ALLOWED_UPDATES = ['message', 'callback_query']

logging.basicConfig(level = logging.INFO)

bot = Bot(token = '7693169019:AAEibxKj0eixEwpWv7GXsBwTAR_HBVITD3A')

dp = Dispatcher()
dp.include_router(user_router)

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=17, minute=41)
async def scheduled_job():
    await update_table()

async def main():
    scheduler.start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALLOWED_UPDATES)

if __name__ == "__main__":
    asyncio.run(main())
