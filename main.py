import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

TOKEN = "7653469544:AAFH4xoRxu8-_nWy0CR1gXA1Nkv1txt3gqc"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Holatlar (states)
YUK_QOSHISH, SHOFR_QOSHISH = range(2)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_keyboard = [['🚛 Yuk qo‘shish', '🚚 Shofyor elon qo‘shish'],
                      ['📦 Yuklarni ko‘rish', '👷 Shofyorlarni ko‘rish'],
                      ['ℹ️ Yordam']]
    await update.message.reply_text(
        "BobEx Birja Botiga xush kelibsiz! Kerakli bo‘limni tanlang:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)
    )

# YUK QO‘SHISH
async def yuk_qoshish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yuk eloningizni matn ko‘rinishida yozing:", reply_markup=ReplyKeyboardRemove())
    return YUK_QOSHISH

async def save_yuk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    yuk_info = update.message.text
    context.user_data['yuk'] = yuk_info
    await update.message.reply_text("Yuk eloningiz saqlandi.")
    return ConversationHandler.END

# SHOFR QO‘SHISH
async def shofr_qoshish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Shofyor eloningizni matn ko‘rinishida yozing:", reply_markup=ReplyKeyboardRemove())
    return SHOFR_QOSHISH

async def save_shofr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shofr_info = update.message.text
    context.user_data['shofr'] = shofr_info
    await update.message.reply_text("Shofyor eloningiz saqlandi.")
    return ConversationHandler.END

# YUKLARNI KO‘RISH
async def yuklarni_korish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    yuk = context.user_data.get('yuk', 'Yuklar hali qo‘shilmagan.')
    await update.message.reply_text(f"Yuklar: {yuk}")

# SHOFRLARNI KO‘RISH
async def shofrlarni_korish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shofr = context.user_data.get('shofr', 'Shofyorlar hali qo‘shilmagan.')
    await update.message.reply_text(f"Shofyorlar: {shofr}")

# YORDAM
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Yordam uchun admin bilan bog‘laning.")

# RAQAM YOZISHNI BLOKLASH
async def block_numbers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if any(char.isdigit() for char in text):
        await update.message.reply_text("Raqam yozish mumkin emas!")
    else:
        await update.message.reply_text("Xabaringiz qabul qilindi.")

# BEKOR QILISH
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('🚛 Yuk qo‘shish'), yuk_qoshish),
            MessageHandler(filters.Regex('🚚 Shofyor elon qo‘shish'), shofr_qoshish)
        ],
        states={
            YUK_QOSHISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_yuk)],
            SHOFR_QOSHISH: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_shofr)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Regex('📦 Yuklarni ko‘rish'), yuklarni_korish))
    app.add_handler(MessageHandler(filters.Regex('👷 Shofyorlarni ko‘rish'), shofrlarni_korish))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, block_numbers))

    app.run_polling()

if __name__ == '__main__':
    main()
