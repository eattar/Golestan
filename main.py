from selenium.common.exceptions import ElementNotInteractableException, NoSuchFrameException, NoSuchWindowException
from browser import Browser
from browser import GOLESTAN_PASSWORD, GOLESTAN_USERNAME
import os

browser = Browser(headless=False)

def login():

    browser.get_url()
    browser.captcha()
    browser.enter_username_password(GOLESTAN_USERNAME, GOLESTAN_PASSWORD)
    while True:
        try:
            browser.submit_username_password()
            browser.go_to_login_error_frame()
            browser.check_error()
        except(NoSuchFrameException, NoSuchWindowException, ElementNotInteractableException):
            break

def main():
    
    login()
    browser.userInputMenuNumber()
    browser.go_to_menu()
    browser.driver.quit()

if __name__ == "__main__":
    main()