import logging
import os
import json
from enum import Enum, auto
from db import Mongo
import numpy as np
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext,
                          CallbackQueryHandler)

from browser import Browser, EC, wait, By
from browser import NoSuchFrameException, NoSuchWindowException, ElementNotInteractableException, NoSuchElementException

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

GO_BACK_EMOJI = "بازگشت ↪"
with open(os.path.realpath('unis.json')) as f:
    uni_json_list = json.load(f)


def uni_generator():
    for key, value in uni_json_list.items():
        for uni in value:
            yield uni


# Commands



def help_cmd(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("The text/img for the help will be here.")


def start_menu_new_user(update: Update, back=None):
    start_menu_ = [
        [
            InlineKeyboardButton("راهنما", callback_data='guide'),
            InlineKeyboardButton("انتخاب استان", callback_data='choose_province_btn'),
        ],
    ]

    start_menu_new_user_markup = InlineKeyboardMarkup(start_menu_)
    if back:
        query = update.callback_query
        query.edit_message_text(text="به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی گزینه مورد نظر کلیک کنید.",
                                reply_markup=start_menu_new_user_markup)
        return
    else:
        update.message.reply_text(text="به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی گزینه مورد نظر کلیک کنید.",
                                  reply_markup=start_menu_new_user_markup)



    # if back:
    #     query = update.callback_query
    #     query.edit_message_text(text="به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی گزینه مورد نظر کلیک کنید.",
    #                             reply_markup=start_menu_markup)
    # else:
    #     update.message.reply_text(text="به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی گزینه مورد نظر کلیک کنید.",
    #                               reply_markup=start_menu_markup)


def provinces_menu(query, update: Update = None, back=None):
    province_menu = [
        [InlineKeyboardButton("{}".format(list(uni_json_list.keys())[i]),
                              callback_data="{}".format(list(uni_json_list.keys())[i])) for i in
         range(len(uni_json_list.keys()))]
    ]

    reshaped_province_menu = reshape_menu(province_menu, 2)
    reshaped_province_menu.append([InlineKeyboardButton(GO_BACK_EMOJI, callback_data="province_menu_back_btn")])
    province_reply_markup = InlineKeyboardMarkup(reshaped_province_menu)

    if back:
        start_menu_new_user(update, back=True)
        return
    query.edit_message_text(text="انتخاب استان 🇮🇷", reply_markup=province_reply_markup)


def unis_menu(query, city=None, back=None):
    if back:
        provinces_menu(query)
        return

    if city:
        uni_menu = [
            [InlineKeyboardButton("{}".format(list(uni_json_list.get(city)[i])[0]),
                                  callback_data="{}".format(list(uni_json_list.get(city)[i])[0][:28])) for i in
             range(0, len(list(uni_json_list.get(city))))]
        ]
        reshaped_uni_menu = reshape_menu(uni_menu, 1)
        reshaped_uni_menu.append([InlineKeyboardButton(GO_BACK_EMOJI, callback_data="uni_menu_back_btn")])
        uni_menu_markup = InlineKeyboardMarkup(reshaped_uni_menu)
        query.edit_message_text("انتخاب دانشگاه 🏫", reply_markup=uni_menu_markup)


def golestan_menu(query):
    golestan_menu_ = [
        [InlineKeyboardButton("برنامه هفتگی", callback_data='week_schedule')],
        [InlineKeyboardButton(GO_BACK_EMOJI, callback_data='golestan_menu_back')],
    ]
    golestan_reply_markup = InlineKeyboardMarkup(golestan_menu_)
    query.edit_message_text(text='انتخاب کنید', reply_markup=golestan_reply_markup)


def reshape_menu(button_list: list, column: int):
    """Reshapes the InlineKeyboardButton matrix into an n dimensional matrix using Numpy library. """
    if len(button_list[0]) < 3:
        return button_list
    elif len(button_list[0]) % 2 != 0:
        button_list[0].append(InlineKeyboardButton("", callback_data="void"))
    button_list = np.reshape(button_list[0], (len(button_list[0]) // column, column)).tolist()
    return button_list


class TelegramBot:

    TELEGRAM_USERNAME = ""
    UNIVERSITY_LINK = ""
    UNIVERSITY_NAME = ""
    browser = Browser()

    def save_to_db(self):
        Mongo.COL.insert_one({"telegramUsername": "{}".format(self.TELEGRAM_USERNAME),
                              "uniName": "{}".format(self.UNIVERSITY_NAME),
                              "uniLink": "{}".format(self.UNIVERSITY_LINK), "golestanUsername": "",
                              "golestanPassword": ""})

    def login_to_golestan(self, update: Update, context: CallbackContext):

        self.get_uni_page(update, context)
        self.captcha(update, context)

    def get_uni_page(self, update: Update, context: CallbackContext):

        context.bot.send_message(chat_id=update.message.chat_id, text="لطفا صبر کنید...")
        username = update.message.from_user.username
        row = Mongo.COL.find_one({"telegramUsername": username})
        self.browser.get_url(row['uniLink'])

    def captcha(self, update: Update, context: CallbackContext):

        self.browser.captcha_screenshot()
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('captcha.png', 'rb'))
        context.bot.send_message(update.message.chat_id, text="کپچا را وارد کنید.")
        context.bot.send_message(update.message.chat_id, text="کپچا:", reply_markup=ForceReply())





    # def submit(self, update: Update, context: CallbackContext):
    #     self.enter_user_password()
    #     self.enter_captcha()
    #     while True:
    #         try:
    #             self.browser.submit_username_password()
    #             self.browser.go_to_login_error_frame()
    #             self.check_error(update, context)
    #         except(NoSuchFrameException, NoSuchWindowException, ElementNotInteractableException):
    #             break
    #     try:
    #         wait(self.browser.driver, 2).until(EC.visibility_of_element_located((By.XPATH,
    #                                            "//span[@style='cursor:hand;color:blue']")))
    #
    #         Mongo.COL.find_one_and_update(
    #             {"telegramUsername": update.message.from_user.username},
    #             {"$set": {"golestanUsername": self.`GOLESTAN_USERNAME`,
    #                       "golestanPassword": self.GOLESTAN_PASSWORD}})
    #         print('saved')
    #
    #     except NoSuchElementException:
    #         print("didn't work")
    #
    #     context.bot.send_message(chat_id=update.message.chat_id, text='گزینه مورد نظر را انتخاب کنید:',
    #                              reply_markup=golestan_menu())


def save_credentials(update: Update, context: CallbackContext):
    kb = [
        [InlineKeyboardButton("بله", callback_data='yes')],
        [InlineKeyboardButton("خیر", callback_data='no')],
    ]
    kb_markup = InlineKeyboardMarkup(kb)
    context.bot.send_message(chat_id=update.message.chat_id, text="آيا مایلید اطلاعات کاربری شما برای استفاده آتی ذخیره شود؟",
                             reply_markup=kb_markup)








class Menu(Enum):
    WEEK_SCHEDULE = 78
    WEEK_SCHEDULE_ENROLLMENT = 88
    FINAL_EXAMS = 428

