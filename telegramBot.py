import logging
import os
import json
import numpy as np
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

load_dotenv()
API_KEY = os.getenv('API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

start_reply_markup = None
go_back_emoji = "بازگشت ↪"
with open(os.path.realpath('unis.json')) as f:
    uniList = json.load(f)


def start(update: Update, context: CallbackContext) -> None:
    start_menu = [
        [
            InlineKeyboardButton("راهنما", callback_data='guide'),
            InlineKeyboardButton("شروع", callback_data='run'),
        ],
    ]
    global start_reply_markup
    start_reply_markup = InlineKeyboardMarkup(start_menu)
    update.message.reply_text("به سامانه گلستان خوش آمدید!\nبرای شروع بر روی دکمه شروع کلیک کنید.",
                              reply_markup=start_reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    query.answer()

    province_menu = [
        [InlineKeyboardButton("{}".format(list(uniList.keys())[i]),
                              callback_data="{}".format(list(uniList.keys())[i])) for i in range(len(uniList.keys()))]
    ]
    reshaped_province_menu = reshape_menu(province_menu)
    reshaped_province_menu.append([InlineKeyboardButton(go_back_emoji, callback_data="province_menu_back")])
    province_reply_markup = InlineKeyboardMarkup(reshaped_province_menu)

    if query.data == 'run':
        query.edit_message_text(text="انتخاب استان 🇮🇷", reply_markup=province_reply_markup)
    if query.data == 'province_menu_back':
        # update.message.message_id
        query.edit_message_text("به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی دگمه شروع بزنید.",
                                reply_markup=start_reply_markup)
    if query.data == 'uni_menu_back':
        query.edit_message_text(text="انتخاب استان 🇮🇷", reply_markup=province_reply_markup)

    for value in list(uniList.keys()):
        if query.data == value:
            uni_menu = [
                [InlineKeyboardButton("{}".format(list(uniList.get(value)[i])[0]),
                                      callback_data="{}".format(list(uniList.get(value)[i])[0][8:28])) for i in
                 range(0, len(list(uniList.get(value))))]
            ]
            reshaped_uni_menu = reshape_menu(uni_menu)
            reshaped_uni_menu.append([InlineKeyboardButton(go_back_emoji, callback_data="uni_menu_back")])
            uni_reply_markup = InlineKeyboardMarkup(reshaped_uni_menu)
            query.edit_message_text("انتخاب دانشگاه 🏫", reply_markup=uni_reply_markup)
            break


def reshape_menu(button_list: list) -> list:
    if len(button_list[0]) < 3:
        return button_list
    elif len(button_list[0]) % 2 != 0:
        button_list[0].append(InlineKeyboardButton("", callback_data="void"))
    button_list = np.reshape(button_list[0], (len(button_list[0]) // 2, 2)).tolist()
    return button_list


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("The text/img for the help will be here.")


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(API_KEY)

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
