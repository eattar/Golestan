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

    def __init__(self) -> None:
        self._webdriver_local_path = os.path.realpath('chromedriver')
        self._options = Options()
    
    def webdriver_setup(self, new_path=None, headless=None, start_maximize=None) -> None:
        if new_path:
            self._webdriver_local_path = new_path
        if headless:
            self._options.add_argument('--headless')
        if start_maximize:
            self._options.add_argument("--start-maximized")
       
    def webdriver_run(self):
        return webdriver.Chrome(self._webdriver_local_path, options=self._options)


def main():
    visible_browser = Browser()
    visible_browser.webdriver_setup(headless=False, start_maximize=True)
    browser = visible_browser.webdriver_run()
    browser.get("http://google.com")

if __name__ == "__main__":
    main()
