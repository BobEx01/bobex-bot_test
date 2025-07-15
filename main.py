
from config import ADMIN_IDS, BOT_TOKEN
from database import Database
from handlers import setup_handlers
from telegram.ext import Updater

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    setup_handlers(dp)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
