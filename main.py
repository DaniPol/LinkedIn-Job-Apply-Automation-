from selenium import webdriver
from selenium.webdriver.edge.service import Service
import json
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


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
        time.sleep(3)
        login_pass.send_keys(Keys.RETURN)

    def load_jobs_page(self):
        """This function goes to the 'Jobs' section a looks for all the jobs that matches the keywords and location"""

        # go to Jobs
        jobs_link = self.driver.find_element(By.LINK_TEXT, 'Jobs')
        jobs_link.click()

    def enter_keywords_and_location(self):
        # search based on keywords and location and hit enter
        search_keywords = self.driver.find_element(By.XPATH, "//input[starts-with(@id,'jobs-search-box-keyword')]")
        search_keywords.clear()
        search_keywords.send_keys(self.keywords)
        time.sleep(3)
        search_location = self.driver.find_element(By.XPATH, "//input[starts-with(@id,'jobs-search-box-location')]")
        search_location.clear()
        search_location.send_keys(self.location)
        time.sleep(3)
        search_location.send_keys(Keys.RETURN)

    def filter_jobs(self):
        """This function filters all the job results by 'Easy Apply'"""

        all_filters_button = self.driver.find_element(By.XPATH,
                                                      '//*[@id="search-reusables__filters-bar"]/div/div/button')
        all_filters_button.click()
        time.sleep(3)

        easy_apply_button = self.driver.find_element(By.CLASS_NAME, 'jobs-search-advanced-filters__binary-toggle')
        easy_apply_button.click()
        time.sleep(3)

        intership_button = self.driver.find_element(By.XPATH, "//label[@for='advanced-filter-experience-1']")
        intership_button.click()
        time.sleep(3)

        entry_level_button = self.driver.find_element(By.XPATH, "//label[@for='advanced-filter-experience-2']")
        entry_level_button.click()
        time.sleep(3)

        apply_filter_button = self.driver.find_element(By.XPATH, "//*[@class='justify-flex-end display-flex mv3 "
                                                                 "mh2']/button[2]")
        apply_filter_button.click()

    def find_job_offers(self):
        """This function finds all the offers through all the pages result of the search and filter"""

        # find the total amount of results (if the results are above 24-more than one page-, we will scroll through
        # all available pages)
        total_results = self.driver.find_element(By.CLASS_NAME, "display-flex.t-12.t-black--light.t-normal")
        total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))
        time.sleep(3)

        num_of_pages = 1
        flag = 1
        page_number = 2

        while num_of_pages > 0:
            results = self.driver.find_elements(By.CLASS_NAME,
                                                "ember-view.jobs-search-results__list-item.occludable-update.p0"
                                                ".relative.scaffold-layout__list-item")

            if flag:
                num_of_pages = total_results_int // len(results)
                flag = 0

            for result in results:
                hover = ActionChains(self.driver).move_to_element(result)
                hover.perform()
                self.submit_apply(result)

            num_of_pages -= 1
            apply_filter_button = self.driver.find_element(By.XPATH, f"//*[@aria-label='Page {page_number}']")
            apply_filter_button.click()
            page_number += 1

    def submit_apply(self, job_add):
        """This function submits the application for the job add found"""

        print('You are applying to the position of: ', job_add.text)
        job_add.click()
        time.sleep(3)

        # click on the easy apply button, skip if already applied to the position
        try:
            in_apply = self.driver.find_element(By.XPATH, "//*[@class='jobs-apply-button--top-card']/button")
            in_apply.click()
        except NoSuchElementException:
            print('You already applied to this job, go to next...')
            pass
        time.sleep(3)

        # try to submit if submit application is available...
        try:
            submit = self.driver.find_element(By.XPATH, "//button[@aria-label='Submit application']")
            submit.send_keys(Keys.RETURN)
            print("submit pressed")
            time.sleep(3)

            dismiss = self.driver.find_element(By.XPATH, "//button[@aria-label='Dismiss']")
            dismiss.click()
            print("Dismiss pressed")
            time.sleep(3)
        # ... if not available, discard application and go to next
        except NoSuchElementException:
            print('Not direct application, going to next...')
            try:
                discard = self.driver.find_element(By.XPATH, "//*[@class='artdeco-modal__dismiss artdeco-button "
                                                             "artdeco-button--circle artdeco-button--muted "
                                                             "artdeco-button--2 artdeco-button--tertiary ember-view']")
                discard.send_keys(Keys.RETURN)
                time.sleep(3)
                discard_confirm = self.driver.find_element(By.XPATH, "//button[@data-test-dialog-secondary-btn]")
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(3)
            except NoSuchElementException:
                pass

        time.sleep(1)


if __name__ == "__main__":
    with open('config.json') as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)

    bot.login_linkedin()
    time.sleep(3)

    bot.load_jobs_page()
    time.sleep(3)

    bot.enter_keywords_and_location()
    time.sleep(3)

    bot.filter_jobs()
    time.sleep(3)

    bot.find_job_offers()
