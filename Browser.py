from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchFrameException, NoSuchElementException, StaleElementReferenceException
from PIL import Image
from io import BytesIO
from time import sleep
import os
import sys


class Browser:
    """ this class makes a browser from Selenium framework. """

    def __init__(self, path=None, headless:bool=True, start_maximized:bool=True) -> None:
        
        if path:
            self._webdriver_local_path = path
        else:
            self._webdriver_local_path = os.path.realpath('chromedriver')
        
        self._options = Options()
        if headless:
            self._options.add_argument('--headless')
        if start_maximized:
            self._options.add_argument("--start-maximized")
        
        self.driver = webdriver.Chrome(self._webdriver_local_path, options=self._options)

    def get_url(self):
        self.driver.get("https://golestan.du.ac.ir/forms/authenticateuser/main.htm")
    
    def captcha_element(self) -> WebElement:
        """ Driver must WAIT for this element to be clickable.
         Despite item is availble, it is not visible for taking a screenshot. """

        wait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="imgCaptcha"]'))) 
        return self.driver.find_element_by_css_selector('#imgCaptcha')
        
    def go_to_captcha_frame(self) -> None:
        """ Some elements are within inner frames and we have to switch to their frames. """
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('Faci1')
        self.driver.switch_to.frame('Master')
        self.driver.switch_to.frame('Form_Body')       
        
    def element_screenshot(self, element:WebElement, file_name:str) -> None:
        location = element.location
        size = element.size
        page_screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(BytesIO(page_screenshot))
        
        left = int(location['x'])
        upper = int(location['y'] + size['height'])
        right = int(location['x'] + size['width'])
        lower = int(location['y'] + 2*size['height'])

        image = image.crop((left, upper, right, lower))
        image.save(f'{file_name}')

    def captcha_screenshot(self):
        self.element_screenshot(self.captcha_element(), 'captcha.png')

    def enter_login_captcha(self):
        captcha = str(input("Enter: "))
        captcha_field = self.driver.find_element_by_id('F51701')
        captcha_field.clear()
        captcha_field.click()
        captcha_field.send_keys(captcha)

    def enter_username_password(self):
        user_field = self.driver.find_element_by_xpath('//*[@id="F80351"]')
        password_field = self.driver.find_element_by_xpath('//*[@id="F80401"]')
        username = '94432027'
        password = 'a123456@'
        user_field.clear()
        password_field.clear()
        user_field.send_keys(username)
        password_field.send_keys(password)
    
    def submit_entries(self):
        self.driver.find_element_by_xpath('//*[@id="btnLog"]').click()

    def go_to_menu(self):
        wait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'F20851')))
        input_field = self.driver.find_element_by_xpath('//*[@id="F20851"]')
        input_field.send_keys(str(input("Enter Menu: ")))
        self.driver.find_element_by_xpath('//*[@id="OK"]').click()


b = Browser(headless=False)
b.get_url()
b.go_to_captcha_frame()
b.captcha_screenshot()
b.enter_login_captcha()
b.enter_username_password()
b.submit_entries()
b.go_to_menu()