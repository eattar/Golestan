from selenium.common.exceptions import NoAlertPresentException
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, Filters
from db import Mongo
from browser import NoSuchFrameException, NoSuchWindowException, NoSuchElementException
from browser import Browser, EC, By, wait

browser = Browser(headless=False)


class Golestan:
    username = None
    password = None
    captcha = None
    telegram_username = None


def golestan_menu(query):
    golestan_menu_ = [
        [InlineKeyboardButton("برنامه هفتگی", callback_data='week_schedule')],
    ]
    golestan_reply_markup = InlineKeyboardMarkup(golestan_menu_)
    query.edit_message_text(text='انتخاب کنید', reply_markup=golestan_reply_markup)


def golestan_menu_saved_user(update: Update, context: CallbackContext):
    golestan_menu_ = [
        [InlineKeyboardButton("برنامه هفتگی", callback_data='week_schedule')],
    ]
    golestan_reply_markup = InlineKeyboardMarkup(golestan_menu_)
    context.bot.send_message(update.message.chat_id, text='انتخاب کنید', reply_markup=golestan_reply_markup)


def check_error(update: Update, context: CallbackContext):

    error_element = browser.driver.find_element_by_id('errtxt')
    error_message = error_element.get_attribute('title')
    if error_message == "لطفا كد امنيتي را به صورت صحيح وارد نماييد":
        context.bot.send_message(update.message.chat_id, error_message)
        return captcha(update, context)

    if error_message == "کد1 : شناسه کاربري يا گذرواژه اشتباه است.":
        context.bot.send_message(update.message.chat_id, error_message)
        keyboard = [['/login']]
        markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
        update.message.reply_text(text='بر روی Login بزنید.', reply_markup=markup)
        return

    if error_message == "لطفا صبر کنيد.":
        browser.driver.implicitly_wait(1)
        check_error(update, context)


def enter_user_and_password():
    browser.enter_username_password(Golestan.username, Golestan.password)


def enter_captcha():
    browser.enter_captcha(Golestan.captcha)


def get_uni_page(update: Update, context: CallbackContext):

    context.bot.send_message(chat_id=update.message.chat_id, text="لطفا صبر کنید...")
    username = update.message.from_user.username
    row = Mongo.COL.find_one({"telegramUsername": username})
    browser.get_url(row['uniLink'])


def captcha(update: Update, context: CallbackContext):

    browser.captcha_screenshot()
    context.bot.send_photo(chat_id=update.message.chat_id, photo=open('captcha.png', 'rb'))
    context.bot.send_message(update.message.chat_id, text="کپچا را وارد کنید.")
    context.bot.send_message(update.message.chat_id, text="کپچا:", reply_markup=ForceReply())


def save_credentials_menu(update: Update, context: CallbackContext):
    kb = [
        [InlineKeyboardButton("بله", callback_data='yes')],
        [InlineKeyboardButton("خیر", callback_data='no')],
    ]
    kb_markup = InlineKeyboardMarkup(kb)
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="آيا مایلید اطلاعات کاربری شما برای استفاده آتی ذخیره شود؟",
                             reply_markup=kb_markup)

def save_golestan_captcha(update: Update, context: CallbackContext) -> int:
    Golestan.captcha = update.message.text
    enter_user_and_password()
    enter_captcha()
    browser.submit_username_password()
    try:
        browser.go_to_login_error_frame()
        check_error(update, context)
    except (NoSuchFrameException, NoSuchWindowException, NoSuchElementException):
        pass
    browser.go_to_frame('Faci2', 'Master', 'Form_Body')
    try:
        wait(browser.driver, 1).until(EC.visibility_of_element_located((By.ID, 'F51851')))
    except NoSuchElementException:
        browser.driver.implicitly_wait(1)
    finally:
        save_credentials_menu(update, context)
        return ConversationHandler.END



def login_to_golestan_saved_user(update: Update, context: CallbackContext):
    Golestan.captcha = update.message.text
    browser.enter_username_password(Golestan.username, Golestan.password)
    enter_captcha()
    browser.submit_username_password()
    try:
        browser.go_to_login_error_frame()
        check_error(update, context)
    except (NoSuchFrameException, NoSuchWindowException, NoSuchElementException):
        pass
    golestan_menu_saved_user(update, context)
    return ConversationHandler.END




