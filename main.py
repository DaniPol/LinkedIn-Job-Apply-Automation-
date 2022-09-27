from selenium import webdriver
from selenium.webdriver.edge.service import Service
import json
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys



class EasyApplyLinkedin:

    def __init__(self, data):
        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Edge(service=Service(data['driver_path']))

    def login_linkedin(self):
        """This function logs into your personal LinkedIn profile"""

        # go to the LinkedIn login url
        self.driver.get("https://www.linkedin.com/login")

        # introduce email and password and hit enter
        login_email = self.driver.find_element(By.NAME, 'session_key')
        login_email.clear()
        login_email.send_keys(self.email)
        login_pass = self.driver.find_element(By.NAME, 'session_password')
        login_pass.clear()
        login_pass.send_keys(self.password)
        time.sleep(1)
        login_pass.send_keys(Keys.RETURN)


if __name__ == "__main__":
    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.login_linkedin()
