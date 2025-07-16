import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

TOKEN = "7653469544:AAFH4xoRxu8-_nWy0CR1gXA1Nkv1txt3gqc"

SELECT_ACTION, SELECT_REGION, SELECT_DISTRICT, ENTER_CARGO_DETAILS = range(4)

REGIONS = {
    "Toshkent": ["Olmazor", "Chilonzor", "Yunusobod"],
    "Samarqand": ["Samarqand shahar", "Urgut", "Narpay"],
    "Andijon": ["Andijon shahar", "Asaka", "Marhamat"]
}

cargo_db = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        [KeyboardButton("📦 Yangi Yuk qo'shish")],
        [KeyboardButton("🔍 Yuklar ro'yxati")],
        [KeyboardButton("⚙️ Hisob raqamlarim")],
        [KeyboardButton("ℹ️ Yordam")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Assalomu alaykum, BobEx Birja botiga xush kelibsiz!\nKerakli bo‘limni tanlang:",
        reply_markup=reply_markup
    )
    return SELECT_ACTION

async def add_cargo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    buttons = [[InlineKeyboardButton(region, callback_data=f"region_{region}")] for region in REGIONS]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text("Yuk uchun viloyatni tanlang:", reply_markup=reply_markup)
    return SELECT_REGION

async def region_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    region = query.data.split('_')[1]
    context.user_data['region'] = region

    districts = REGIONS[region]
    buttons = [[InlineKeyboardButton(d, callback_data=f"district_{d}")] for d in districts]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        f"{region} viloyati tanlandi. Endi tumanni tanlang:",
        reply_markup=reply_markup
    )
    return SELECT_DISTRICT

async def district_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    district = query.data.split('_')[1]
    context.user_data['district'] = district

    await query.edit_message_text(
        f"Manzil: {context.user_data['region']}, {district}\n\n"
        "Endi yuk tafsilotlarini kiriting (turi, og'irligi, qo'shimcha ma'lumot):"
    )
    return ENTER_CARGO_DETAILS

async def cargo_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    details = update.message.text
    cargo_db.append({
        "user_id": update.message.from_user.id,
        "region": context.user_data['region'],
        "district": context.user_data['district'],
        "details": details
    })

    await update.message.reply_text(
        "✅ Yuk muvaffaqiyatli qo‘shildi!\nBosh menyuga qaytish uchun /start buyrug‘ini bosing."
    )
    return ConversationHandler.END

async def show_cargo_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not cargo_db:
        await update.message.reply_text("📭 Hozircha yuklar mavjud emas.")
        return
    text = "📦 Yuklar ro‘yxati:\n\n"
    for idx, cargo in enumerate(cargo_db, 1):
        text += (
            f"{idx}) Viloyat: {cargo['region']}\n"
            f"Tuman: {cargo['district']}\n"
            f"Tafsilot: {cargo['details']}\n\n"
        )
    await update.message.reply_text(text)

async def hisob_raqamlar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💳 Hisob raqamlaringiz:\n"
        "1. Uzcard: 8600 xxxx xxxx xxxx\n"
        "2. Humo: 9860 xxxx xxxx xxxx\n"
        "3. Payme, Click ham mavjud."
    )

async def yordam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🆘 Yordam uchun: @AdminUser\n"
        "Qo‘shimcha ma’lumot va yordam uchun admin bilan bog‘laning."
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("❌ Amal bekor qilindi. Bosh menyuga qaytish uchun /start bosing.")
    return ConversationHandler.END

def main():
    application = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^📦 Yangi Yuk qo'shish$"), add_cargo)],
        states={
            SELECT_REGION: [CallbackQueryHandler(region_selected, pattern="^region_")],
            SELECT_DISTRICT: [CallbackQueryHandler(district_selected, pattern="^district_")],
            ENTER_CARGO_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, cargo_details)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^🔍 Yuklar ro'yxati$"), show_cargo_list))
    application.add_handler(MessageHandler(filters.Regex("^⚙️ Hisob raqamlarim$"), hisob_raqamlar))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ Yordam$"), yordam))
    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
