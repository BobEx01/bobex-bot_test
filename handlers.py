from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from database import Database
from config import ADMIN_ID, CARD_NUMBER, CARD_OWNER

db = DB()

def start(update: Update, context: CallbackContext):
    user = update.effective_user
    db.add_user(user.id, user.username)
    update.message.reply_text(f"Salom {user.first_name}, Bobex yuk birjasiga xush kelibsiz!")

def profile(update: Update, context: CallbackContext):
    user = update.effective_user
    profil = db.get_user_profile(user.id)
    if profil:
        update.message.reply_text(f"Sizning profil:\nUsername: @{profil['username']}\nBalans: {profil['balance']} so'm")
    else:
        update.message.reply_text("Profil topilmadi.")

def balans(update: Update, context: CallbackContext):
    user = update.effective_user
    balans = db.get_balance(user.id)
    update.message.reply_text(f"Joriy balansingiz: {balans} so'm")

def tolovi_tarixi(update: Update, context: CallbackContext):
    user = update.effective_user
    tarix = db.get_payment_history(user.id)
    if tarix:
        matn = "To‘lovlar tarixi:\n"
        for item in tarix:
            matn += f"- {item['amount']} so'm | {item['date']}\n"
        update.message.reply_text(matn)
    else:
        update.message.reply_text("To‘lov tarixi bo‘sh.")

def payment(update: Update, context: CallbackContext):
    user = update.effective_user
    text = f"To‘lov uchun karta ma’lumotlari:\n\nKarta: {CARD_NUMBER}\nEga: {CARD_OWNER}\n\nTo‘lov qilingandan so‘ng tasdiqlang."
    update.message.reply_text(text)

def add_elon(update: Update, context: CallbackContext):
    user = update.effective_user
    update.message.reply_text("Yangi e’lon qo‘shish uchun yuk nomini yozing:")

def view_elonlar(update: Update, context: CallbackContext):
    elonlar = db.get_all_elon()
    if elonlar:
        text = "Aktiv e’lonlar:\n"
        for elon in elonlar:
            text += f"{elon['title']} - {elon['price']} so'm\n"
        update.message.reply_text(text)
    else:
        update.message.reply_text("Hozircha e’lonlar yo‘q.")

def admin_approve(update: Update, context: CallbackContext):
    if update.effective_user.id != ADMIN_ID:
        update.message.reply_text("Bu buyruq faqat admin uchun.")
        return
    update.message.reply_text("Qaysi to‘lovni tasdiqlashni xohlaysiz? ID yuboring.")

def chat(update: Update, context: CallbackContext):
    update.message.reply_text("Yuk egasiga murojaat uchun bu yerda yozing. Diqqat! Telefon raqam yoki boshqa aloqa usulini yuborish mumkin emas.")

def bonus_system(update: Update, context: CallbackContext):
    update.message.reply_text("Yangi foydalanuvchi chaqirsangiz 2000 so‘m bonus olasiz!\nObunachi bonusi: 50,000 so‘m.")

def vip_obuna(update: Update, context: CallbackContext):
    update.message.reply_text("VIP obuna 1 oyga 1,000,000 so‘m. VIP xizmatlar bepul!")

def aksiyalar(update: Update, context: CallbackContext):
    update.message.reply_text("Juma kungi aksiya: Barcha xizmatlarga 50% chegirma!")

def setup_handlers(application):
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("profil", profile))
    application.add_handler(CommandHandler("balans", balans))
    application.add_handler(CommandHandler("tolov", payment))
    application.add_handler(CommandHandler("tolov_tarixi", tolovi_tarixi))
    application.add_handler(CommandHandler("elon_qoshish", add_elon))
    application.add_handler(CommandHandler("elonlar", view_elonlar))
    application.add_handler(CommandHandler("chat", chat))
    application.add_handler(CommandHandler("bonus", bonus_system))
    application.add_handler(CommandHandler("vip", vip_obuna))
    application.add_handler(CommandHandler("aksiya", aksiyalar))
    application.add_handler(CommandHandler("tasdiq", admin_approve))
