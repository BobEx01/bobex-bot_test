import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import asyncio

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! Bobex botiga xush kelibsiz."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Bobex botining komandalar ro'yxati:\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam\n"
        "Botga matn yuboring, men sizga javob beraman."
    )
    await update.message.reply_text(help_text)

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    received_text = update.message.text
    await update.message.reply_text(f"Siz yozdingiz: {received_text}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception raised:", exc_info=context.error)

async def main():
    TOKEN = "7816762544:AAHr5nHRBjZCwMelQfr0IbHkSy8SxSkt9Po"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    app.add_error_handler(error_handler)

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
