from dotenv import load_dotenv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import json
import boto3
import os

load_dotenv()

access_key_id = os.getenv("ACCESS_KEY_ID")
secret_access_key = os.getenv("SECRET_ACCESS_KEY")

def scrape_jobs(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--start-fullscreen')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    driver.set_window_size(1920, 1080)

    job_data = []

    while True:
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'page-link')]"))
            )
            jobs = driver.find_element(By.XPATH, "//div[contains(@class, 'jobListingCardsContainer')]")

            jobs = jobs.find_elements(By.XPATH, "//div[contains(@class, 'jobListingCard-')]")

            for job in jobs:
                job.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'jobDescriptionContent')]"))
                )
                title = job.find_elements(By.XPATH, ".//h2[contains(@class, 'jobListingCardTitle')]")[0].text
                company = job.find_elements(By.XPATH, ".//p[contains(@class, 'companynameAndRating')]/span")[0].text
                stacks = job.find_elements(By.XPATH, ".//span[contains(@class, 'techStackContainer')]")
                description = job.find_elements(By.XPATH, "//div[contains(@class, 'jobDescriptionContent')]")[0].text
                src = job.find_elements(By.XPATH, "//img[contains(@class, 'companyAvatar')]")[0].get_attribute("src")
                stacks_array = []
                for stack in stacks:
                    stacks_array.append(stack.text)
                salary = job.find_elements(By.XPATH, ".//span[contains(@class, 'salary')]")
                salary_amt = "Empty"
                if salary:
                    salary_amt = salary[0].text
                job_data.append({
                    'company': company,
                    'img': src,
                    'title': title,
                    'stacks': stacks_array,
                    'salary': salary_amt,
                    'description': description
                })

            current_button = driver.find_element(By.XPATH, "//li[contains(@class, 'page-item') and contains(@class, 'active')]")
            current_button = current_button.find_element(By.XPATH, ".//a").text
            next_button = driver.find_elements(By.XPATH, "//a[contains(@class, 'page-link')]")[-2]
            print(current_button)

            # break
            if next_button.text != "⟩":
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
    url = "https://nodeflair.com/jobs?query=software&page=1&sort_by=relevant&positions%5B%5D=full_stack_developer&positions%5B%5D=backend_developer&positions%5B%5D=frontend_developer&positions%5B%5D=gaming_engineer&positions%5B%5D=blockchain_engineer&positions%5B%5D=android_developer&positions%5B%5D=ios_developer&positions%5B%5D=mobile_developer&positions%5B%5D=data_analyst&positions%5B%5D=data_engineer&positions%5B%5D=data_scientist&positions%5B%5D=algorithm_engineer&positions%5B%5D=devops_engineer&positions%5B%5D=reliability_engineer&positions%5B%5D=sysops_engineer&positions%5B%5D=qa_engineer&positions%5B%5D=cybersecurity_engineer&positions%5B%5D=cybersecurity_operations&seniorities%5B%5D=junior&countries%5B%5D=Singapore"
    jobs = scrape_jobs(url)

    s3 = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    bucket_name = 'is459-t3-job-raw-data'
    file_name = 'jobs.json'
    json_string = json.dumps(jobs)

    s3.put_object(
        Bucket=bucket_name,
        Key='nodeflair_raw/' + file_name,
        Body=json_string.encode('utf-8')
    )


    # with open("jobs.json", "w") as outfile:
    #     json.dump(jobs, outfile)
    
    
    


