from os import path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from PIL import Image
from io import BytesIO
from selenium.common.exceptions import NoSuchFrameException, NoSuchElementException, StaleElementReferenceException
from time import sleep
import os


class Browser:
    """ this class makes a browser from Selenium framework. """

    def __init__(self):
        self.webdriver_path = os.path.realpath('chromedriver')
        self.options = Options()

    def setup_browser(self, new_path=None, headless=None, start_maximize=None):

        if new_path:
            self.webdriver_path = new_path

        if headless:
            self.options.add_argument('--headless')

        if start_maximize:
            self.options.add_argument("--start-maximized")

    def run(self):
        webdriver.Chrome(self.webdriver_path, options=self.options)


def main():
    visible_browser = Browser()
    visible_browser.setup_browser(headless=True)
    print(visible_browser.webdriver_path)
    visible_browser.run()


if __name__ == "__main__":
    main()