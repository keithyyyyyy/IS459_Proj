from dotenv import load_dotenv
import os

import time
from datetime import datetime, timedelta
import boto3
import pandas as pd
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

load_dotenv()
access_key_id = os.getenv("ACCESS_KEY_ID")
secret_access_key = os.getenv("SECRET_ACCESS_KEY")

# read json file for companies to scrape
f = open('indeed_companies.json')
# f = open('./companies_to_scrape/indeed.json')
companies = json.load(f)

# review variables
REVIEWCOLUMNONE = "Rating"
REVIEWCOLUMNTWO = "Title"
REVIEWCOLUMNTHREE = "Comment"
reviewDetails = pd.DataFrame(columns=[REVIEWCOLUMNONE, REVIEWCOLUMNTWO, REVIEWCOLUMNTHREE])

############################### Functions ###############################

# get Rating
def getRating(review):
    global reviewDetails
    
    ratingInView = review.find_element(By.XPATH,".//div[@class='css-1h3aion eu4oa1w0']/div/button")
    rating = ratingInView.text

    reviewDetails.loc[len(reviewDetails), REVIEWCOLUMNONE] = rating

# get Title
def getTitle(review):
    global reviewDetails
    
    titleInView = review.find_element(By.XPATH,".//h2[@class='css-wn2j4x e1tiznh50']")
    anchorTag = titleInView.find_element(By.XPATH,".//span[@class='css-82l4gy eu4oa1w0']")
    title = anchorTag.text

    reviewDetails.loc[len(reviewDetails)-1, REVIEWCOLUMNTWO] = title

# get Comment
def getComment(review):
    global reviewDetails
    reviews = []

    anchorTag = review.find_elements(By.XPATH,".//div[@class='css-rr5fiy eu4oa1w0']")
    for r in anchorTag:
        reviewTag = r.find_elements(By.XPATH,".//span[@class='css-82l4gy eu4oa1w0']")
        for c in reviewTag:
            reviews.append(c.text)
    
    reviewDetails.loc[len(reviewDetails)-1, REVIEWCOLUMNTHREE] = reviews

# scrape details for each company
def fullReview(company):
    global companyURL
    global reviewCount
    global count
    global numOfReview

    driver.get(company)

    # wait for initialize, in seconds
    wait = WebDriverWait(driver, 10)

    action_chains = ActionChains(driver)
    action_chains.move_by_offset(100, 100).click().perform()

    # get total review count once
    if count == 0:
        try:
            # get review count
            reviewCountTag = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='css-r5p2ca eu4oa1w0']/span")))
            reviewCountDesc = reviewCountTag.text
            reviewCountText = reviewCountDesc.split(" ")[2]
        
            reviewCountTextSplit = reviewCountText.split(",")
            for i in reviewCountTextSplit:
                numOfReview += int(i)
        except:
            print("Error getting review count.")

    reviewsContainer = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='cmp-ReviewsList']")))
    wait.until(EC.presence_of_all_elements_located((By.XPATH,"//div[@class='cmp-ReviewsList']")))
    reviewsInView = reviewsContainer.find_elements(By.XPATH,"//div[@class='css-t3vkys eu4oa1w0']")

    for review in reviewsInView:
        # review rating
        getRating(review)

        # review title
        getTitle(review)

        # review comment
        getComment(review)
    
    # check if next page exist
    try:
        count+=20
        if numOfReview == 0:
            numOfReview = count
        if count <= reviewCount and count <= numOfReview:
            fullReview(companyURL + "&start=" + str(count))
    except:
        print("There are no more pages of reviews.")

# save file in json
def save_json(filename, new_dict):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(new_dict, f, ensure_ascii=False, indent=4, default=str)
    except:
        print(f"Error saving {filename}.")

############################### SCRAPING  ###############################

# s = Service("C:\chromedriver.exe")

# driver = webdriver.Chrome(service=s)

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--start-fullscreen')
chrome_options.add_argument('--no-sandbox')

driver = webdriver.Chrome(options=chrome_options)

start = time.time()
print("Beginning scraper now...")

cdict = {}

for c in companies:
    try_count = 1

    companyName = c
    companyURL = companies[c] + "?fcountry=ALL"
    
    while try_count < 3:
        reviewDetails = pd.DataFrame(columns=[REVIEWCOLUMNONE, REVIEWCOLUMNTWO, REVIEWCOLUMNTHREE])
        
        try: 
            reviewCount = 50
            count = 0
            numOfReview = 0
            print(f"Beginning attempt {try_count} of scraping {companyName} reviews...")
            fullReview(companyURL)

            try_count += 2
        
        except:
            print(f"Attempt {try_count} of scraping {companyName} failed.")
            try_count += 1
        
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])

    jreviews = reviewDetails.to_json(orient="records")
    parsedV = json.loads(jreviews)
    cdict[companyName] = parsedV

    print(f"Scraping of {companyName} reviews completed.")
    print(f"{len(parsedV)} reviews scraped.\n")

# export file in json
# save_json("indeedReviews.json",cdict)

s3 = boto3.client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
bucket_name = 'is459-t3-job-raw-data'
file_name = 'indeed_reviews.json'
json_string = json.dumps(cdict)

s3.put_object(
    Bucket=bucket_name,
    Key='indeed_raw/' + file_name,
    Body=json_string.encode('utf-8')
)


end = time.time()

print("Indeed companies scraping completed.")
print("\n\n===========================================")
print("TOTAL TIME TAKEN: ",end - start)
print("===========================================\n\n")

driver.quit()
