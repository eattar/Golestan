from selenium.common.exceptions import NoAlertPresentException, NoSuchFrameException, NoSuchWindowException, \
    NoSuchElementException
from telegram import Update, ForceReply
from telegram.ext import CallbackQueryHandler, ConversationHandler, MessageHandler, Filters, CommandHandler, \
                          Updater, CallbackContext
from new_user import start_menu_new_user, NewUser, KeyboardButton, ReplyKeyboardMarkup, \
                      unis_menu, provinces_menu, uni_generator, uni_json_list, save_to_db
from registeredUser import golestan_menu, Golestan, login_to_golestan_saved_user, captcha, save_golestan_captcha, \
    get_uni_page
import os
from dotenv import load_dotenv
from db import Mongo
from browser import Browser

Mongo.init()
load_dotenv()
browser = Browser(headless=False)
USERNAME, PASSWORD, CAPTCHA, CAPTCHA_REGISTERED_USER = range(4)
API_KEY = os.environ.get('API_KEY')


# Start Command
def start(update: Update, context: CallbackContext) -> None:
    if Mongo.is_username_in_db(update.message.from_user.username):
        Golestan.telegram_username = update.message.from_user.username
        # keyboard = [[KeyboardButton("/login")], [KeyboardButton("/start")] ]
        keyboard = [['/start'], ['/RUN']]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text(text="خوش آمدید. بر روی RUN/ بزنید.", reply_markup=markup)
    else:
        start_menu_new_user(update)


def login(update: Update, context: CallbackContext):
    doc = Mongo.is_username_in_db(update.message.from_user.username)
    if doc['golestanUsername']:
        login_saved_credentials(update, context, doc)
        return CAPTCHA_REGISTERED_USER

    else:
        get_uni_page(update, context)
        try:
            alert = browser.driver.switch_to_alert()
            alert.accept()

            update.message.reply_text('شناسه کاربری:', reply_markup=ForceReply())
            return USERNAME

        except NoAlertPresentException:
            update.message.reply_text('شناسه کاربری:', reply_markup=ForceReply())
            return USERNAME


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
                NewUser.UNIVERSITY_NAME = uni_name
                NewUser.UNIVERSITY_LINK = link
                NewUser.TELEGRAM_USERNAME = query.from_user.username
                query.bot.answer_callback_query(query.id, text='نام دانشگاه ذخیره شد.', show_alert=True,
                                                cache_time=0)

                save_to_db()
                query.bot.send_message(query.message.chat_id, "دوباره استارت کنید")
                return

    if query.data == "week_schedule":
        query.bot.send_message(query.message.chat_id, "لطفا صبر کنید.")
        browser.go_to_menu('78')
        if os.path.isfile('week.png'):
            query.bot.send_photo(chat_id=query.message.chat_id, photo=open('week.png', 'rb'))
        if os.path.isfile('week.txt'):
            with open('week.txt', 'r') as textFile:
                text = textFile.read()
            query.bot.send_document(chat_id=query.message.chat_id, document=open('noInfo.png', 'rb'))
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


def login_saved_credentials(update: Update, context: CallbackContext, doc):
    Golestan.username = doc['golestanUsername']
    Golestan.password = doc['golestanPassword']
    get_uni_page(update, context)
    captcha(update, context)


def save_golestan_username(update: Update, context: CallbackContext) -> int:
    Golestan.username = update.message.text
    update.message.reply_text('گذرواژه:', reply_markup=ForceReply())
    return PASSWORD


def save_golestan_password(update: Update, context: CallbackContext) -> int:
    Golestan.password = update.message.text
    captcha(update, context)
    return CAPTCHA



def cancel(update: Update, context: CallbackContext):
    pass

# conv_handler_saved_user = ConversationHandler(allow_reentry=True,
#                                    entry_points=[CommandHandler('start', start)],
#                                    states={
#                                             CAPTCHA_REGISTERED_USER: [MessageHandler(Filters.text, login_to_golestan_saved_user)],
#                                             }, fallbacks=[CommandHandler('cancel', cancel)],
#                                    )

conv_handler_new_user = ConversationHandler(allow_reentry=True,
                                   entry_points=[CommandHandler('RUN', login)],
                                   states={
                                            USERNAME: [MessageHandler(Filters.text, save_golestan_username)],
                                            PASSWORD: [MessageHandler(Filters.text, save_golestan_password)],
                                            CAPTCHA: [MessageHandler(Filters.text, save_golestan_captcha)],
                                            CAPTCHA_REGISTERED_USER: [MessageHandler(Filters.text, login_to_golestan_saved_user)]
                                            }, fallbacks=[CommandHandler('cancel', cancel)],
                                   )







def main() -> None:
    """Run the bot."""
    updater = Updater(API_KEY)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    # updater.dispatcher.add_handler(CommandHandler('help', help_cmd))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(conv_handler_new_user)
    # updater.dispatcher.add_handler(conv_handler_saved_user)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
