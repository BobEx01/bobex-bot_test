from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

from database import Database
from utils import is_admin, send_formatted_message

db = Database()

# --- 1. /start komandasi ---
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = user.id
    
    # Foydalanuvchini bazaga qo'shish yoki tekshirish
    if not db.get_user(user_id):
        db.add_user(user_id, user.full_name, user.username)
        
        # BONUS: yangi foydalanuvchiga 50,000 som bonus qo'shish
        db.update_balance(user_id, 50000)
        send_formatted_message(update, "Xush kelibsiz", [("🎁 Bonus", "Sizga 50,000 som bonus berildi!")])
    
    keyboard = [
        [InlineKeyboardButton("🧾 Profilim", callback_data="show_profile")],
        [InlineKeyboardButton("💳 To'lovlar tarixi", callback_data="payment_history_0")],
        [InlineKeyboardButton("📢 Elon berish", callback_data="post_ad")],
        [InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"Assalomu alaykum, {user.first_name}!\n"
        "Bobex Birja botiga xush kelibsiz!",
        reply_markup=reply_markup
    )


# --- 2. Profil ko'rsatish ---
def show_profile(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    user_data = db.get_user(user_id)
    if not user_data:
        query.answer("Foydalanuvchi topilmadi!", show_alert=True)
        return
    
    # To'lov statistikasi
    stats = db.get_payment_stats(user_id)
    
    items = [
        ("👤 Ism", user_data['full_name']),
        ("🆔 ID", str(user_data['user_id'])),
        ("💰 Balans", f"{user_data['balance']} so'm"),
        ("💳 To'lovlar soni", str(stats['total_count'])),
        ("✅ Tasdiqlangan to'lovlar", str(stats['confirmed_count'])),
        ("❌ Rad etilgan to'lovlar", str(stats['rejected_count'])),
    ]
    
    send_formatted_message(update, "Profil ma'lumotlari", items)
    query.answer()


# --- 3. To'lovlar tarixini sahifalash ---
def payment_history(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    
    # Sahifa raqamini olish (callback_data: payment_history_{page})
    data = query.data
    page = 0
    try:
        page = int(data.split('_')[-1])
    except Exception:
        page = 0
    
    limit = 10
    offset = page * limit
    
    payments = db.get_payments(user_id, limit=limit, offset=offset)
    total = db.count_payments(user_id)
    
    if not payments and page > 0:
        # Sahifa bo'sh bo'lsa oldingi sahifani ko'rsatish
        page = 0
        payments = db.get_payments(user_id, limit=limit, offset=0)
    
    status_icons = {'pending': '⏳', 'confirmed': '✅', 'rejected': '❌'}
    payment_lines = []
    for p in payments:
        icon = status_icons.get(p['status'], '')
        payment_lines.append(f"{icon} {p['date']} - {p['amount']} so'm - {p['status']}")
    
    text = f"💳 To'lovlar tarixi (sahifa {page+1}):\n\n" + "\n".join(payment_lines) if payment_lines else "To‘lovlar topilmadi."
    
    # Tugmalar
    buttons = []
    if page > 0:
        buttons.append(InlineKeyboardButton("⬅️ Avvalgi", callback_data=f"payment_history_{page-1}"))
    if (page + 1)*limit < total:
        buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data=f"payment_history_{page+1}"))
    
    reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None
    
    query.edit_message_text(text, reply_markup=reply_markup)
    query.answer()
    # --- 4. Admin panelini ko'rsatish ---
def admin_panel(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("⚠️ Bu buyruq faqat adminlar uchun!")
        return
    
    keyboard = [
    [InlineKeyboardButton("👥 Foydalanuvchilar soni", callback_data="admin_stats_users")],
        [InlineKeyboardButton("💳 To'lovlar statistikasi", callback_data="admin_stats_payments")],
        [InlineKeyboardButton("🎁 Bonuslar statistikasi", callback_data="admin_stats_bonuses")],
        [InlineKeyboardButton("📊 Umumiy statistika", callback_data="admin_stats_general")],
        [InlineKeyboardButton("➕ Bonus berish", callback_data="admin_add_bonus")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text("🛠 *Admin paneli* - Bo‘limlardan birini tanlang:", reply_markup=reply_markup, parse_mode="Markdown")


# --- 5. Admin paneldagi tugmalarni boshqarish ---
def handle_admin_callbacks(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    
    if not is_admin(user_id):
        query.answer("Sizda admin huquqlari yo‘q!", show_alert=True)
        return
    
    if data == "admin_stats_users":
        total_users = db.count_users()
        active_users = db.count_active_users()
        inactive = total_users - active_users
        
        text = (
            f"👥 *Foydalanuvchilar statistikasi*\n\n"
            f"🔢 Jami: {total_users}\n"
            f"🟢 Faol: {active_users}\n"
            f"🔴 Nofaol: {inactive}"
        )
    
    elif data == "admin_stats_payments":
        total_count, total_sum = db.get_total_payments()
        confirmed_count, confirmed_sum = db.get_confirmed_payments()
        pending_count, pending_sum = db.get_pending_payments()
        
        text = (
            f"💳 *To‘lovlar statistikasi*\n\n"
            f"🔢 Jami: {total_count} ta ({total_sum} so'm)\n"
            f"✅ Tasdiqlangan: {confirmed_count} ta ({confirmed_sum} so'm)\n"
            f"⏳ Kutilayotgan: {pending_count} ta ({pending_sum} so'm)"
        )
    
    elif data == "admin_stats_bonuses":
        referral_count, referral_sum = db.get_referral_bonuses()
        total_balance = db.get_total_balance()
        
        text = (
            f"🎁 *Bonuslar statistikasi*\n\n"
            f"👥 Referral bonuslar: {referral_count} ta ({referral_sum} so'm)\n"
            f"💰 Umumiy balanslar: {total_balance} so'm"
        )
    
    elif data == "admin_stats_general":
        users = db.count_users()
        payments = db.count_payments_all()
        total_payments = db.get_confirmed_payments_sum()
        referrals = db.count_referrals()
        
        text = (
            f"📊 *Umumiy statistika*\n\n"
            f"👥 Foydalanuvchilar: {users}\n"
            f"💳 To‘lovlar: {payments} ta\n"
            f"💰 Jami to‘lovlar: {total_payments} so'm\n"
            f"🎁 Referrallar: {referrals}"
        )
    
    elif data == "admin_add_bonus":
        text = (
            "➕ *Bonus berish*\n\n"
            "Bonus berish uchun quyidagi formatda yozing:\n"
            "/addbonus <user_id> <miqdor yoki %> <sabab (ixtiyoriy)>\n\n"
            "Masalan:\n"
            "/addbonus 12345678 10% Referral bonus\n"
            "/addbonus 12345678 50 Admin mukofoti"
        )
    else:
        text = "⚠️ Noma'lum buyruq."
    
    query.edit_message_text(text, parse_mode="Markdown")
    query.answer()


# --- 6. To'lov tasdiqlash uchun admin komandasi ---
def approve_payment(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("⚠️ Bu buyruq faqat adminlar uchun!")
        return
    
    args = context.args
    if len(args) < 2:
        update.message.reply_text("⚠️ To'g'ri format: /approvepayment <payment_id> <tasdiqlash/reject>")
        return
    
    payment_id = args[0]
    action = args[1].lower()
    
    if action not in ['approve', 'reject']:
        update.message.reply_text("⚠️ Tasdiqlash uchun 'approve' yoki 'reject' so'zlarini yozing.")
        return
    
    payment = db.get_payment(payment_id)
    if not payment:
        update.message.reply_text("❌ To'lov topilmadi!")
        return
       def approve_payment(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        update.message.reply_text("⚠️ Bu buyruq faqat adminlar uchun!")
        return

    args = context.args
    if len(args) < 2:
        update.message.reply_text("⚠️ To'g'ri format: /approvepayment <payment_id> <approve/reject>")
        return

    payment_id = args[0]
    action = args[1].lower()

    if action not in ['approve', 'reject']:
        update.message.reply_text("⚠️ Tasdiqlash uchun 'approve' yoki 'reject' so'zlarini yozing.")
        return

    payment = db.get_payment(payment_id)
    if not payment:
        update.message.reply_text("❌ To'lov topilmadi!")
        return

    if action == 'approve':
        db.update_payment_status(payment_id, 'confirmed')
        db.update_balance(payment['user_id'], payment['amount'])
        update.message.reply_text(f"✅ To'lov {payment_id} tasdiqlandi va foydalanuvchi balansiga qo'shildi.")
    else:
        db.update_payment_status(payment_id, 'rejected')
        update.message.reply_text(f"❌ To'lov {payment_id} rad etildi.")
# --- 7. Payment pagination callback ---
def handle_payment_pagination(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    
    if data.startswith("payment_history_"):
        payment_history(update, context)
    else:
        query.answer()


# --- 8. Sahifalash va boshqa callback larni umumiy handleri ---
def callback_query_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    
    # Admin panel callbacks
    if data.startswith("admin_"):
        handle_admin_callbacks(update, context)
        return
    
    # To'lovlar tarixi sahifalari
    if data.startswith("payment_history_"):
        payment_history(update, context)
        return
    
    # Profil ko'rsatish
    if data == "show_profile":
        show_profile(update, context)
        return
    
    # Elon berish bo'limi
    if data == "post_ad":
        # Bu yerda elon berish boshlanishi kerak, keyingi qadamlar yozilishi kerak
        query.answer("Elon berish funksiyasi hozircha tayyor emas.")
        return
    
    # Sozlamalar
    if data == "settings":
        query.answer("Sozlamalar bo‘limi hozircha tayyor emas.")
        return
    
    query.answer("Noma'lum tugma bosildi.")


# --- 9. Botga handlerlarni qo'shish funksiyasi ---
def setup_handlers(dispatcher):
    # /start komandasi
    dispatcher.add_handler(CommandHandler("start", start))
    
    # /adminpanel komandasi
    dispatcher.add_handler(CommandHandler("adminpanel", admin_panel))
    
    # /approvepayment komandasi
    dispatcher.add_handler(CommandHandler("approvepayment", approve_payment))
    
    # CallbackQuery umumiy handleri
    dispatcher.add_handler(
