from selenium.common.exceptions import NoSuchFrameException, NoSuchWindowException, \
    NoAlertPresentException
from telegram import Update, ForceReply
from telegram.ext import CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, CommandHandler, Updater, CallbackContext
from telegramBot import start_menu_new_user, golestan_menu, TelegramBot, KeyboardButton, ReplyKeyboardMarkup, save_credentials, \
    unis_menu, provinces_menu, uni_generator, uni_json_list
import os
import json
from dotenv import load_dotenv
from db import Mongo

USERNAME, PASSWORD, CAPTCHA = range(3)
Mongo.init()
load_dotenv()
telegram = TelegramBot()

API_KEY = os.environ.get('API_KEY')

class Golestan:
    username = None
    password = None
    captcha = None
    telegram_username = None
# Start Command
def start(update: Update, context: CallbackContext) -> None:
    if Mongo.is_username_in_db(update.message.from_user.username):
        Golestan.telegram_username = update.message.from_user.username
        # keyboard = [[KeyboardButton("/login")], [KeyboardButton("/start")] ]
        keyboard = [['/start'], ['/login']]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text(text="خوش آمدید. بر روی Login بزنید.", reply_markup=markup)
    else:
        start_menu_new_user(update)


def login(update: Update, context: CallbackContext):

    telegram.get_uni_page(update, context)
    try:
        alert = telegram.browser.driver.switch_to_alert()
        alert.accept()

        update.message.reply_text('شناسه کاربری:', reply_markup=ForceReply())
        return USERNAME

    except NoAlertPresentException:
        update.message.reply_text('شناسه کاربری:', reply_markup=ForceReply())
        return USERNAME


def enter_user_password():
    telegram.browser.enter_username_password(Golestan.username, Golestan.password)

def enter_captcha():
    telegram.browser.enter_captcha(Golestan.captcha)

def save_golestan_username(update: Update, context: CallbackContext) -> int:
    Golestan.username = update.message.text
    update.message.reply_text('گذرواژه:', reply_markup=ForceReply())
    return PASSWORD


def save_golestan_password(update: Update, context: CallbackContext) -> int:
    Golestan.password = update.message.text
    telegram.captcha(update, context)
    return CAPTCHA


def save_golestan_captcha(update: Update, context: CallbackContext) -> int:
    Golestan.captcha = update.message.text
    enter_user_password()
    enter_captcha()
    telegram.browser.submit_username_password()
    try:
        telegram.browser.go_to_login_error_frame()
        check_error(update, context)
    except (NoSuchFrameException, NoSuchWindowException, NoSuchFrameException):
        pass
    telegram.browser.go_to_frame('Faci2', 'Master', 'Form_Body')
    if telegram.browser.driver.find_element_by_id('F51851'):
        save_credentials(update, context)
        return ConversationHandler.END


def check_error(update: Update, context: CallbackContext):

    error_element = telegram.browser.driver.find_element_by_id('errtxt')
    error_message = error_element.get_attribute('title')
    if error_message == "لطفا كد امنيتي را به صورت صحيح وارد نماييد":
        context.bot.send_message(update.message.chat_id, error_message)
        return telegram.captcha(update, context)

    if error_message == "کد1 : شناسه کاربري يا گذرواژه اشتباه است.":
        context.bot.send_message(update.message.chat_id, error_message)
        keyboard = [['/login']]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text(text='بر روی Login بزنید.', reply_markup=markup)
        return

    if error_message == "لطفا صبر کنيد.":
        telegram.browser.driver.implicitly_wait(1)
        check_error(update, context)


def cancel(update: Update, context: CallbackContext):
    pass


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # NEW USER
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
                telegram.UNIVERSITY_NAME = uni_name
                telegram.UNIVERSITY_LINK = link
                telegram.TELEGRAM_USERNAME = query.from_user.username
                query.bot.answer_callback_query(query.id, text='نام دانشگاه ذخیره شد.', show_alert=True,
                                                cache_time=0)

                telegram.save_to_db()
                query.bot.send_message(query.message.chat_id, "دوباره استارت کنید")
                return
    # USER MENU
    # if query.data == "login":
    #     query.bot.send_message(text='اطلاعات کاربری خود در سامانه گلستان را وارد کنید.',
    #                            chat_id=query.message.chat_id)
    #     self.username_password(query)

    if query.data == "week_schedule":
        query.bot.send_message(query.message.chat_id, "لطفا صبر کنید.")
        telegram.browser.go_to_menu('78')
        if os.path.isfile('week.png'):
            query.bot.send_photo(chat_id=query.message.chat_id, photo=open('week.png', 'rb'))
        if os.path.isfile('week.txt'):
            with open('week.txt', 'r') as textFile:
                text = textFile.read()
            query.bot.send_message(chat_id=query.message.chat_id, text=text)

    # if query.data == "golestan_menu_back":
    #     start_menu(update, back=True)

    if query.data == "yes":
        Mongo.COL.find_one_and_update(
            {"telegramUsername": Golestan.telegram_username},
            {"$set": {"golestanUsername": Golestan.username,
                      "golestanPassword": Golestan.password}})
        query.bot.answer_callback_query(query.id, text='اطلاعات کاربری شما ذخیره شد.',
                                        show_alert=True)
        golestan_menu(query)

    if query.data == "no":
        golestan_menu(query)

conv_handler = ConversationHandler(allow_reentry=True,
    entry_points=[CommandHandler('login', login)],
    states={
        USERNAME: [MessageHandler(Filters.text, save_golestan_username)],
        PASSWORD: [MessageHandler(Filters.text, save_golestan_password)],
        CAPTCHA: [MessageHandler(Filters.text, save_golestan_captcha)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)



def main() -> None:
    """Run the bot."""
    updater = Updater(API_KEY)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    # updater.dispatcher.add_handler(CommandHandler('help', help_cmd))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
