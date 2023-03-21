#application.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Optionsoptions = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)
driver.get("https://www.google.com/")
element_text = driver.page_source
print(element_text)