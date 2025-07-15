
from telegram.ext import CommandHandler, CallbackQueryHandler
from config import ADMIN_IDS, JOIN_BONUS, REFERRAL_BONUS
from database import Database

db = Database()

def start(update, context):
    user_id = update.effective_user.id
    referrer_id = None
    if context.args:
        referrer_id = int(context.args[0]) if context.args[0].isdigit() else None

    db.add_user(user_id, referrer_id)
    db.update_balance(user_id, JOIN_BONUS)

    if referrer_id:
        db.update_balance(referrer_id, REFERRAL_BONUS)
        context.bot.send_message(referrer_id, f"Yangi foydalanuvchi uchun sizga {REFERRAL_BONUS} so'm bonus!")

    update.message.reply_text("Xush kelibsiz! Hisobingizga 50,000 so'm bonus qo'shildi.")

def setup_handlers(dp):
    dp.add_handler(CommandHandler('start', start))
