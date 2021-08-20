import logging
import os
import csv
import json
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, replymarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

load_dotenv()
API_KEY = os.getenv('API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

with open(os.path.realpath('unis.json')) as f:
        uniList = json.load(f)

def start(update: Update, context: CallbackContext) -> None:
    """Sends a message with three inline buttons attached."""
  
    keyboard = [
        [
            InlineKeyboardButton("راهنما", callback_data='guide'),
            InlineKeyboardButton("شروع", callback_data='run'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("به سامانه گلستان خوش آمدید!\nبرای شروع بر روی دکمه شروع کلیک کنید.", \
                                reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    query.answer()

    
    # with open(os.path.realpath('uniNames.csv')) as csvfile:
    #     a = csv.DictReader(csvfile, delimiter=',')
    #     keyboard = [
    #          [InlineKeyboardButton("{}".format(row['uniName']), callback_data="{}".format(row['uniName'][:5]))] for row in a
    #     ]
    
    provinceMenu = [
        [InlineKeyboardButton("{}".format(list(uniList.keys())[i]), \
                                callback_data="{}".format(list(uniList.keys())[i]))] for i in range(len(uniList.keys()))
    ]
    province_reply_markup = InlineKeyboardMarkup(provinceMenu)
    
    if query.data == 'run':
        query.edit_message_text(text="انتخاب استان:", reply_markup=province_reply_markup)
    

    for value in list(uniList.keys()):
        if query.data == value:
            uniMenu = [
            [InlineKeyboardButton("{}".format(list(uniList.get(value)[i])[0]), \
                                    callback_data="{}".format(list(uniList.get(value)[i])[0][8:]))] for i in range(0, len(list(uniList.get(value))))
            ]
            uni_reply_markup = InlineKeyboardMarkup(uniMenu)
            query.edit_message_text("انتخاب دانشگاه:", reply_markup=uni_reply_markup)
            break
        

def help(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("The text/img for the help will be here.")

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_KEY)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()