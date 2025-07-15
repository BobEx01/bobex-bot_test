SCALPING DOMINION, [16.07.2025 1:40]
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from database import JB  # Sizning DB interfeysingiz (o'zgaruvchiga moslang)
from config import ADMIN_IDS  # admin id lar ro'yxati

# /start komandasi
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    username = update.effective_user.username

    # Foydalanuvchini bazaga qo'shish yoki tekshirish
    if not JB.user_exists(user_id):
        JB.add_user(user_id, username)
        # Yangi foydalanuvchiga 50,000 bonus berish
        JB.add_balance(user_id, 50000)
        update.message.reply_text(
            f"Assalomu alaykum, {username}! Siz ro'yxatdan o'tdingiz va 50,000 so'm bonus oldingiz."
        )
    else:
        update.message.reply_text(f"Assalomu alaykum, {username}! Botga xush kelibsiz.")

    # Asosiy menyuni ko'rsatish
    main_menu(update, context)

def main_menu(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Elon berish", callback_data='post_ad')],
        [InlineKeyboardButton("Shafyorlar", callback_data='shafyor_list')],
        [InlineKeyboardButton("Hisobim", callback_data='balance')],
        [InlineKeyboardButton("To'lovlar tarixi", callback_data='payment_history')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Menyu:", reply_markup=reply_markup)

# CallbackQuery asosida menu funksiyalarini boshqarish
def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data

    query.answer()

    if data == 'post_ad':
        # Bosh sahifa - viloyatni tanlash
        send_region_selection(query)
    elif data == 'shafyor_list':
        send_shafyorlar_list(query)
    elif data == 'balance':
        balance = JB.get_balance(user_id)
        query.edit_message_text(f"Sizning hisobingizda: {balance} so'm.")
    elif data == 'payment_history':
        payments = JB.get_payments(user_id)
        if payments:
            text = "To'lovlar tarixi:\n"
            for p in payments:
                text += f"ID: {p['id']} | Miqdor: {p['amount']} so'm | Holat: {p['status']}\n"
            query.edit_message_text(text)
        else:
            query.edit_message_text("Sizda to‘lov tarixi yo‘q.")
    else:
        query.edit_message_text("Notanish buyruq.")

# Viloyatlarni tanlash tugmasini yuborish
def send_region_selection(query):
    regions = JB.get_regions()  # DB dan viloyatlar ro'yxati (misol)
    keyboard = []
    for r in regions:
        keyboard.append([InlineKeyboardButton(r['name'], callback_data=f"region_{r['id']}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Viloyatni tanlang:", reply_markup=reply_markup)

# Viloyat bo‘yicha tumanlar ro‘yxatini yuborish
def region_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data.startswith("region_"):
        region_id = int(data.split('_')[1])
        districts = JB.get_districts(region_id)
        keyboard = []
        for d in districts:
            keyboard.append([InlineKeyboardButton(d['name'], callback_data=f"district_{d['id']}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text("Tumanni tanlang:", reply_markup=reply_markup)

# Tuman bo‘yicha e’lonlar ro‘yxatini ko‘rsatish
def district_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data

    if data.startswith("district_"):
        district_id = int(data.split('_')[1])
        ads = JB.get_ads_by_district(district_id)
        if not ads:
            query.edit_message_text("Bu tumanda e’lonlar yo‘q.")
            return
        text = f"Tumandagi e’lonlar soni: {len(ads)}\n\n"
        for ad in ads:
            # premium bo'lsa yuqoriga chiqarish
            prefix = "⭐ PREMIUM ⭐\n" if ad['is_premium'] else ""

SCALPING DOMINION, [16.07.2025 1:40]
text += f"{prefix}Yuk: {ad['cargo_desc']}\nOg'irligi: {ad['weight']} kg\nTo'lov: {ad['payment']} so'm\n\n"
        query.edit_message_text(text)

# Shafyorlar ro'yxatini yuborish
def send_shafyorlar_list(query):
    shafyors = JB.get_shafyors()
    if not shafyors:
        query.edit_message_text("Hozirda shafyorlar mavjud emas.")
        return
    text = "Shafyorlar ro'yxati:\n"
    for sh in shafyors:
        text += f"{sh['name']} - To'lov: {sh['payment']} so'm\n"
    query.edit_message_text(text)

# Admin uchun to‘lovni tasdiqlash (qo‘l bilan)
def approve_payment(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("Sizda buni bajarish huquqi yo‘q.")
        return

    try:
        payment_id = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("To‘lov ID sini to‘g‘ri kiriting. Masalan: /approve_payment 123")
        return

    # To‘lov holatini yangilash
    JB.update_payment_status(payment_id, 'tasdiqlangan')
    update.message.reply_text(f"To‘lov ID {payment_id} tasdiqlandi.")

# To‘lovni rad etish (admin)
def reject_payment(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        update.message.reply_text("Sizda buni bajarish huquqi yo‘q.")
        return

    try:
        payment_id = int(context.args[0])
    except (IndexError, ValueError):
        update.message.reply_text("To‘lov ID sini to‘g‘ri kiriting. Masalan: /reject_payment 123")
        return

    JB.update_payment_status(payment_id, 'rad etilgan')
    update.message.reply_text(f"To‘lov ID {payment_id} rad etildi.")

# To‘lov qildim tugmasi bosilganda
def payment_made_handler(update: Update, context: CallbackContext):
    update.message.reply_text(
        "To'lovni amalga oshiring, keyin chek (rasm) yuboring va summani kiriting."
    )
    # Keyingi bosqichlar uchun kontekstga to'lov jarayoni yozilishi mumkin

# Profilni ko‘rish
def profile_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    profile = JB.get_user_profile(user_id)
    if not profile:
        update.message.reply_text("Profil topilmadi.")
        return
    text = f"Profil ma'lumotlari:\nFoydalanuvchi: @{profile['username']}\nHisob: {profile['balance']} so'm"
    update.message.reply_text(text)

# Hisob balansini ko‘rsatish
def balance_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    balance = JB.get_balance(user_id)
    update.message.reply_text(f"Sizning hisobingizda: {balance} so'm")

# To‘lov tarixini ko‘rsatish
def payment_history_handler(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    payments = JB.get_payments(user_id)
    if not payments:
        update.message.reply_text("To‘lov tarixi mavjud emas.")
        return
    text = "To‘lovlar tarixi:\n"
    for p in payments:
        text += f"ID: {p['id']} | Miqdor: {p['amount']} so'm | Holat: {p['status']}\n"
    update.message.reply_text(text)

# Handlerlarni ro'yxatga olish funksiyasi
def setup_handlers(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("approve_payment", approve_payment))
    dispatcher.add_handler(CommandHandler("reject_payment", reject_payment))
    dispatcher.add_handler(CommandHandler("profile", profile_handler))
    dispatcher.add_handler(CommandHandler("balance", balance_handler))
    dispatcher.add_handler(CommandHandler("payment_history", payment_history_handler))

    dispatcher.add_handler(CallbackQueryHandler(callback_handler, pattern='^(post_ad|shafyor_list|balance|payment_history)$'))
    dispatcher.add_handler(CallbackQueryHandler(region_callback, pattern=r"^region_\d+$"))
    dispatcher.add_handler(CallbackQueryHandler(district_callback, pattern=r"^district_\d+$"))

    # Qo'shimcha xabarlar uchun handlerlar qo'shing, masalan, rasm, to'lov chekini qabul qilish va boshqalar
