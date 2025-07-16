from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "7653469544:AAFH4xoRxu8-_nWy0CR1gXA1Nkv1txt3gqc"

user_state = {}
user_data = {}

viloyatlar = {
    "Toshkent": ["Chilonzor", "Yunusobod", "Mirzo Ulug‘bek"],
    "Farg‘ona": ["Marg‘ilon", "Qo‘qon", "Farg‘ona shahri"],
    "Samarqand": ["Samarqand shahri", "Urgut", "Pastdarg‘om"]
}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["📦 Yuk joylash", "📋 Yuklarni ko‘rish"],
        ["💳 Hisob raqamlar", "📞 Aloqa"]
    ]
    await update.message.reply_text(
        "Assalomu alaykum! BobEx yuk birjasi botiga xush kelibsiz.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    user_state[update.message.chat_id] = None
    async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    text = update.message.text
    state = user_state.get(chat_id)

    if text == "📦 Yuk joylash":
        keyboard = [[v] for v in viloyatlar] + [["⬅️ Ortga"]]
        await update.message.reply_text("Viloyatni tanlang:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        user_state[chat_id] = "select_viloyat"

    elif state == "select_viloyat" and text in viloyatlar:
        user_data[chat_id] = {"viloyat": text}
        tumanlar = viloyatlar[text]
        keyboard = [[t] for t in tumanlar] + [["⬅️ Ortga"]]
        await update.message.reply_text("Tuman tanlang:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        user_state[chat_id] = "select_tuman"

    elif state == "select_tuman" and any(text in t for t in viloyatlar.values()):
        user_data[chat_id]["tuman"] = text
        await update.message.reply_text("Yuk nomini yozing:")
        user_state[chat_id] = "enter_yuk_nom"

    elif state == "enter_yuk_nom":
        user_data[chat_id]["yuk_nom"] = text
        await update.message.reply_text("Yuk og‘irligini kiriting (tonna):")
        user_state[chat_id] = "enter_ogirlik"

    elif state == "enter_ogirlik":
        user_data[chat_id]["ogirlik"] = text
        await update.message.reply_text("Yuk narxini kiriting (UZS):")
        user_state[chat_id] = "enter_narx"

    elif state == "enter_narx":
        user_data[chat_id]["narx"] = text
        await update.message.reply_text("Qo‘shimcha ma'lumot kiriting:")
        user_state[chat_id] = "enter_desc"

    elif state == "enter_desc":
        user_data[chat_id]["desc"] = text
        data = user_data[chat_id]
        await update.message.reply_text(
            f"✅ Yuk joylandi:\n"
            f"📍 {data['viloyat']} - {data['tuman']}\n"
            f"📦 {data['yuk_nom']}\n"
            f"⚖️ {data['ogirlik']} tonna\n"
            f"💰 {data['narx']} UZS\n"
            f"🗒 {data['desc']}"
        )
        user_state[chat_id] = None

    elif text == "📋 Yuklarni ko‘rish":
        await update.message.reply_text("Hozircha yuklar ro‘yxati mavjud emas. Tez orada chiqamiz!")

    elif text == "💳 Hisob raqamlar":
        await update.message.reply_text(
            "💳 To‘lov uchun hisob raqamlar:\n\n"
            "🏦 Uzcard: 5614 6822 1820 6250\n"
            "🏦 Click: +998 90 123 45 67\n"
            "🏦 Payme: +998 90 123 45 67\n"
            "🏦 Bank rekvizitlari:\n"
            "    Nomi: Bobex Logistics LLC\n"
            "    INN: 305123456\n"
            "    Hisob raqam: 20208000300123456789\n"
            "    Bank: Xalq Banki, Toshkent filiali\n\n"
            "⬅️ Ortga qaytish uchun '⬅️ Ortga' tugmasini bosing."
        )

    elif text == "📞 Aloqa":
        await update.message.reply_text("Bog‘lanish uchun: +998 90 123 45 67")

    elif text == "⬅️ Ortga":
        await start(update, context)

    else:
        await update.message.reply_text("Iltimos menyudan birini tanlang yoki /start ni bosing.")
        def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, message_handler))
    app.run_polling()
    if __name__ == "__main__":
    main()
