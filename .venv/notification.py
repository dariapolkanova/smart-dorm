import asyncio
import aiosqlite
from aiogram import Bot
from datetime import datetime, timedelta
from db import DB_PATH


async def send_notifications(bot):
    async with aiosqlite.connect(DB_PATH) as db:
        now = datetime.now()
        target_time = (now + timedelta(minutes=10)).strftime('%H:%M')

        cursor = await db.execute("""
            SELECT chat_id, washings.id, name, time, machine
            FROM washings JOIN users ON users.id = washings.user_id
            WHERE time=? AND notified=0
        """, (target_time,))

        result = await cursor.fetchall()

        for row in result:
            chat_id = row[0]
            await bot.send_message(chat_id, f"Напоминание: у тебя запланирована стирка через 10 минут! Номер машины - {row[4]}")

            db.execute("""
                UPDATE washings SET notified=1 WHERE id=?
            """, (row[1],))

        await db.commit()
        await db.close()