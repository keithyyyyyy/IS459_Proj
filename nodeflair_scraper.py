import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

def scrape_jobs(url):
    driver = webdriver.Chrome()
    driver.get(url)

    job_data = []

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'jobListingCardsContainer')]"))
            )
            jobs = driver.find_element(By.XPATH, "//div[contains(@class, 'jobListingCardsContainer')]")

            jobs = jobs.find_elements(By.XPATH, "//div[contains(@class, 'jobListingCard-')]")

            for job in jobs:
                title = job.find_element(By.XPATH, ".//h2[contains(@class, 'jobListingCardTitle')]").text
                company = job.find_element(By.XPATH, ".//p[contains(@class, 'companynameAndRating')]/span").text
                country = job.find_element(By.XPATH, ".//div[contains(@class, 'country')]").text
                stacks = job.find_elements(By.XPATH, ".//span[contains(@class, 'techStackContainer')]")
                stacks_array = []
                for stack in stacks:
                    stacks_array.append(stack.text)
                salary = job.find_elements(By.XPATH, ".//span[contains(@class, 'salary')]")
                salary_amt = "Empty"
                if salary:
                    salary_amt = salary[0].text
                job_data.append({
                    'company': company,
                    'title': title,
                    'country': country,
                    'stacks': stacks_array,
                    'salary': salary_amt
                })

            next_button = driver.find_elements(By.XPATH, "//a[contains(@class, 'page-link')]")[5]

            if 'disabled' in next_button.get_attribute('class'):
                break
            else:
                next_button.click()
                time.sleep(2)

        except Exception as e:
            print(f"Error occurred: {e}")
            break

    driver.quit()

    return job_data

if __name__ == "__main__":
    url = "https://nodeflair.com/jobs?query=software&page=1&sort_by=relevant&seniorities%5B%5D=junior"
    # jobs = scrape_jobs(url)

    # with open("jobs.json", "w") as outfile:
    #     json.dump(jobs, outfile)
