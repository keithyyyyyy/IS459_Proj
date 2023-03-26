import time
from datetime import datetime, timedelta
import pandas as pd
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

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

    driver.get(company)

    # wait for initialize, in seconds
    wait = WebDriverWait(driver, 10)

    # get total review count once
    if count == 0:
        try:
            # get review count
            reviewCountTag = wait.until(EC.visibility_of_element_located((By.XPATH,"//div[@class='css-r5p2ca eu4oa1w0']/span")))
            reviewCountDesc = reviewCountTag.text
            reviewCountText = reviewCountDesc.split(" ")[2]
        
            reviewCountTextSplit = reviewCountText.split(",")
            for i in reviewCountTextSplit:
                reviewCount += int(i)
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
        if count <= reviewCount:
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
    reviewDetails = pd.DataFrame(columns=[REVIEWCOLUMNONE, REVIEWCOLUMNTWO, REVIEWCOLUMNTHREE])

    companyName = c
    companyURL = companies[c] + "?fcountry=ALL"

    reviewCount = 0
    count = 0
    print(f"Beginning scraping of {companyName}...")
    fullReview(companyURL)

    jreviews = reviewDetails.to_json(orient="records")
    parsedV = json.loads(jreviews)
    cdict[companyName] = parsedV

    print(f"{companyName} completed.")

# export file in json
save_json("indeedReviews.json",cdict)

end = time.time()

print("Indeed companies scraping completed.")
print("\n\n===========================================")
print("TOTAL TIME TAKEN: ",end - start)
print("===========================================\n\n")

driver.quit()