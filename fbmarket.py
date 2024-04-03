#!/usr/bin/env python
# coding: utf-8

"""
This file scrapes the html from facebook marketplace for honda insight car
listings. It iterates through a list of cities, grabs the info from each
respective page, and exports the cleaned data into csv file. It then inserts
the data from those CSVs into my PSQL DB.
"""

# In[289]:


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


# In[290]:


# Set up splinter
browser = Browser('chrome')

# base url
base_url = "https://www.facebook.com/marketplace/sanfrancisco/search?"

# search parameters
deliveryMethod = "local_pick_up"
query = "honda%20insight"
availability = "in%20stock"

# List of cities
LOCATIONS = [
    "San Francisco, California",
    "Los Angeles, California",
    "Seattle, Washington",
    "New York, New York",
    "Pittsburgh, Pennsylvania",
    "Austin, Texas",
    "Salt Lake City, Utah",
    "Boulder, Colorado",
    "Nashville, Tennessee"

]

#full url
url = f"{base_url}availability={availability}&deliveryMethod={deliveryMethod}&query={query}"

# Make new directory for the day if you have not yet
if not os.path.exists(f'/Users/evanishibashi/Projects/insight/csv/fb/{date.today()}'):
    os.mkdir(f'/Users/evanishibashi/Projects/insight/csv/fb/{date.today()}')
#visit site
browser.visit(url)


# In[292]: Exit out of pop up


if browser.is_element_present_by_css('div[aria-label="Close"]', wait_time=10):
    # Click on the element once it's found
    browser.find_by_css('div[aria-label="Close"]').first.click()




# MASSIVE LOOP STARTS!!!!!

