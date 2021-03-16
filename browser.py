from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchWindowException, RemoteDriverServerException, TimeoutException
from selenium.common.exceptions import NoSuchFrameException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.keys import Keys
from PIL import Image
from io import BytesIO
import os

from selenium.webdriver.support.wait import WebDriverWait


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
        self.driver.get("https://ems.atu.ac.ir/forms/authenticateuser/main.htm")
    
    def captcha_element(self) -> WebElement:
        """ Driver must WAIT for this element to be clickable.
         Despite item is availble, it is not visible for taking a screenshot. """
        self.go_to_login_frame()
        wait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="imgCaptcha"]'))) 
        return self.driver.find_element_by_css_selector('#imgCaptcha')
        
    def go_to_frame(self, *frames:str) -> None:
        """ Some elements are within inner frames and we have to switch to their frames. """
        while True:
            try:
                for frame in frames:
                    self.driver.switch_to.frame(frame)
                break
            except NoSuchFrameException or NoSuchWindowException:
                self.driver.switch_to.default_content()
                continue
    
    def element_screenshot(self, element:WebElement, file_name:str) -> None:
        location = element.location
        size = element.size
        page_screenshot = self.driver.get_screenshot_as_png()
        image = Image.open(BytesIO(page_screenshot))
        
        left = int(location['x'])
        upper = int(location['y'] + size['height'])
        right = int(location['x'] + size['width'])
        lower = int(location['y'] + 2*size['height'])
        
        # left = int(location['x'])
        # upper = int(location['y'])
        # right = int(location['x'] + size['width'])
        # lower = int(location['y'] + size['height'])

        image = image.crop((left, upper, right, lower))
        image.save(f'{file_name}')

    def captcha_screenshot(self):
        self.element_screenshot(self.captcha_element(), 'captcha.png')

    def enter_captcha(self):
        captcha = str(input("Enter Captcha: "))
        captcha_field = self.driver.find_element_by_id('F51701')
        captcha_field.clear()
        captcha_field.click()
        captcha_field.send_keys(captcha)

    def go_to_login_frame(self):
        self.driver.switch_to.default_content()
        self.driver.switch_to_frame('Faci1')
        self.driver.switch_to_frame('Master')
        self.driver.switch_to_frame('Form_Body')

    def enter_username_password(self, username:str, password:str) -> None:
        self.go_to_login_frame()
        user_field = self.driver.find_element_by_xpath('//*[@id="F80351"]')
        password_field = self.driver.find_element_by_xpath('//*[@id="F80401"]')
        self.username = username
        self.password = password
        user_field.clear()
        password_field.clear()
        user_field.send_keys(username)
        password_field.send_keys(password)
    
    def submit_entries(self):
        self.go_to_login_frame()
        self.driver.find_element_by_id('btnLog').click()
    
    def check_error(self):
        error_element= self.driver.find_element_by_id('errtxt')
        error_message = error_element.get_attribute('title')
        if error_message == "لطفا كد امنيتي را به صورت صحيح وارد نماييد":
            print(error_message)
            self.captcha()
        if error_message == "کد1 : شناسه کاربري يا گذرواژه اشتباه است.":
            print(error_message)
            self.enter_username_password('98131314103', 'mo1112')
            self.captcha()

        if error_message == "لطفا صبر کنيد.":
            self.driver.implicitly_wait(1)
            print(error_message)

    def captcha(self):
        self.captcha_screenshot()
        self.enter_captcha()

    def go_to_menu(self):
        # ok_button = self.driver.find_element_by_id('OK')
        # while True:
        #     try:
        #         self.go_to_frame('Faci2', 'Master', 'Form_Body')
        #         break
        #     except:
        #         NoSuchFrameException or ElementNotInteractableException
        #         continue
        self.go_to_frame('Faci2', 'Master', 'Form_Body')
        
        input_field = self.driver.find_element_by_xpath('//*[@id="F20851"]')
        input_field.send_keys(str(input("Enter Menu: ")))
        ok_button = self.driver.find_element_by_id('OK')
        ok_button.click()
        
        
        self.go_to_frame('Faci3', 'Commander')
        
        show_report_button = self.driver.find_element_by_id('IM16_ViewRep')
        show_report_button.click()
     
        self.go_to_frame('Faci3', 'Master', 'Header', 'Form_Body')
        week_table = self.driver.find_element_by_xpath('//*[@id="DIVVarRem_2"]/table')
        self.element_screenshot(week_table, 'week.png')

    def frame_availability(self, frame:str):
        self.driver.switch_to.default_content()
        try:
            self.driver.switch_to.frame(frame)
            return True
        except NoSuchFrameException:
            return False
    
    def go_to_login_error_frame(self):
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame('Faci1')
        self.driver.switch_to.frame('Message')
