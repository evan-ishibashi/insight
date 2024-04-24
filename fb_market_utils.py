from bs4 import BeautifulSoup as soup
import re
from datetime import date
from state_name_to_abbr import name_to_abbreviation
from csv import DictReader
from app import db
from models import Listing
import ast
import os
from dotenv import load_dotenv
import pandas as pd

# Import create_engine from SQLAlchemy
from sqlalchemy import create_engine

class Fb_market_utils():
    """Class for scraping FB Marketplace"""

    def parse_html(html):
        """parses html into titles, prices, locations/mileage, images, urls"""
        #create BS object from HTML
        market_soup = soup(html, "html.parser")

        # Extract all the info, put into lists
        titles_div = market_soup.find_all('span', class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6")
        titles_list = [title.text.strip() for title in titles_div]
        titles_list.pop(0)
        titles_list.pop(0)

        prices_div = market_soup.find_all('span', class_="x193iq5w xeuugli x13faqbe x1vvkbs xlh3980 xvmahel x1n0sxbx x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x3x7a5m x1lkfr7t x1lbecb7 x1s688f xzsf02u")
        prices_list = [price.text.strip() for price in prices_div]

        location_miles_div = market_soup.find_all('span', class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft")
        location_miles_list = [mile.text.strip() for mile in location_miles_div]

        image_elems = market_soup.find_all('img', class_= "xt7dq6l xl1xv1r x6ikm8r x10wlt62 xh8yej3")
        image_list = [image.get('src') for image in image_elems]

        urls_elems = market_soup.find_all('a', class_= "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv")
        urls_list = [url.get('href') for url in urls_elems]

        print("titles length", len(titles_list))
        print("image_list length", len(image_list))
        print("miles_list", len(location_miles_list))
        print("urls_list", len(urls_list))

        return ( titles_list, prices_list, image_list, location_miles_list, urls_list )

    def append_locations_mileage(locations_mileage, CITY, STATE_ABBR):
        """Locations and Mileage data are lumped together when scraping from
        FB marketplace. This method ensures that both Locations and mileage
        lengths are equal by appending filler mileage or location"""

        # pattern for City, State (ex: Los Angeles, CA)
        location_pattern = re.compile(r"[a-zA-Z -']+[,]\s[A-Z]")
        # pattern for miles (ex: 100K miles)
        miles_pattern = re.compile(r'([0-9.]+)[K]? miles')
        # regex pattern for the item after the last valid piece of mileage data.
        login_or_sign = re.compile(r'Log in or sign up for Facebook')

        # initialize empty list
        locations_mileage_appended = []

        #iterate through the original mileage entries
        for item in locations_mileage:

            # Current item is location, previous item is location (2 locations in a row)
            if location_pattern.match(item) and len(locations_mileage_appended) >= 1 and location_pattern.match(locations_mileage_appended[-1]):
                locations_mileage_appended.append('0K miles')
                locations_mileage_appended.append(item)

            # Current item is empty string, Previous item is location (Miles is empty string)
            elif len(item) == 0 and location_pattern.match(locations_mileage_appended[-1]) and len(locations_mileage_appended) >=1:
                locations_mileage_appended.append('0K miles')

            # Previous item is miles, and current item is miles (Missing Location)
            elif miles_pattern.match(item) and len(locations_mileage_appended) >= 1 and miles_pattern.match(locations_mileage_appended[-1]):
                locations_mileage_appended.append(f'{CITY}, {STATE_ABBR}')
                locations_mileage_appended.append(item)

            # Previous item is location, and current item does not match (2 locations in a row)
            elif len(locations_mileage_appended) >= 1 and location_pattern.match(locations_mileage_appended[-1]) and miles_pattern.match(item) == None:
                locations_mileage_appended.append('0K miles')

            # Last listing does not have mileage, so append 0K
            elif len(locations_mileage_appended) >= 1 and login_or_sign.match(item) and location_pattern.match(locations_mileage_appended[-1]):
                locations_mileage_appended.append('0k miles')

            # if all looks good, just append the item.
            else:
                locations_mileage_appended.append(item)

        print("prices list", len(locations_mileage_appended))
        return locations_mileage_appended

    def separate_clean_locations_mileage(locations_mileage_appended):
        """Cleans and separates Location and Mileage data, handling edge
        cases"""

        # regex pattern for mileage. Ex: 100K miles
        miles_pattern_miles = r'([0-9.]+)[K]? miles'

        # regex pattern for mileage in km. Ex: 100K km
        miles_pattern_km = r'(\d+)K km'

        # regex pattern for location. Ex: Los Angeles, CA
        location_pattern = r'[a-zA-Z ]+[,]\s[A-Z][A-Z]'

        # regex pattern for a full city / state. Ex: Seattle, Washington
        full_state_pattern_one = r'[a-zA-Z ]+[,]\s[A-Z][a-z]+'
        full_state_pattern_two = r'[a-zA-Z ]+[,]\s[A-Z][a-z]+\s[A-Z][a-z]+'


        mileage_clean = []
        locations_clean =[]

        for item in locations_mileage_appended:

            match_miles_km = re.search(miles_pattern_km, item)

            match_mileage_miles = re.search(miles_pattern_miles, item)

            match_location = re.search(location_pattern, item)

            match_full_state_one = re.search(full_state_pattern_one, item)

            match_full_state_two = re.search(full_state_pattern_two, item)

            if match_miles_km or match_mileage_miles or match_location or match_full_state_one or match_full_state_two:
                if match_miles_km:
                    mileage_clean.append(int(match_miles_km.group(1)) *1000)

                if match_mileage_miles:
                    mileage_clean.append(int(float(match_mileage_miles.group(1))) *1000)

                if match_location:
                    locations_clean.append(item)

                if match_full_state_one or match_full_state_two:
                    full_state = item.split(', ')[1]
                    locations_clean.append(name_to_abbreviation[full_state])

            else:
                print('NON-MATCHING MILES/LOCATION',item)

        print("locations_clean length",len(locations_clean))
        print("miles_clean length",len(mileage_clean))

        if len(locations_clean) != len(mileage_clean):
            print("Locations list length does not match mileage list length")
            print()

        print("successfully cleaned and split locations / mileage")
        return (locations_clean, mileage_clean)

    def clean_prices(prices_list):
        """Cleans Price Data, returns list of clean prices"""

        # Make Prices into Integer
        prices_clean = []

        for price in prices_list:
            if price == 'Free':
                prices_clean.append(0)
            elif price == "·":
                prices_clean.append(0)
            elif price == "$12,345":
                prices_clean.append(0)
            else:
                prices_clean.append(int(re.sub(r'[₹,A-Z,a-z,$,.]','', price)))

        print("Successfully Cleaned Prices")
        return prices_clean

    def clean_urls(url_list):
        """Appends facebook base url to listing url. Returns cleaned url list"""

        urls_clean = []

        for url in url_list:
            urls_clean.append('https://www.facebook.com' + url)

        print("successfully cleaned urls")
        return urls_clean

    def organize_data(titles_list, locations_clean, mileage_clean, prices_clean,
                      urls_clean, image_list):
        # add all values to a list of dictionaries

        vehicles_list = []

        for i, item in enumerate(titles_list):
            cars_dict = {}
            first_gen = False
            insight = False
            parts = False

            year = 0
            year_pattern = r'[0-9]{4}'
            year_match = re.search(year_pattern,titles_list[i])
            first_gen_years = [2000, 2001, 2002, 2003, 2004, 2005, 2006]
            parts_list = ["part", "wheel", "mirror", "door", "piece"]

            #Checks for year
            if year_match:
                year = int(year_match[0])

            #Checks if insight is actually in the title
            if "insight" in titles_list[i].lower():
                insight = True

            #Checks if any cars are 2000 - 2006
            if year_match:
                if any(x == int(year_match[0]) for x in first_gen_years) and insight:
                    first_gen = True

            #Checks if car listing is for parts
            if any(x == parts_list for x in titles_list[i].lower()):
                parts = True


            #Splits up the City and State from location
            city = locations_clean[i].split(', ')[0]
            state = locations_clean[i].split(', ')[-1]



            # Map out key value pairs
            cars_dict["date"] = date.today()
            cars_dict["title"] = titles_list[i]
            cars_dict["price"] = prices_clean[i]
            cars_dict["city"] = city
            cars_dict["state"] = state
            cars_dict["mileage"] = mileage_clean[i]
            cars_dict["url"] = urls_clean[i]
            cars_dict["image"] = image_list[i]
            cars_dict["insight"] = insight
            cars_dict["first_gen"] = first_gen
            cars_dict["parts"] = parts
            cars_dict["site"] = "fb"
            cars_dict["year"] = year
            vehicles_list.append(cars_dict)

        return vehicles_list

    def data_to_csv(vehicles_list, location):
        vehicles_df = pd.DataFrame(vehicles_list)


        filtered_df = vehicles_df[vehicles_df['insight'] == True]


        csv_file_path = f'/Users/evanishibashi/Projects/insight/csv/fb/{date.today()}/{location}.csv'

        filtered_df.to_csv(csv_file_path, index=False)

    def csv_to_db():
        # Load environment variables from .env file
        load_dotenv()

        # Use the DATABASE_URL environment variable
        db_url = os.environ.get('DATABASE_URL')
        engine = create_engine(db_url)


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

                with engine.connect() as conn:
                    conn.execute(Listing.__table__.insert(), clean_listings)
                    conn.commit()

        db.session.commit()