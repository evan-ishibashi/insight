#!/usr/bin/env python
# coding: utf-8

"""
This file scrapes the html from facebook marketplace for honda insight car
listings. It iterates through a list of cities, grabs the info from each
respective page, and exports the cleaned data into csv file. It then inserts
the data from those CSVs into my PSQL DB.
"""


# import libraries
import time
from selenium.webdriver.common.keys import Keys
from state_name_to_abbr import name_to_abbreviation
from fb_market_utils import Fb_market_utils


# Set up splinter
browser = Fb_market_utils.create_browser()

Fb_market_utils.set_up(browser)


# MASSIVE LOOP STARTS!!!!!

for i, location in enumerate(Fb_market_utils.LOCATIONS):
    print("STARTING CYCLE FOR ", location)
    CITY = location.split(", ")[0]
    STATE = location.split(", ")[1]
    STATE_ABBR = name_to_abbreviation[STATE]

    if i > 0:
        browser.find_by_text(f'{Fb_market_utils.LOCATIONS[i - 1]}').click()
    else:
        browser.find_by_text(f'{Fb_market_utils.LOCATIONS[i]}').click()

    browser.find_by_css('input[aria-label="Location"]').click()
    time.sleep(1)
    while (len(browser.find_by_css('input[aria-label="Location"]').value)) > 0:
        browser.find_by_css(
            'input[aria-label="Location"]').type(Keys.BACKSPACE)
    time.sleep(1)
    browser.find_by_css(
        'input[aria-label="Location"]').type(f'{Fb_market_utils.LOCATIONS[i]}')
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
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        time.sleep(scroll_delay)

    # Parse HTML
    html = browser.html

    titles_list, prices_list, image_list, location_miles_list, urls_list = Fb_market_utils.parse_html(
        html)

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
    urls_clean = Fb_market_utils.clean_urls(urls_list)

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

    Fb_market_utils.data_to_csv(vehicles_list, location)

# End browsing session
browser.quit()


Fb_market_utils.csv_to_db()
