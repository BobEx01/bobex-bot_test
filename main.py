from telegram import Update
from telegram.ext import ApplicationBuilder
from config import TOKEN
from handlers import setup_handlers
from database import Database

db = Database()

async def start_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    setup_handlers(app)

    print("Bobex bot ishga tushdi...")
    await app.run_polling()

if name == '__main__':
    import asyncio
    asyncio.run(start_bot())
