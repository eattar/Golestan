import logging
import os
import json
import numpy as np
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, ForceReply
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext, MessageHandler, Filters
import pymongo
from browser import Browser, EC, wait, By
from browser import NoSuchFrameException, NoSuchWindowException, ElementNotInteractableException, NoSuchElementException
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY = os.environ.get('API_KEY')

client = pymongo.MongoClient('localhost', 27017)
db = client['golestandb']
col = db['user']

counter = 0
go_back_emoji = "بازگشت ↪"

with open(os.path.realpath('unis.json')) as f:
    uni_json_list = json.load(f)


def uni_generator():
    for key, value in uni_json_list.items():
        for uni in value:
            yield uni


def registered_user(update: Update):
    username = update.message.from_user.username
    username_query = dict(telegramUsername=f'{username}')
    if col.find_one(username_query):
        return True


def help_command(update: Update, context: CallbackContext) -> None:
    """Displays info on how to use the bot."""
    update.message.reply_text("The text/img for the help will be here.")


def golestan_menu():

    golestan_menu_ = [
        [InlineKeyboardButton("برنامه هفتگی", callback_data='week_schedule')],
        [InlineKeyboardButton(go_back_emoji, callback_data='golestan_menu_back')],
    ]
    golestan_reply_markup = InlineKeyboardMarkup(golestan_menu_)
    return golestan_reply_markup


def start_menu(update: Update, back=None):

    start_menu_ = [
        [
            InlineKeyboardButton("تنظیمات", callback_data='setting'),
            InlineKeyboardButton("ورود به سامانه گلستان", callback_data='login'),
        ],
    ]

    start_menu_markup = InlineKeyboardMarkup(start_menu_)
    if back:
        query = update.callback_query
        query.edit_message_text(text="به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی گزینه مورد نظر کلیک کنید.",
                                reply_markup=start_menu_markup)
        return
    else:
        update.message.reply_text(text="به سامانه گلستان خوش آمدید!\nبرای ادامه بر روی گزینه مورد نظر کلیک کنید.",
                                  reply_markup=start_menu_markup)


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


def provinces_menu(query, update: Update = None, back=None):

    province_menu = [
        [InlineKeyboardButton("{}".format(list(uni_json_list.keys())[i]),
                              callback_data="{}".format(list(uni_json_list.keys())[i])) for i in
         range(len(uni_json_list.keys()))]
    ]

    reshaped_province_menu = reshape_menu(province_menu, 2)
    reshaped_province_menu.append([InlineKeyboardButton(go_back_emoji, callback_data="province_menu_back_btn")])
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
        reshaped_uni_menu.append([InlineKeyboardButton(go_back_emoji, callback_data="uni_menu_back_btn")])
        uni_menu_markup = InlineKeyboardMarkup(reshaped_uni_menu)
        query.edit_message_text("انتخاب دانشگاه 🏫", reply_markup=uni_menu_markup)


def start(update: Update, context: CallbackContext) -> None:

    if registered_user(update):
        start_menu(update)
    else:
        start_menu_new_user(update)


