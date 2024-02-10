# from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as webdriver
import time

class BrowserActions:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # change the path to your own user data directory
        options.add_argument("--user-data-dir=C:\\Users\\green\\AppData\\Local\\Google\\Chrome\\User Data")
        options.add_argument("--headless=new")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options, version_main=121)
        self.driver.get("https://web.snapchat.com")
        time.sleep(2)

    def take_screenshot(self, filename):
        time.sleep(1)
        self.driver.save_screenshot(filename)

    def close_browser(self):
        self.driver.close()


    # Snapchat specific

    def open_chat(self, num):
        time.sleep(0.5)
        num = int(num) + 2
        chat = self.driver.find_element("xpath", "//*[@id='root']/div[1]/div[2]/nav/div[1]/div/div/div["+str(num)+"]")
        chat.click()

    def reply_to_chat(self, message):
        time.sleep(0.5)
        input_box = self.driver.find_element("xpath", "//div[@role='textbox']")
        # convert any emojis like U+1F603 to u'\U0001F600
        message = message.encode('utf-16', 'surrogatepass').decode('utf-16')
        input_box.send_keys(message)
        input_box.send_keys(Keys.RETURN)

    def return_to_home(self):
        time.sleep(0.5)
        self.driver.get("https://web.snapchat.com")
