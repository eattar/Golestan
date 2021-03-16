from selenium.common.exceptions import ElementNotInteractableException, NoSuchElementException, NoSuchFrameException
from browser import Browser

browser = Browser(headless=False)



def login():
    browser.get_url()
    browser.captcha()
    browser.enter_username_password('981313141032', 'mo1112')
    browser.submit_entries()
    while True:
        try:
            browser.go_to_frame('Faci1', 'Message')
            browser.check_error()
            try:
                browser.submit_entries()
            except NoSuchFrameException:
                break
        except ElementNotInteractableException:
            break

def main():

    login()



if __name__ == "__main__":
    main()