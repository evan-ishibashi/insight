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
import pandas as pd
import time
from datetime import date
from selenium.webdriver.common.keys import Keys
from state_name_to_abbr import name_to_abbreviation
from fb_market_utils import Fb_market_utils


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
    "Chicago, Illinois",
    "Tampa, Florida",
    "Minneapolis, Minnesota",
    "Jackson, Mississippi",
    "Raleigh, North Carolina",


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
    STATE_ABBR = name_to_abbreviation[STATE]


    if i > 0:
        browser.find_by_text(f'{LOCATIONS[i - 1]}').click()
    else:
        browser.find_by_text(f'{LOCATIONS[i]}').click()



    browser.find_by_css('input[aria-label="Location"]').click()
    time.sleep(1)
    while (len(browser.find_by_css('input[aria-label="Location"]').value)) > 0:
        browser.find_by_css('input[aria-label="Location"]').type(Keys.BACKSPACE)
    time.sleep(1)
    browser.find_by_css('input[aria-label="Location"]').type(f'{LOCATIONS[i]}')
    time.sleep(4)


    browser.find_by_css('input[aria-label="Location"]').type(Keys.DOWN)
    time.sleep(1)
    browser.find_by_css('input[aria-label="Location"]').type(Keys.ENTER)
    time.sleep(1)



    browser.find_by_css('div[aria-label="Apply"]').click()
    time.sleep(2)


    # scroll down to load more results

    scroll_count = 4

    scroll_delay = 5

    for _ in range(scroll_count):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(scroll_delay)



    # Parse HTML
    html = browser.html

    titles_list, prices_list, image_list, location_miles_list, urls_list = Fb_market_utils.parse_html(html)

    # Skips to next location if no listings
    if len(titles_list) == 0:
        print("No listings for this location. Continuing to next location")
        continue

    # appends filler locations / mileage data
    appended_mileage_locations = Fb_market_utils.append_locations_mileage(
                                    location_miles_list, CITY, STATE_ABBR
                                    )

    # cleans the appended data and splits into two lists
    (locations_clean, mileage_clean) = Fb_market_utils.separate_clean_locations_mileage(
                                                        appended_mileage_locations
                                                        )
    # cleans price data into Integers
    prices_clean = Fb_market_utils.clean_prices(prices_list)



    # Make URLS full url
    urls_clean = Fb_market_utils.clean_urls

    if len(locations_clean) != len(titles_list):
        print("location data length not equal to ", len(titles_list))
        print("location data length is ", len(locations_clean))
        continue

    if len(mileage_clean) != len(titles_list):
        print("mileage data length not equal to ", len(titles_list))
        print("mileage data length is ", len(mileage_clean))
        continue

    if len(prices_clean) != len(titles_list):
        print("prices data length not equal to ", len(titles_list))
        print("prices data length is ", len(prices_clean))
        continue

    # add all values to a list of dictionaries
    vehicles_list = Fb_market_utils.organize_data(titles_list,
                                    locations_clean, mileage_clean,
                                    prices_clean, urls_clean, image_list)


    vehicles_df = pd.DataFrame(vehicles_list)


    filtered_df = vehicles_df[vehicles_df['insight'] == True]


    csv_file_path = f'/Users/evanishibashi/Projects/insight/csv/fb/{date.today()}/{location}.csv'

    filtered_df.to_csv(csv_file_path, index=False)

# End browsing session
browser.quit()


Fb_market_utils.csv_to_db()


