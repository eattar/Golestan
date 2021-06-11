from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, NoSuchFrameException, NoSuchWindowException
from browser import Browser

browser = Browser()



def login():

    browser.get_url()
    browser.captcha()
    browser.enter_username_password('98131314103', 'mo1112')
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

if __name__ == "__main__":
    main()