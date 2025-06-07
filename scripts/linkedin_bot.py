# === Imports ===
import sys
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# === Path Setup ===
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(PROJECT_ROOT)

from config import CHROMEDRIVER_PATH
from database import SessionLocal, Job, Application

# === Configurations ===
# Using the specific, pre-filtered URL you provided
LINKEDIN_SEARCH_URL = "https://www.linkedin.com/jobs/search/?f_AL=true&f_WT=2&keywords=java%20pleno"
LINKEDIN_COOKIES_PATH = os.path.join(PROJECT_ROOT, "linkedin_cookies.json")


# === Helper Functions ===

def perform_cookie_login(driver):
    """
    Performs login to LinkedIn by loading session cookies from a file.
    """
    print("   - Attempting login using session cookies...")
    try:
        with open(LINKEDIN_COOKIES_PATH, 'r') as file:
            cookies = json.load(file)
    except FileNotFoundError:
        print(f"   - ERROR: Cookie file not found at {LINKEDIN_COOKIES_PATH}")
        return False

    # Navigate to a base URL to set the cookies
    driver.get("https://www.linkedin.com/")
    time.sleep(2)

    # NEW: Delete any existing cookies before adding the new one
    driver.delete_all_cookies()

    for cookie in cookies:
        driver.add_cookie(cookie)

    print("   - Cookies loaded into the browser session.")
    driver.refresh()
    time.sleep(5)

    if "feed" in driver.current_url.lower():
        print("   - SUCCESS: Logged in successfully.")
        return True
    else:
        print("   - FAILED: Could not log in with cookies.")
        return False

def scrape_job_listings(driver, wait, db):
    """
    Navigates to the search URL, scrolls to load all jobs,
    and scrapes the job data.
    """
    print("\n--- Starting Job Scraping Phase ---")
    driver.get(LINKEDIN_SEARCH_URL)

    try:
        # Wait for the main job list container to load
        list_container_xpath = "//div[contains(@class, 'scaffold-layout__list-container')]"
        list_container = wait.until(EC.presence_of_element_located((By.XPATH, list_container_xpath)))

        # Scroll down to load all jobs
        print("   - Scrolling to load all job listings...")
        last_height = driver.execute_script("return arguments[0].scrollHeight", list_container)
        while True:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", list_container)
            time.sleep(2) # Wait for new jobs to load
            new_height = driver.execute_script("return arguments[0].scrollHeight", list_container)
            if new_height == last_height:
                break
            last_height = new_height
        print("   - Finished scrolling.")

        # Find all individual job cards
        job_cards = driver.find_elements(By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]")
        print(f"   - Found {len(job_cards)} job cards on the page.")

        if not job_cards:
            print("   - No job cards found. The page structure may have changed.")
            return

        newly_found_jobs = []
        for card in job_cards:
            try:
                link_element = card.find_element(By.TAG_NAME, 'a')
                job_url = link_element.get_attribute('href').split('?')[0] # Clean URL

                # Check if job already exists in the database
                if db.query(Job).filter(Job.url == job_url).first():
                    continue

                job_title = card.find_element(By.CLASS_NAME, 'job-card-list__title').text
                company_name = card.find_element(By.CLASS_NAME, 'job-card-container__primary-description').text

                job = Job(url=job_url, title=job_title, company=company_name, platform="LinkedIn")
                db.add(job)
                db.commit()
                print(f"     + New Job Saved: '{job_title}' at '{company_name}'")
                newly_found_jobs.append(job)

            except NoSuchElementException:
                # This can happen with ad cards or other non-standard list items
                continue
        
        print(f"\n--- Found and saved {len(newly_found_jobs)} new jobs. ---")


    except TimeoutException:
        print("   - ERROR: Timed out waiting for job listings to load.")
        return


# === Main Bot Logic ===

def run_linkedin_bot():
    """
    Main function to run the LinkedIn bot.
    """
    print("--- Starting LinkedIn Bot ---")
    db = SessionLocal()

    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service)
        wait = WebDriverWait(driver, 15)
        driver.maximize_window()
    except Exception as e:
        print(f"ERROR: Could not initialize the Selenium driver: {e}")
        db.close()
        return

    try:
        logged_in = perform_cookie_login(driver)

        if logged_in:
            scrape_job_listings(driver, wait, db)
            #
            # <<< STEP 28 (APPLYING LOGIC) WILL GO HERE >>>
            #

    except Exception as e:
        print(f"\nAn unhandled error occurred: {e}")
    finally:
        print("\nBot run finished. Closing browser.")
        driver.quit()
        db.close()


if __name__ == "__main__":
    run_linkedin_bot()