for i, location in enumerate(LOCATIONS):
    print("STARTING CYCLE FOR ", location)
    CITY = location.split(", ")[0]
    STATE = location.split(", ")[1]
    STATE_ABBR = location.split(", ")[1][0] + location.split(", ")[1][1].upper()

    # In[296]:

    if i > 0:
        browser.find_by_text(f'{LOCATIONS[i - 1]}').click()
    else:
        browser.find_by_text(f'{LOCATIONS[i]}').click()



    # In[305]:

    browser.find_by_css('input[aria-label="Location"]').click()
    time.sleep(1)
    while (len(browser.find_by_css('input[aria-label="Location"]').value)) > 0:
        browser.find_by_css('input[aria-label="Location"]').type(Keys.BACKSPACE)
    time.sleep(1)
    browser.find_by_css('input[aria-label="Location"]').type(f'{LOCATIONS[i]}')
    time.sleep(4)


    # In[306]:


    browser.find_by_css('input[aria-label="Location"]').type(Keys.DOWN)
    time.sleep(1)
    browser.find_by_css('input[aria-label="Location"]').type(Keys.ENTER)
    time.sleep(1)


    # In[307]:


    browser.find_by_css('div[aria-label="Apply"]').click()
    time.sleep(2)


    # In[308]:


    # scroll down to load more results

    scroll_count = 4

    scroll_delay = 5

    for _ in range(scroll_count):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(scroll_delay)


    # In[309]:


    # Parse HTML
    html = browser.html

    #create BS object from HTML
    market_soup = soup(html, "html.parser")


    # In[310]:


    # End browsing session
    # browser.quit()


    # In[311]:


    # Extract all the info, put into lists
    titles_div = market_soup.find_all('span', class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6")
    titles_list = [title.text.strip() for title in titles_div]
    titles_list.pop(0)
    titles_list.pop(0)

    prices_div = market_soup.find_all('span', class_="x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1lkfr7t x1lbecb7 x1s688f xzsf02u")
    prices_list = [price.text.strip() for price in prices_div]

    miles_div = market_soup.find_all('span', class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft")
    miles_list = [mile.text.strip() for mile in miles_div]

    image_elems = market_soup.find_all('img', class_= "xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3")
    image_list = [image.get('src') for image in image_elems]

    urls_elems = market_soup.find_all('a', class_= "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv")
    urls_list = [url.get('href') for url in urls_elems]




    # In[312]:


    print("titles length", len(titles_list))





    # In[313]:


    print("image_list length", len(image_list))


    # In[314]:


    print("miles_list", len(miles_list))


    # In[315]:


    print("urls_list", len(urls_list))


    # In[316]:


    # regex to filter
    # pattern for City, State (ex: Los Angeles, CA)
    location_pattern = re.compile(r'[a-zA-Z -]+[,]\s[A-Z][A-Z]')
    # pattern for miles (ex: 100K miles)
    miles_pattern = re.compile(r'([0-9.]+)[K]? miles')

    # initialize empty list
    miles_list2 = []

    #iterate through the original mileage entries
    for item in miles_list:

        # Current item is location, previous item is location (2 locations in a row)
        if location_pattern.match(item) and len(miles_list2) >= 1 and location_pattern.match(miles_list2[-1]):
            miles_list2.append('0K miles')
            miles_list2.append(item)

        # Current item is empty string, Previous item is location (Miles is empty string)
        elif len(item) == 0 and location_pattern.match(miles_list2[-1]) and len(miles_list2) >=1:
            miles_list2.append('0K miles')

        # Previous item is miles, and current item is miles (Missing Location)
        elif miles_pattern.match(item) and len(miles_list2) >= 1 and miles_pattern.match(miles_list2[-1]):
            miles_list2.append(f'{CITY}, {STATE_ABBR}')
            miles_list2.append(item)

        # Previous item is location, and current item does not match (2 locations in a row)
        elif len(miles_list2) >= 1 and location_pattern.match(miles_list2[-1]) and miles_pattern.match(item) == None:
            miles_list2.append('0K miles')


        else:
            miles_list2.append(item)



    # In[317]:


    print("prices list", len(prices_list))


    # In[318]:


    # Clean Location and Miles Data
    miles_pattern_miles = r'([0-9.]+)[K]? miles'
    miles_pattern_km = r'(\d+)K km'
    location_pattern = r'[a-zA-Z ]+[,]\s[A-Z][A-Z]'

    full_city_pattern = r'[a-zA-Z ]+[,]\s[' + STATE + r']{' + f'{len(STATE)}' + r'}'


    miles_clean = []
    locations_clean =[]

    for item in miles_list2:

        match_miles_km = re.search(miles_pattern_km, item)

        match_mileage_miles = re.search(miles_pattern_miles, item)

        match_location = re.search(location_pattern, item)

        match_full_city = re.search(full_city_pattern, item)

        if match_miles_km or match_mileage_miles or match_location or match_full_city:
            if match_miles_km:
                miles_clean.append(int(match_miles_km.group(1)) *1000)

            if match_mileage_miles:
                miles_clean.append(int(float(match_mileage_miles.group(1))) *1000)
                # print(match_mileage_miles)
                # print(int(float(match_mileage_miles.group(1))) *1000)

            if match_location:
                locations_clean.append(item)

            if match_full_city:
                locations_clean.append(item)

        else:
            print('NON-MATCHING MILES/LOCATION',item)


    # In[319]:
    print("locations_clean length",len(locations_clean))


    # Make Prices into Integer
    prices_clean = []

    for price in prices_list:
        if price == 'Free':
            prices_clean.append(0)
        elif price == "·":
            prices_clean.append("Pending")
        else:
            prices_clean.append(int(re.sub(r'[₹,M,X,$,]','', price)))


    # In[320]:


    # Make URLS full url
    urls_clean = []

    for url in urls_list:
        urls_clean.append('https://www.facebook.com' + url)


    # In[321]:


    # miles_list2


    # In[322]:


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
        city = locations_clean[i].split(', ')[0]
        state = locations_clean[i].split(', ')[-1]



        # Map out key value pairs
        cars_dict["date"] = date.today()
        cars_dict["title"] = titles_list[i]
        cars_dict["price"] = prices_clean[i]
        cars_dict["city"] = city
        cars_dict["state"] = state
        cars_dict["mileage"] = miles_clean[i]
        cars_dict["url"] = urls_clean[i]
        cars_dict["image"] = image_list[i]
        cars_dict["insight"] = insight
        cars_dict["first_gen"] = first_gen
        cars_dict["parts"] = parts
        cars_dict["site"] = "fb"
        vehicles_list.append(cars_dict)


    # In[323]:


    vehicles_list


    # In[324]:


    vehicles_df = pd.DataFrame(vehicles_list)


    # In[325]:


    # vehicles_df


    # In[326]:

    filtered_df = vehicles_df[vehicles_df['insight'] == True]


    # In[327]:


    # filtered_df


    # In[328]:


    csv_file_path = f'/Users/evanishibashi/Projects/insight/csv/fb/{date.today()}/{location}.csv'

    filtered_df.to_csv(csv_file_path, index=False)


    # In[ ]:

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

directory = f'../csv/fb/{date.today()}'

for location_csv in os.listdir(directory):
    full_file_path = os.path.join(directory,location_csv)

    with open(full_file_path) as fb_listings:
        clean_listings = []
        csv_reader = DictReader(fb_listings)
        for row in csv_reader:
            #convert string boolean values to actual Boolean
            for key, value in row.items():
                if value.lower() in ['true','false']:
                    row[key] = ast.literal_eval(value.title())
            clean_listings.append(row)

        db.session.bulk_insert_mappings(Listing, clean_listings)


db.session.commit()


