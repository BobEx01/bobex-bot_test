from telegram.ext import Application
from config import TOKEN
from handlers import setup_handlers
import asyncio

async def start_bot():
    app = Application.builder().token(TOKEN).build()

    setup_handlers(app)

    print("Bobex bot ishga tushdi...")
    await app.run_polling()

if __name__ == '__main__':
    asyncio.run(start_bot())
