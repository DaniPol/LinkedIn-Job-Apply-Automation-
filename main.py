import json
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import Select


class EasyApplyLinkedin:

    def __init__(self, data):
        """Initialize the EasyApplyLinkedin instance with user and LinkedIn configuration and data"""

        # User configuration
        self.email = data['user_conf']['email']
        self.password = data['user_conf']['password']
        self.keywords = data['user_conf']['keywords']
        self.location = data['user_conf']['location']
        self.driver = webdriver.Edge(service=Service(data['user_conf']['driver_path']))
        self.logs = data['user_conf']['logs']

        # LinkedIn configuration
        self.questions_answers = data['linkedin_question_answer']
        self.filters = data['linkedin_filters']

        if self.logs:
            print("EasyApplyLinkedin was successfully initialized with configure data")

    def login_linkedin(self):
        """Open LinkedIn log in page, enter email and password and log in to LinkedIn"""

        # Open LinkedIn log in page
        self.driver.get('https://www.linkedin.com/login')

        # Enter email and press enter key
        login_email = self.driver.find_element(By.NAME, 'session_key')
        login_email.clear()
        login_email.send_keys(self.email)

        # Enter password and press enter key
        login_pass = self.driver.find_element(By.NAME, 'session_password')
        login_pass.clear()
        login_pass.send_keys(self.password)
        time.sleep(3)

        # Press enter key to log in
        login_pass.send_keys(Keys.RETURN)

        if self.logs:
            print(f'\nLogged in to LinkedIn with email = {self.email} and password = {self.password}')

    def load_jobs_page(self):
        """Go to LinkedIn job page"""

        # Press the job button
        self.driver.find_element(By.LINK_TEXT, 'Jobs').click()

        if self.logs:
            print('\nEntered jobs page')

    def enter_keywords_and_location(self):
        """Search jobs with keyword and location"""

        # Enter keyword
        search_keywords = self.driver.find_element(By.XPATH, '//input[starts-with(@id,"jobs-search-box-keyword")]')
        search_keywords.clear()
        search_keywords.send_keys(self.keywords)
        time.sleep(3)

        # Enter location
        search_location = self.driver.find_element(By.XPATH, '//input[starts-with(@id,"jobs-search-box-location")]')
        search_location.clear()
        search_location.send_keys(self.location)
        time.sleep(3)

        # Press enter key to apply the keyword and location to jobs search
        search_location.send_keys(Keys.RETURN)

        if self.logs:
            print(f'\nApplied keyword = {self.keywords} and location = {self.location} to search')

    def filter_jobs(self):
        """Apply filters to job search"""

        # Open all filters page
        self.driver.find_element(By.XPATH, '//*[@id="search-reusables__filters-bar"]/div/div/button').click()
        time.sleep(3)

        # Apply easy apply filter
        if self.filters['easy_apply']:
            self.driver.find_element(By.CLASS_NAME, 'jobs-search-advanced-filters__binary-toggle').click()

            if self.logs:
                print("\neasy_apply filter has been chosen")

            time.sleep(3)

        # Apply experience level filters
        for index, (filter_key, filter_value) in enumerate(self.filters['experience level'].items()):
            if filter_value:
                self.driver.find_element(By.XPATH, f'//label[@for="advanced-filter-experience-{index + 1}"]').click()

                if self.logs:
                    print(f'{filter_key} filter has been chosen')

                time.sleep(3)

        # Press apply filters to apply all filters that are checked in filter page
        self.driver.find_element(By.XPATH, '//*[@class="justify-flex-end display-flex mv3 mh2"]/button[2]').click()

        if self.logs:
            print('Filters applied to job search')

    def find_job_offers(self):
        """Find all job applications of job search result, run the submit_apply() function to submit job applciation and go to next page when all jobs are applied in current page"""

        # Get the amount of jobs available for applying
        total_results = self.driver.find_element(By.CLASS_NAME, 'display-flex.t-12.t-black--light.t-normal')
        total_results_int = int(total_results.text.split(' ', 1)[0].replace(",", ""))

        if self.logs:
            print(f"\nFound {total_results_int} job offers")

        num_of_pages = 1
        flag = 1
        page_number = 2

        # Submit all job application in current page of job search result and go to next page
        while num_of_pages > 0:

            # Get the job application in current page
            results = self.driver.find_elements(By.CLASS_NAME,
                                                'ember-view.jobs-search-results__list-item.occludable-update.p0.relative.scaffold-layout__list-item')

            # Calculate the number of pages (only ones)
            if flag:
                num_of_pages = total_results_int // len(results)
                flag = 0

                if self.logs:
                    print(f"There are {num_of_pages + 1} pages")

            # Submit application in each job offer
            for result in results:
                hover = ActionChains(self.driver).move_to_element(result)
                hover.perform()
                self.submit_apply(result)

            # Go to next page of job search result
            num_of_pages -= 1
            self.driver.find_element(By.XPATH, f'//*[@aria-label="Page {page_number}"]').click()

            if self.logs:
                print(f'\nDone applying for jobs in page = {page_number - 1}\n')

            page_number += 1

    def submit_apply(self, job_application):
        """Try submitting job application using the functions submit_application(), next_step(), self.review_application() and review_application(). If not submitted in 5 tries, exit application"""

        if self.logs:
            print(f'\nYou are applying to the position of: {job_application.text}')

        # Open job application
        job_application.click()
        time.sleep(3)

        # If already applied, don't try to apply job application
        if self.already_applied():
            return

        # Try to apply job application for maximum 5 times
        num_of_submit_tries = 0
        while not self.submit_application() and num_of_submit_tries < 5:
            if self.logs:
                print(f'Try to submit number = {num_of_submit_tries + 1}')

            self.next_step()
            self.answer_additional_questions()
            self.review_application()
            num_of_submit_tries += 1

        # If didn't apply in 5 tries exit job application
        if num_of_submit_tries > 4:
            self.exit_application()

        time.sleep(1)

    def already_applied(self):
        """If already applied, don't try to apply job application.
           Return 1 if didn't apply else 0"""

        try:
            # Search easy apply button and click it if found
            self.driver.find_element(By.XPATH, '//*[@class="jobs-apply-button--top-card"]/button').click()

        except NoSuchElementException:
            # If easy apply button not found
            if self.logs:
                print('You already applied to this job, go to next')

            return 1

        return 0

    def submit_application(self):
        """Press the submit application and dismiss buttons if found.
           Return 1 if application submitted else 0"""

        try:
            # Search submit application button and click it if found
            self.driver.find_element(By.XPATH, '//button[@aria-label="Submit application"]').send_keys(Keys.RETURN)

            if self.logs:
                print('Submit clicked')

            time.sleep(3)

            # Search dismiss button and click it if found
            self.driver.find_element(By.XPATH, '//button[@aria-label="Dismiss"]').click()

            if self.logs:
                print('Dismiss clicked')

            return 1

        except NoSuchElementException:
            # If submit application or dismiss buttons not found
            if self.logs:
                print('Did not find submit application or dismiss buttons')

            return 0

    def next_step(self):
        """Go to next stage in job application"""

        try:
            # Search next button and click it if found
            self.driver.find_element(By.XPATH, '//*[@aria-label="Continue to next step"]').click()

            if self.logs:
                print('Next clicked')

        except NoSuchElementException:
            # If next button not found
            if self.logs:
                print('Did not find next button')

    def review_application(self):
        """Review application (1 step before submitting application)"""

        try:
            # Search review button and click it if found
            self.driver.find_element(By.XPATH, '//*[@aria-label="Review your application"]').click()
            if self.logs:
                print('Review clicked')

        except NoSuchElementException:
            # If review button not found
            if self.logs:
                print('Did not find review button')

    def close_session(self):
        """Close the service that the driver opened"""
        if self.logs:
            print('\nService closed')

        self.driver.close()

    def exit_application(self):
        """Close job application"""

        try:
            # Find the x(used for exit) button press enter key
            self.driver.find_element(By.XPATH,
                                     '//*[@class="artdeco-modal__dismiss artdeco-button artdeco-button--circle artdeco-button--muted artdeco-button--2 artdeco-button--tertiary ember-view"]').send_keys(
                Keys.RETURN)
            time.sleep(3)

            # Find the exit confirmation and press enter key
            self.driver.find_element(By.XPATH, '//button[@data-test-dialog-secondary-btn]').send_keys(Keys.RETURN)
            time.sleep(3)

            if self.logs:
                print('Job application was closed')

        except NoSuchElementException:
            # If submit application or dismiss buttons not found
            if self.logs:
                print('Did not find x or exit confirmation buttons')

    def answer_additional_questions(self):
        """Answer questions in the job application using answer_question(), answer_dropdown() and answer_check_box() """

        num_of_questions = 0

        try:
            # Find question in page and count them
            window_data = self.driver.find_element(By.CLASS_NAME, 'pb4')
            num_of_questions = self.num_of_qestions_to_answer(window_data)

            if self.logs:
                print(f'Found {num_of_questions} questions')

        except NoSuchElementException:
            # If didn't find questions
            if self.logs:
                print('Did not find questions')

        # Answer questions, choose values from dropdown or mark a checkbox
        for i in range(num_of_questions):
            self.answer_question(i)
            self.answer_dropdown(i)
            self.answer_check_box(i)

    def num_of_qestions_to_answer(self, questions):
        """Find out howe many ? are in the string to find the number of questions"""
        return questions.text.count('?')

    def find_answer_for_question(self, question):
        """Check if answer for question is in data that was created from confing file.
           If answer exits return it else return 1"""

        # Remove unnecessary data from string, make characters lower and create a list of words from string.
        substring = '?\nRequired'
        question = question.replace(substring, '')
        question = question.lower().split(' ')

        # Search if self.questions_answers (linkedin_question_answer from configure file) keys match a word from the question. If there is a match return the value of the key else return 1
        for q in self.questions_answers:
            if q in question:
                return self.questions_answers[q]
        return 1

    def answer_question(self, i):
        """Answer question number i"""

        try:
            # Find a question number i and get answer from find_answer_for_question() functon and answer question
            question_label = self.driver.find_element(By.XPATH, f'//*[@class="pb4"]/div[{i + 1}]/div/div/div/input')
            question_text = self.driver.find_element(By.XPATH, f'//*[@class="pb4"]/div[{i + 1}]').text
            time.sleep(3)
            answer = self.find_answer_for_question(question_text)
            question_label.clear()
            question_label.send_keys(answer)

            if self.logs:
                print(f'Question = {question_text}')
                print(f'Answer = {answer}')

        except NoSuchElementException:
            # If didn't find question
            if self.logs:
                print('Did not find question')

    def answer_dropdown(self, i):
        """Choose and option (Yes or Professional) from the dropdown"""

        answer_found = ''

        try:
            # Find dropdown options
            dropdown_options = Select(
                self.driver.find_element(By.XPATH, f'//*[@class="pb4"]/div[{i + 1}]/div/div/select')).options

            # If one of the options in drop down is Yes or Professional, choose it
            for option in dropdown_options:
                if option.text == 'Yes':
                    answer_found = 'Yes'

                elif option.text == 'Professional':
                    answer_found = 'Professional'

                if answer_found:
                    self.driver.find_element(By.XPATH,
                                             f'//*[@class="pb4"]/div[{i + 1}]/div/div/select/option[text()="{answer_found}"]').click()

                    if self.logs:
                        dropdown = self.driver.find_element(By.XPATH, f'//*[@class="pb4"]/div[{i + 1}]/div')
                        print(f'Dropdown = {dropdown.text}')
                        print(f'Chose {answer_found} from dropdown')

                    return

        except NoSuchElementException:
            # If didn't dropdown or an option to choose
            if self.logs:
                print('Did not find dropdown or an option to choose')

    def answer_check_box(self, i):
        """Check the first answer from the checkbox options"""

        try:
            # TODO add question and answer
            # Find the first option in the checkbox and check it
            self.driver.find_element(By.XPATH, f'//*[@class="pb4"]/div[{i + 1}]/fieldset/div/div[1]/label').click()

            if self.logs:
                checkbox_data = self.driver.find_element(By.XPATH, f'//*[@class="pb4"]/div[{i + 1}]/fieldset')
                checkbox_options = self.driver.find_element(By.XPATH,
                                                            f'//*[@class="pb4"]/div[{i + 1}]/fieldset/div').text
                checkbox_options = checkbox_options.split('\n')
                print(f'Checkbox = {checkbox_data.text}')
                print(f'{checkbox_options[0]} has been checked')

        except NoSuchElementException:
            # If didn't find and answer to check
            if self.logs:
                print('Did not find check box or an option to check')


def find_job():
    with open('config.json') as config_file:
        conf = json.load(config_file)

    bot = EasyApplyLinkedin(conf)

    bot.login_linkedin()
    time.sleep(3)

    bot.load_jobs_page()
    time.sleep(3)

    bot.enter_keywords_and_location()
    time.sleep(3)

    bot.filter_jobs()
    time.sleep(3)

    bot.find_job_offers()

    bot.close_session()


if __name__ == "__main__":
    find_job()
