from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, NoSuchFrameException, NoSuchWindowException
from browser import Browser

browser = Browser()



def login():

    browser.get_url()
    browser.captcha()
    browser.enter_username_password('', '')
    while True:
        try:
            browser.submit_entries()
            browser.go_to_login_error_frame()
            browser.check_error()
        except(NoSuchFrameException, NoSuchWindowException, ElementNotInteractableException):
            break


def main():
    
    login()
    browser.go_to_menu()

if __name__ == "__main__":
    main()