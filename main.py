mport logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
import asyncio

# Logger sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# /start komandasi uchun handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}! Bobex botiga xush kelibsiz."
    )

# /help komandasi uchun handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "Bobex botining komandalar ro'yxati:\n"
        "/start - Botni ishga tushirish\n"
        "/help - Yordam\n"
        "Botga matn yuboring, men sizga javob beraman."
    )
    await update.message.reply_text(help_text)

# Oddiy matnli xabarlarga javob (echo)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    received_text = update.message.text
    await update.message.reply_text(f"Siz yozdingiz: {received_text}")

# Xatoliklarni qayd etish
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Exception raised:", exc_info=context.error)
    # Istasangiz, foydalanuvchiga xatolik haqida xabar ham berishingiz mumkin:
    # if update and update.effective_message:
    #     await update.effective_message.reply_text("Kechirasiz, xatolik yuz berdi.")

async def main():
    # Bot tokenini shu yerga joylang
    TOKEN = "7816762544:AAHr5nHRBjZCwMelQfr0IbHkSy8SxSkt9Po"

    # Ilovani yaratish
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlerlarni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Xatoliklar handleri
    app.add_error_handler(error_handler)

    # Botni ishga tushirish
    await app.run_polling()

if name == "__main__":
    asyncio.run(main())
