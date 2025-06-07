# === Imports ===
import sys, os, time
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from config import GUPY_EMAIL, GUPY_PASSWORD, SEARCH_KEYWORDS, JOB_LEVELS
from database import SessionLocal, Job, Application


# === Configurations ===
CHROMEDRIVER_PATH = r"C:\Users\ofds2\.wdm\drivers\chromedriver\win64\137.0.7151.68\chromedriver-win32\chromedriver.exe"
BASE_URL = "https://portal.gupy.io/job-search/term="
REMOTE_FILTER = "&workplaceTypes[]=remote"


# === Helper Functions ===

def handle_cookie_banner(driver):
    try:
        btn_xpath = "//span[@aria-label='Accept Cookies']"
        btn = WebDriverWait(driver, 7).until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
        print("   - Cookie banner found. Clicking to accept...")
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(2)
    except TimeoutException:
        pass


def perform_login(driver, wait):
    print("     - Login page detected. Performing login...")
    handle_cookie_banner(driver)
    wait.until(EC.visibility_of_element_located((By.ID, "username"))).send_keys(GUPY_EMAIL)
    driver.find_element(By.ID, "password-input").send_keys(GUPY_PASSWORD)
    driver.find_element(By.ID, "button-signin").click()
    print("     - Login form submitted.")


def generate_search_urls():
    urls = []
    for keyword in SEARCH_KEYWORDS:
        for level in JOB_LEVELS:
            term = quote(f"{keyword} {level}".strip())
            urls.append(f"{BASE_URL}{term}{REMOTE_FILTER}")
    return urls


def scan_page_for_new_jobs(driver, db):
    newly_found = []
    JOB_LIST_XPATH = "//h3[contains(text(), 'Vagas') or contains(text(), 'Jobs')]/following-sibling::ul[1]"

    try:
        ul = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, JOB_LIST_XPATH)))
        items = ul.find_elements(By.TAG_NAME, 'li')
        if not items: return []
    except TimeoutException:
        return []

    print(f"   - Found {len(items)} job items. Checking DB...")
    for item in items:
        try:
            link = item.find_element(By.TAG_NAME, 'a')
            url = link.get_attribute('href')
            if not url or db.query(Job).filter(Job.url == url).first():
                continue

            title = link.find_element(By.TAG_NAME, 'h3').text
            company = link.find_element(By.TAG_NAME, 'p').text
            job = Job(url=url, title=title, company=company, platform="Gupy")
            db.add(job)
            db.commit()
            print(f"     + New Job Saved: '{title}' at '{company}'")
            newly_found.append(job)
        except NoSuchElementException:
            continue

    return newly_found


def perform_application(job, driver, wait, db, logged_in):
    print(f"   -> Applying to: '{job.title}'")
    application = Application(job_id=job.id, status="Processing")
    db.add(application)
    db.commit()

    try:
        driver.get(job.url)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Candidatar-se') or contains(text(), 'Apply')]"))).click()
        if not logged_in:
            perform_login(driver, wait)

        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Continuar')]"))).click()
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "pushActionRefuse"))).click()
        except TimeoutException:
            pass
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Salvar e continuar')]"))).click()

        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "dialog-give-up-personalization-step"))).click()
            application.status = "Applied"
            application.notes = "Successfully finalized simple application."
            print("     - SUCCESS: Application finalized.")
        except TimeoutException:
            application.status = "Action Required"
            application.notes = "Requires manual answers or next steps."
            print("     - INFO: Manual steps needed.")
    except Exception as e:
        print(f"     - ERROR during application: {e}")
        application.status = "Failed"
        application.notes = f"Bot error: {str(e)}"
    finally:
        db.commit()

    return True


# === Main Bot Logic ===

# === Main Bot Logic ===

def run_gupy_bot():
    print("Starting Gupy bot with INTERLEAVED scrape-and-apply workflow...")
    db = SessionLocal()
    search_urls = generate_search_urls()

    try:
        driver = webdriver.Chrome(service=Service(CHROMEDRIVER_PATH))
        wait = WebDriverWait(driver, 20)
        driver.maximize_window()
    except Exception as e:
        db.close()
        raise e

    try:
        logged_in = False
        for url in search_urls:
            print(f"\n--- Processing Search URL: {url} ---")
            driver.get(url)
            handle_cookie_banner(driver)

            page = 1
            while True:
                print(f"-> Scraping page {page}...")
                new_jobs = scan_page_for_new_jobs(driver, db)

                if new_jobs:
                    # Improvement 1: Save the correct page URL
                    search_page_url = driver.current_url
                    
                    print(f"-> Found {len(new_jobs)} new jobs. Applying...")
                    for job in new_jobs:
                        logged_in = perform_application(job, driver, wait, db, logged_in)
                        time.sleep(3)

                    print("-> Done applying. Returning to correct search page...")
                    # Go back to the specific page we were on
                    driver.get(search_page_url)
                else:
                    print("   - No new jobs found.")

                try:
                    # Improvement 2: Make the click more robust
                    next_xpath = "//button[.//*[@data-testid='NavigateNextIcon'] and not(@disabled)]"
                    next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, next_xpath)))
                    next_button.click()
                    time.sleep(3)
                    page += 1
                except (NoSuchElementException, TimeoutException):
                    print("-> No more pages.")
                    break
    except Exception as e:
        print(f"\nAn unhandled error occurred: {e}")
    finally:
        print("\nBot run finished. Closing browser.")
        driver.quit()
        db.close()


if __name__ == "__main__":
    run_gupy_bot()
