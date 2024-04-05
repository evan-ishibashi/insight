#!/usr/bin/env python
# coding: utf-8

# In[351]:


#import libraries
#Need to pip install selenium
import os
from splinter import Browser
from bs4 import BeautifulSoup as soup
import re
import pandas as pd
import time
from datetime import date
from selenium.webdriver.common.keys import Keys

zipcode_list = [
    '90012', # Los Angeles
    '94122', # San Francisco
    '10001', # New York
    '78732', # Austin
]

# Make new directory for the day if you have not yet
if not os.path.exists(f'/Users/evanishibashi/Projects/insight/csv/offerup/{date.today()}'):
    os.mkdir(f'/Users/evanishibashi/Projects/insight/csv/offerup/{date.today()}')


# Set up splinter
browser = Browser('chrome')

# base url
base_url = "https://offerup.com/search?"

# search parameters
# days_listed = 7
query = "honda+insight"
distance = 200

#full url
url = f"{base_url}q={query}&DISTANCE={distance}"


#visit site
browser.visit(url)


#MASSIVE LOOP STARTS HERE

for zipcode in zipcode_list:
    print("starting process for zipcode", zipcode)

    # Click on the element once it's found
    browser.find_by_css('button[aria-label="Set my location currently set to"]').click()
    time.sleep(1)
    browser.find_by_css('div[class="MuiGrid-root MuiGrid-container MuiGrid-spacing-xs-2 MuiGrid-justify-content-xs-space-between"]').click()
    time.sleep(1)
    browser.find_by_name('zipCode').type(Keys.BACKSPACE)
    browser.find_by_name('zipCode').type(Keys.BACKSPACE)
    browser.find_by_name('zipCode').type(Keys.BACKSPACE)
    browser.find_by_name('zipCode').type(Keys.BACKSPACE)
    browser.find_by_name('zipCode').type(Keys.BACKSPACE)
    browser.find_by_name('zipCode').type(f'{zipcode}')
    time.sleep(1)
    browser.find_by_css('button[aria-label="Apply"]').click()
    time.sleep(1)
    browser.find_by_css('button[aria-live="polite"]').click()


    # scroll down to load more results

    scroll_count = 4

    scroll_delay = 3

    for _ in range(scroll_count):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(scroll_delay)


    # Parse HTML
    html = browser.html

    #create BS object from HTML
    market_soup = soup(html, "html.parser")


    # Extract all the info, put into lists
    info_tag = market_soup.findAll(href=re.compile("item/detail"))

    titles_list = [title.get('title') for title in info_tag]
    titles_list.pop(0)

    info_list = [title.get('aria-label') for title in info_tag]
    info_list.pop(0)

    href_list = [tag.get('href') for tag in info_tag]
    href_list.pop(0)


    img_tag = market_soup.findAll(src=re.compile(".jpg"))
    img_list = [tag.get('src') for tag in img_tag]

    # print(titles_list)

    # print(info_list)

    # print(href_list)

    # print(img_list)



    # Split info into Price, Mileage, Location

    prices_list = []
    mileage_list = []
    locations_list = []

    location_pattern = r'\s[i][n]\s[a-zA-Z -]*[,]\s[A-Z][A-Z]'
    mileage_pattern = r'\s[0-9]+[k]'
    price_pattern = r'[$][0-9,]+'

    for item in info_list:

        price_match = re.search(price_pattern, item)
        mileage_match = re.search(mileage_pattern, item)
        location_match = re.search(location_pattern, item)

        # Handles parsing out the Price
        if price_match:
            prices_list.append(int(re.sub(r'[₹,M,X,$,]','', price_match[0])))
        else:
            prices_list.append(0)

        # Handles parsing out the Mileage
        if mileage_match:
            miles_int = (int(mileage_match[0][1:-1]) *1000)
            mileage_list.append(miles_int)
        else:
            mileage_list.append(0)

        # Handles parsing out the Location
        if location_match:
            location_clean = location_match[0][4:]
            locations_list.append(location_clean)
        else:
            locations_list.append(0)


    print('prices_list length', len(prices_list),
        '\nmileage_list length', len(mileage_list),
        '\nlocations_list length', len(locations_list),
        '\nhref_list length', len(href_list),
        '\nimg_list length', len(img_list))


    # Make URLS full url
    url_list = []

    for href in href_list:
        url_list.append('https://www.offerup.com' + href)


    # add all values to a list of dictionaries
    vehicles_list = []

    for i, item in enumerate(titles_list):
        cars_dict = {}
        first_gen = False
        insight = False
        parts = False
        years = ["2000", "2001", "2002", "2003", "2004", "2005", "2006", "1st", "first gen"]

        #Checks if any cars are 2000 - 2006
        if any(x in titles_list[i] for x in years):
            first_gen = True

        #Checks if car listing is for parts
        if "part" in titles_list[i].lower():
            parts = True

        #Checks if insight is actually in the title
        if "insight" in titles_list[i].lower():
            insight = True

        #Splits up the City and State from location
        city = locations_list[i].split(', ')[0]
        state = locations_list[i].split(', ')[-1]



        # Map out key value pairs
        cars_dict["date"] = date.today()
        cars_dict["title"] = titles_list[i]
        cars_dict["price"] = prices_list[i]
        cars_dict["city"] = city
        cars_dict["state"] = state
        cars_dict["mileage"] = mileage_list[i]
        cars_dict["url"] = url_list[i]
        # cars_dict["image"] = None
        cars_dict["insight"] = insight
        cars_dict["first_gen"] = first_gen
        cars_dict["parts"] = parts
        cars_dict["site"] = "offerup"
        vehicles_list.append(cars_dict)


    vehicles_df = pd.DataFrame(vehicles_list)


    filtered_df = vehicles_df[vehicles_df['insight']==True]


    csv_file_path = f'/Users/evanishibashi/Projects/insight/csv/offerup/{date.today()}/{zipcode}.csv'

    filtered_df.to_csv(csv_file_path, index=False)

# End browsing session
browser.quit()


# Insert newly attained data into DB
from csv import DictReader
from app import db
from models import Listing
from datetime import date
import ast
import os

# db.drop_all()
# db.create_all()

directory = f'../csv/offerup/{date.today()}'

for location_csv in os.listdir(directory):
    full_file_path = os.path.join(directory,location_csv)

    with open(full_file_path) as offerup_listings:
        clean_listings = []
        csv_reader = DictReader(offerup_listings)
        for row in csv_reader:
            #convert string boolean values to actual Boolean
            for key, value in row.items():
                if value.lower() in ['true','false']:
                    row[key] = ast.literal_eval(value.title())
            clean_listings.append(row)

        db.session.bulk_insert_mappings(Listing, clean_listings)


db.session.commit()




