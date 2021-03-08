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


class Golestan:
    """ this class makes a browser from Selenium framework. """

    def __init__(self):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument("--start-maximized")
        opts.add_argument("--ignore-certificate-errors")
        opts.add_argument("disable-infobars")
        opts.add_argument("--disable-extensions")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        path = os.path.realpath('chromedriver')
        self.driver = webdriver.Chrome(path, options=opts)
