import os
import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters, ConversationHandler
)

# Logger sozlash
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
AD_TYPE, ORIGIN, DESTINATION, DETAILS, PRICE = range(5)

# SQLite yordamida e’lonlar saqlash
DB_PATH = "bobex_ads.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            ad_type TEXT,
            origin TEXT,
            destination TEXT,
            details TEXT,
            price TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_ad(user_id, data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO ads(user_id, ad_type, origin, destination, details, price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, data['ad_type'], data['origin'], data['destination'], data['details'], data['price']))
    conn.commit()
    conn.close()

def get_ads_by_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, ad_type, origin, destination, details, price FROM ads WHERE user_id = ?", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# Bot komandalar, handlerlar
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📝 E’lon joylashtirish", "📄 Mening e’lonlarim"], ["🔍 E’lonlarni ko‘rish", "/help"]]
    await update.message.reply_text(
        "Assalomu alaykum! BobEx logistika botiga xush kelibsiz.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start – Asosiy menyu\n"
        "/help – Yordam\n"
        "/cancel – E’lon berishni bekor qilish\n"
        "/myads – Mening e’lonlarim\n"
        "Yoki menyudan tugmani tanlang."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("E’lon berish bekor qilindi.")
    return ConversationHandler.END

async def myads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ads = get_ads_by_user(user_id)
    if not ads:
        await update.message.reply_text("Siz hali hech qanday e’lon bermagansiz.")
    else:
        text = "\n\n".join([f"➡️ ID:{r[0]}\nTuri: {r[1]}\n{r[2]} → {r[3]}\nNarx: {r[5]}\nTavsif: {r[4]}" for r in ads])
        await update.message.reply_text(text)

async def main_menu_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text
    if txt == "📝 E’lon joylashtirish":
        await update.message.reply_text("Yuk turini kiriting (masalan: Avtomobil / Kuryer):")
        return AD_TYPE
    elif txt == "📄 Mening e’lonlarim":
        await myads(update, context)
        return ConversationHandler.END
    elif txt == "🔍 E’lonlarni ko‘rish":
        await update.message.reply_text("Barcha e’lonlar hozircha mavjud emas.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Iltimos, menyudan tanlang.")
        return ConversationHandler.END

async def ad_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ad_type'] = update.message.text
    await update.message.reply_text("Jo‘natish manzilini kiriting:")
    return ORIGIN

async def origin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['origin'] = update.message.text
    await update.message.reply_text("Manzilga yetkazish manzilini kiriting:")
    return DESTINATION

async def destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['destination'] = update.message.text
    await update.message.
    reply_text("Yuk haqida batafsil yozing:")
    return DETAILS

async def details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['details'] = update.message.text
    await update.message.reply_text("Narxni kiriting:")
    return PRICE

async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['price'] = update.message.text
    data = context.user_data
    save_ad(update.effective_user.id, data)
    await update.message.reply_text(
        f"E’lon qabul qilindi:\n\nTuri: {data['ad_type']}\n{data['origin']} → {data['destination']}\nNarx: {data['price']}\nTavsif: {data['details']}"
    )
    return ConversationHandler.END

async def error_handler(update, context):
    logger.error("Xato:", exc_info=context.error)

def main():
    init_db()
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        logger.error("TOKEN topilmadi. BOT_TOKEN o'zgaruvchisini sozlang.")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()

    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^(📝 E’lon joylashtirish|📄 Mening e’lonlarim|🔍 E’lonlarni ko‘rish)$"), main_menu_text)],
        states={
            AD_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ad_type)],
            ORIGIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, origin)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, destination)],
            DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, details)],
            PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("myads", myads))
    app.add_handler(conv)
    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()
