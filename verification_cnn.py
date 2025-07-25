import os
import time
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

email = os.getenv("EMAIL")
password = os.getenv("PASS")
keyword = os.getenv("KEYWORD")
location = os.getenv("LOCATION")
base_url = "https://www.linkedin.com"

options = Options()
options.add_argument("--disable-popup-blocking")
driver = webdriver.Chrome(options=options)
action = ActionChains(driver)

def test_open_jobs():
    try:
        job_selector = "//div[contains(@class, 'scaffold-layout__list')]//ul/li[contains(@class, 'scaffold-layout__list-item')]"
        jobs_list = driver.find_elements(By.XPATH, job_selector)
        print(f"'test_open_jobs()': Found {len(jobs_list)} jobs (initially in DOM)")

        idx = 0
        total_jobs_seen = set()
        
        while idx < len(jobs_list):
            job = jobs_list[idx]
            job_id = job.get_attribute("id")
            if job_id in total_jobs_seen:
                idx += 1
                continue
            total_jobs_seen.add(job_id)

            driver.execute_script("arguments[0].scrollIntoView();", job)
            time.sleep(1.5)  

            try:
                job_title_elem = job.find_element(By.CSS_SELECTOR, "a.job-card-container__link span[aria-hidden='true'] strong")
                job_title = job_title_elem.text.strip()
            except NoSuchElementException:
                print(f"Job #{idx+1}: No job title found, skipping.")
                idx += 1
                continue

            easy_apply = job.find_elements(By.CSS_SELECTOR, "svg.job-card-list__icon[data-test-icon='linkedin-bug-color-small']")
            if easy_apply:
                print(f"Easy-Apply button found for Job #{idx + 1}: {job_title}")
            else:
                print(f"No Easy-Apply button found for Job #{idx + 1}: {job_title}")

            jobs_list = driver.find_elements(By.XPATH, job_selector)
            idx += 1

    except Exception as e:
        logging.error(f"'test_open_jobs()': Test failed: {str(e)}")
        return
