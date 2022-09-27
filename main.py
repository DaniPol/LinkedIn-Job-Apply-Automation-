from selenium import webdriver
from selenium.webdriver.edge.service import Service
import json



class EasyApplyLinkedin:

    def __init__(self, data):

        self.email = data['email']
        self.password = data['password']
        self.keywords = data['keywords']
        self.location = data['location']
        self.driver = webdriver.Edge(service=Service(data['driver_path']))



if __name__ == "__main__":
    with open('config.json') as config_file:
        data = json.load(config_file)