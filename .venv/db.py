import asyncio
from datetime import datetime, timedelta
import aiosqlite

DB_PATH = 'smart_dorm_db.db'

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id BIGINT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            room TEXT NOT NULL
        )
        ''')
        await db.execute('''
        CREATE TABLE IF NOT EXISTS washings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            machine  TEXT NOT NULL,
            notified BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        ''')
        # await db.execute('DROP TABLE washings')
        # await db.execute('DROP TABLE users')
        await db.commit()

async def add_user(chat_id, name, room):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR IGNORE INTO users (chat_id, name, room) VALUES (?, ?, ?)', (chat_id, name, room))
        await db.commit()

async def get_user_id(chat_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT id FROM users WHERE chat_id = ?', (chat_id,))
        result = await cursor.fetchone()
        return result[0]

async def get_user_data(chat_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT name, room FROM users WHERE chat_id = ?', (chat_id,))
        result = await cursor.fetchone()
        return result

async def add_washing(chat_id, day, time, machine):
    user_id = await get_user_id(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        if user_id:
            await db.execute(
                'INSERT INTO washings (user_id, day, time, machine) VALUES (?, ?, ?, ?)',
                (user_id, day, time, machine)
            )
            await db.commit()

async def delete_washing(chat_id, day, time, machine):
    user_id = await get_user_id(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        if user_id:
            await db.execute(
                'DELETE FROM washings WHERE user_id=? AND day=? AND time=? AND machine=?',
                (user_id, day, time, machine)
            )
            await db.commit()