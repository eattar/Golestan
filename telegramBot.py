import logging
import os
import json
from typing import ContextManager
import numpy as np
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

API_KEY = os.environ.get('API_KEY')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

start_reply_markup = None
go_back_emoji = "بازگشت ↪"
with open(os.path.realpath('unis.json')) as f:
    uni_json_list = json.load(f)


def uni_generator():
    for key, value in uni_json_list.items():
        for uni in value:
            yield uni


def start(update: Update, context: CallbackContext) -> None:
    if user == new:
        start_menu = [
            [
                InlineKeyboardButton("ورود به سامانه گلستان", callback_data='login'),
                InlineKeyboardButton("تنظیمات", callback_data='setting'),
            ],
        ]

    else:
        start_menu = [
        [
            InlineKeyboardButton("راهنما", callback_data='guide'),
            InlineKeyboardButton("انتخاب دانشگاه", callback_data='choose_uni'),
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
        [InlineKeyboardButton("{}".format(list(uni_json_list.keys())[i]),
                              callback_data="{}".format(list(uni_json_list.keys())[i])) for i in range(len(uni_json_list.keys()))]
    ]

    reshaped_province_menu = reshape_menu(province_menu)
    reshaped_province_menu.append([InlineKeyboardButton(go_back_emoji, callback_data="province_menu_back")])
    province_reply_markup = InlineKeyboardMarkup(reshaped_province_menu)

    # Start Inlinekeyboard -> CHOOSE PROVINCE
    if query.data == 'choose_uni':
        query.edit_message_text(text="انتخاب استان 🇮🇷", reply_markup=province_reply_markup)
    # Choose Province BACK Inlinekeyboard -> Start
    if query.data == 'province_menu_back':
        query.edit_message_text("به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی دگمه شروع بزنید.",
                                reply_markup=start_reply_markup)
    # Province Inlinekeyboard -> CHOOSE UNI
    for city in list(uni_json_list.keys()):
        if query.data == city:
            uni_menu = [
                [InlineKeyboardButton("{}".format(list(uni_json_list.get(city)[i])[0]),
                                      callback_data="{}".format(list(uni_json_list.get(city)[i])[0][:28])) for i in
                 range(0, len(list(uni_json_list.get(city))))]
            ]
            reshaped_uni_menu = reshape_menu(uni_menu)
            reshaped_uni_menu.append([InlineKeyboardButton(go_back_emoji, callback_data="uni_menu_back")])
            uni_reply_markup = InlineKeyboardMarkup(reshaped_uni_menu)
            query.edit_message_text("انتخاب دانشگاه 🏫", reply_markup=uni_reply_markup)
            break

    uni_name_list = uni_generator()
    for uni in uni_name_list:
        for uni_name, link in uni.items():
            if query.data == uni_name[0:28]:
                query.bot.send_message(chat_id=query.message.chat_id, text='نام دانشگاه ذخیره شد.', )
                # Save uni_name to the database
                break

    # context.bot.send_message(chat_id=update.message.chat_id, text='نام کاربری خود در سامانه گلستان را وارد کنید:')
    # print(update.message.text)
    # Save username to the database
    # query.edit_message_text('نام کاربری خود در سامانه گلستان را وارد کنید:')

    # Choose Uni BACK Inlinekeyboard -> Province
    if query.data == 'uni_menu_back':
        query.edit_message_text(text="انتخاب استان 🇮🇷", reply_markup=province_reply_markup)

    if query.data == "login":
        # print 'please wait' 
        # show golestan menus
        golestan_menu = [
            [InlineKeyboardButton("برنامه هفتگی", callback_data='week_schedule')],
        ]
        golestan_reply_markup = InlineKeyboardMarkup(golestan_menu)
        query.edit_message_text("انتخاب", reply_markup=golestan_reply_markup)


def reshape_menu(button_list: list) -> list:
    """Reshapes the InlineKeyboardButton matrix into a two dimensional matrix using Numpy library. """
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
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
