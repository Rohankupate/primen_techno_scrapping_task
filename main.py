import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
base_url = 'https://hprera.nic.in/PublicDashboard'

def get_project_details():
    details = {}
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#project-menu-html > div:nth-child(2) > div:nth-child(1) > div > table'))
        )
        rows = driver.find_elements(By.CSS_SELECTOR, '#project-menu-html > div:nth-child(2) > div:nth-child(1) > div > table tr')
        for row in rows:
            cols = row.find_elements(By.TAG_NAME, 'td')
            if len(cols) == 2:
                key = cols[0].text.strip()
                value = cols[1].text.strip()
                if key in ['GSTIN No.', 'PAN No.', 'Permanent Address', 'Name']:
                    details[key] = value
    except Exception as e:
        print(f"Error fetching details: {e}")
    return details

def scrape_projects():
    driver.get(base_url)
    projects = []
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[title="View Application"]'))
        )
        links = driver.find_elements(By.CSS_SELECTOR, 'a[title="View Application"]')
        for link in links[:6]:
            project_id = link.text
            try:
                driver.execute_script("arguments[0].click();", link)
                time.sleep(3)
                details = get_project_details()
                details['Project ID'] = project_id
                projects.append(details)
            except Exception as e:
                print(f"Error during clicking or detail page processing: {e}")
    except Exception as e:
        print(f"Error during scraping: {e}")
    return projects

def main():
    try:
        projects = scrape_projects()
        if projects:
            df = pd.DataFrame(projects)
            df.to_csv('projects_details.csv', index=False)
        else:
            print("No data collected.")
    finally:
        driver.quit()

if __name__ == '__main__':
    main()
