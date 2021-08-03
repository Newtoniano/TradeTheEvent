import time
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from pymongo import MongoClient


ticker = 'AAL'

DB_NAME = "TTE"
client = MongoClient('localhost', 27017)
db = client[DB_NAME]
collection_news = db["news"]


options = Options()
options.headless = False
d = webdriver.Chrome(ChromeDriverManager().install())


current_url = set()

print("downloading:" + ticker)
FOUND = False

for suffix in ['', '.OQ', '.N']:
    comp_link = ticker + suffix
    url = 'https://www.reuters.com/companies/{}/news'.format(comp_link)
    d.get(url)
    soup = BeautifulSoup(d.page_source, 'lxml')
    if len(soup.find_all('div', {'class': 'item'})) > 0:
        FOUND = True
        break
    time.sleep(1.5)

url = 'https://www.reuters.com/companies/{}/news'.format(comp_link)

d.get(url)
soup = BeautifulSoup(d.page_source, 'lxml')

for item in soup.find_all('div', {'class':'item'}):
    url = item.div.a['href']
    current_url.add(url)

old_length = 0
fail_count = 0
while True:

    # Scroll down to bottom
    d.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(1.2)

    print(len(current_url))
    soup = BeautifulSoup(d.page_source, 'lxml')
    for item in soup.find_all('div', {'class':'item'}):
        url = item.div.a['href']
        current_url.add(url)

    if len(current_url) == old_length:
        fail_count += 1
        if fail_count >= 3:
            break

    old_length = len(current_url)

    time.sleep(1.2)

print("Find {} links for {}, inserting to the database".format(len(current_url), ticker))

data = []
for url in current_url:
    item = {'url':url}
    data.append(item)
collection_news.insert_many(data)

d.close()
