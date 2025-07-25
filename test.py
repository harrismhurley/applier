import os
import time
import pickle
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException


load_dotenv()

# Config
email = os.getenv("EMAIL")
password = os.getenv("PASS")
keyword = os.getenv("KEYWORD")
phone = os.getenv("PHONE")
location = os.getenv("LOCATION")
base_url = "https://www.linkedin.com"
resume_name = os.getenv("RESUME")

resume = os.path.abspath(resume_name)

# def _options():
#     options = Options()
#     options.add_argument("--incognito")
#     options.add_argument("--verbose")
#     options.add_argument("--disable-popup-blocking")
#     return options

options = Options()

driver = webdriver.Chrome(options=options)
action = ActionChains(driver)

def clear_cookies():
    driver.get('chrome://settings/clearBrowserData')
    driver.find_element(By.XPATH, '//settings-ui').send_keys(Keys.ENTER)
    time.sleep(3)


def test_sign_in_and_search():
    try:
        print(f"'test_signup()': Current URL: {driver.current_url}")
        email_input = driver.find_element(By.NAME, "session_key")
        password_input = driver.find_element(By.NAME, "session_password")
        signup_submit = driver.find_element(By.XPATH, '//button[contains(., "Sign in")]')

        email_input.send_keys(email)
        password_input.send_keys(password)
        signup_submit.click()
        time.sleep(3)
        
        #  Verification handling
        verification_endpoint = '/checkpoint/challenge/'
        if verification_endpoint in driver.current_url:
            print(f"'test_signup()': User verification required, 5 minutes to complete")
            try:
                WebDriverWait(driver, 300).until_not(
                    EC.url_contains(verification_endpoint)
                )
            except TimeoutException:
                print(f"'test_signup()': Verification timed out after 5 minutes")
                raise    
                    
        keyword_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//input[contains(@aria-label, "Search by title, skill")]')
            )
        )
        location_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//input[contains(@aria-label, "City, state, or zip code")]')
            )
        )

        keyword_input.send_keys(keyword)
        location_input.clear()
        location_input.send_keys(location, Keys.ENTER)
        print("'test_sign_in_and_search()': Search successful")
    except Exception as e:
        logging.error(f"'test_sign_in_and_search()': Test failed: {str(e)}")


def test_open_jobs():
    try:
        job_selector = "//div[contains(@class, 'scaffold-layout__list')]//ul/li[contains(@class, 'scaffold-layout__list-item')]"
        jobs_list = driver.find_elements(By.XPATH, job_selector)

        idx = 0
        total_jobs_seen = set()
        print(f"'test_open_jobs()': Found {len(jobs_list)} jobs (initially in DOM)")

        while idx < len(jobs_list):
            job = jobs_list[idx]
            job_id = job.get_attribute("id")

            if job_id in total_jobs_seen:
                idx += 1
                continue

            total_jobs_seen.add(job_id)
            driver.execute_script("arguments[0].scrollIntoView();", job)

            try:
                job_title_elem = job.find_element(
                    By.CSS_SELECTOR,
                    "a.job-card-container__link span[aria-hidden='true'] strong",
                )
                job_title = job_title_elem.text.strip()
            except NoSuchElementException:
                print(f"Job #{idx+1}: No job title found, skipping.")
                idx += 1
                continue

            easy_apply = job.find_elements(
                By.CSS_SELECTOR,
                "svg.job-card-list__icon[data-test-icon='linkedin-bug-color-small']",
            )
            if easy_apply:
                print(f"\nEasy-Apply button found for Job #{idx + 1}: {job_title}")
                job.click()
                
                apply_button = driver.find_element(
                    By.XPATH, "//button[contains(@class, 'jobs-apply-button') and .//span[text()[contains(., 'Easy Apply')]]]"
                )
                apply_button.click()
                time.sleep(3)

                test_apply_modal_1()                
                time.sleep(3)
                
                test_apply_modal_2()
                time.sleep(3)
                
                # test_apply_modal_3()
                # time.sleep(3)
                
                time.sleep(2000)

            else:
                print(f"\nNo Easy-Apply button found for Job #{idx + 1}: {job_title}")

            jobs_list = driver.find_elements(By.XPATH, job_selector)
            idx += 1

    except Exception as e:
        logging.error(f"'test_open_jobs()': Test failed: {str(e)}")
        return


def test_apply_modal_1():
    try:
        phone_input = driver.find_element(
            By.XPATH, "//label[contains(text(), 'Mobile phone number')]/following-sibling::input"
        )
        phone_input.clear()
        phone_input.send_keys(phone)
        
        submit = driver.find_element(
            By.XPATH, "//button[.//span[text()='Next']]")
        submit.click()
        
    except Exception as e:
        logging.error(f"'test_apply_modal_1()': Test failed: {str(e)}")    
    
def test_apply_modal_2():
    try:
        try:
            driver.find_element(By.XPATH, "//p[contains(@class, 'jobs-document-upload__format-text')]")
            resume_needed = True
        except NoSuchElementException:
            resume_needed = False
            
        if resume_needed:
            resume_input = driver.find_element(By.XPATH, "//input[@type='file']")
            resume_input.send_keys(resume)
            time.sleep(3)
            
        submit = driver.find_element(By.XPATH, "//button[.//span[text()='Next']]")
        submit.click()
        
    except Exception as e:
        logging.error(f"'test_apply_modal_2()': Test failed: {str(e)}")


        
# %%
def test_main():
    
    clear_cookies()
    
    driver.get(f"{base_url}/jobs")
    time.sleep(3)
    
    test_sign_in_and_search()
    time.sleep(3)

    test_open_jobs()
    time.sleep(3)

test_main()