def reshape_menu(button_list: list, column: int):
    """Reshapes the InlineKeyboardButton matrix into an n dimensional matrix using Numpy library. """
    if len(button_list[0]) < 3:
        return button_list
    elif len(button_list[0]) % 2 != 0:
        button_list[0].append(InlineKeyboardButton("", callback_data="void"))
    button_list = np.reshape(button_list[0], (len(button_list[0]) // column, column)).tolist()
    return button_list


# def login():
#
#     Browser.get_url(UNIVERSITY_LINK)
#     Browser.captcha()
#     Browser.enter_username_password(GOLESTAN_USERNAME, GOLESTAN_PASSWORD)
#     while True:
#         try:
#             Browser.submit_username_password()
#             Browser.go_to_login_error_frame()
#             Browser.check_error()
#         except(NoSuchFrameException, NoSuchWindowException, ElementNotInteractableException):
#             break

class TelegramBot:
    TELEGRAM_USERNAME = ""
    GOLESTAN_USERNAME = ""
    GOLESTAN_PASSWORD = ""
    UNIVERSITY_LINK = ""
    UNIVERSITY_NAME = ""
    CAPTCHA = ""
    counter = 0
    browser = Browser()

    def button(self, update: Update, context: CallbackContext) -> None:
        """Parses the CallbackQuery and updates the message text."""
        query = update.callback_query
        # Start Inlinekeyboard -> CHOOSE PROVINCE
        if query.data == 'choose_province_btn':
            provinces_menu(query)
        # Choose Province BACK Inlinekeyboard -> Start
        if query.data == 'province_menu_back_btn':
            start_menu_new_user(update, back=True)
        # Province Inlinekeyboard -> CHOOSE UNI
        for city in list(uni_json_list.keys()):
            if query.data == city:
                return unis_menu(query, city)
        # Choose Uni BACK Inlinekeyboard -> Province
        if query.data == 'uni_menu_back_btn':
            unis_menu(query, back=True)
        # Select Uni
        uni_name_list = uni_generator()
        for uni in uni_name_list:
            for uni_name, link in uni.items():
                if query.data == uni_name[0:28]:
                    self.UNIVERSITY_NAME = uni_name
                    self.UNIVERSITY_LINK = link
                    self.TELEGRAM_USERNAME = query.from_user.username
                    query.bot.answer_callback_query(query.id, text='نام دانشگاه ذخیره شد.', show_alert=True,
                                                    cache_time=0)

                    self.save_to_db()
                    return start_menu(update, back=True)

        if query.data == "login":
            query.bot.send_message(text='اطلاعات کاربری خود در سامانه گلستان را وارد کنید.',
                                   chat_id=query.message.chat_id)
            query.bot.send_message(query.message.chat_id, 'شناسه کاربری:', reply_markup=ForceReply())

        if query.data == "week_schedule":
            query.bot.send_message(query.message.chat_id, "لطفا صبر کنید.")
            self.browser.go_to_menu('78')
            if os.path.isfile('week.png'):
                query.bot.send_photo(chat_id=query.message.chat_id, photo=open('week.png', 'rb'))
            if os.path.isfile('week.txt'):
                with open('week.txt', 'r') as textFile:
                    text = textFile.read()
                query.bot.send_message(chat_id=query.message.chat_id, text=text)

        if query.data == "golestan_menu_back":
            start_menu(update, back=True)

    def save_to_db(self):
        col.insert_one(dict(telegramUsername=f'{self.TELEGRAM_USERNAME}', uniName=f'{self.UNIVERSITY_NAME}',
                            uniLink=f'{self.UNIVERSITY_LINK}', golestanUsername=f'{self.GOLESTAN_USERNAME}',
                            golestanPassword=f'{self.GOLESTAN_PASSWORD}'))

    def login(self, update: Update, context: CallbackContext):

        context.bot.send_message(chat_id=update.message.chat_id, text="لطفا صبر کنید...")
        username = update.message.from_user.username
        row = col.find_one({"telegramUsername": username})
        self.browser.get_url(row['uniLink'])
        self.browser.captcha_screenshot()
        context.bot.send_photo(chat_id=update.message.chat_id, photo=open('captcha.png', 'rb'))
        context.bot.send_message(update.message.chat_id, text="کپچا را وارد کنید.")
        context.bot.send_message(update.message.chat_id, text="کپچا:", reply_markup=ForceReply())

    def submit(self, update: Update, context: CallbackContext):
        self.browser.enter_captcha(self.CAPTCHA)
        self.browser.enter_username_password(self.GOLESTAN_USERNAME, self.GOLESTAN_PASSWORD)
        while True:
            try:
                self.browser.submit_username_password()
                self.browser.go_to_login_error_frame()
                self.browser.check_error()
            except(NoSuchFrameException, NoSuchWindowException, ElementNotInteractableException):
                break
        try:
            wait(self.browser.driver, 2).until(EC.visibility_of_element_located((By.XPATH,
                                                "//span[@style='cursor:hand;color:blue']")))
            col.find_one_and_update(
                {"telegramUsername": update.message.from_user.username},
                {"$set": {"golestanUsername": self.GOLESTAN_USERNAME,
                          "golestanPassword": self.GOLESTAN_PASSWORD}})
            print('saved')

        except NoSuchElementException:
            print('didnt work')

        context.bot.send_message(chat_id=update.message.chat_id, text='گزینه مورد نظر را انتخاب کنید:',
                                 reply_markup=golestan_menu())

    def input_golestan_credentials(self, update: Update, context: CallbackContext):
        if self.counter == 0:
            self.GOLESTAN_USERNAME = update.message.text
            context.bot.send_message(update.message.chat_id, 'گذرواژه:', reply_markup=ForceReply())
            self.counter += 1

        elif self.counter == 1:
            self.GOLESTAN_PASSWORD = update.message.text
            self.counter += 1
            self.login(update, context)

        elif self.counter == 2:
            self.CAPTCHA = update.message.text
            self.counter += 1
            self.submit(update, context)


def main() -> None:
    """Run the bot."""
    telegram = TelegramBot()
    updater = Updater(API_KEY)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_command))
    updater.dispatcher.add_handler(CallbackQueryHandler(telegram.button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, telegram.input_golestan_credentials))

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
