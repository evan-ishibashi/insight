from splinter import Browser
from datetime import date, datetime
import os
import re
import pandas as pd
from bs4 import BeautifulSoup as soup

class Lkq():
    """Class for scraping LKQ Car Parts"""

    base_url = "https://www.lkqpickyourpart.com"
    locations = {

        'huntsville-1223':'Huntsville, AL',
        'anaheim-1265':'Anaheim, CA',
        'bakersfield-1260':'Bakersfield, CA',
        'rialto-1284':'Rialto, CA',
        'chula-vista-1264':'Chula Vista, CA',
        'fontana-1285':'Fontana, CA',
        'hesperia-1292':'Hesperia, CA',
        'monrovia-1281':'Monrovia, CA',
        'oceanside-1286':'Oceanside, CA',
        'ontario-1280':'Ontario, CA',
        'riverside-1290':'Riverside, CA',
        'san-bernardino-1291':'San Bernadino, CA',
        'stanton-1268':'Stanton, CA',
        'sun-valley-1263':'Sun Valley, CA',
        'thousand-palms-1289':'Thousand Palms, CA',
        'victorville-1287':'Victorville, CA',
        'wilmington-help-yourself-1262':'Wilmington, CA',
        'aurora-1230':'Aurora, CO',
        'central-1231':'Denver, CO',
        'bradenton-1185':'Bradenton, FL',
        'clearwater-1190':'Clearwater, FL',
        'ft-lauderdale-1198':'Davie, FL',
        'daytona-1225':'Daytona Beach, FL',
        'gainesville-1224':'Gainesville, FL',
        'largo-1189':'Largo, FL',
        'orlando-1134':'Orlando, FL',
        'tampa-1180':'Tampa, FL',
        'west-palm-beach-1196':'West Palm Beach, FL',
        'fayetteville-1229':'Fayetteville, GA',
        'savannah-1163':'Savannah, GA',
        'blue-island-1582':'Blue Island, IL',
        'chicago-1581':'Chicago, IL',
        'chicago-south-1585':'Chicago South, IL',
        'rockford-1250':'Rockford, IL',
        'st-louis-1586':'Washington Park, IL',
        'fort-wayne-1254':'Fort Wayne, IN',
        'south-bend-1255':'South Bend, IN',
        'wichita-1246':'Wichita, KS',
        'baltimore-hawkins-1207':'Hawkins, MD',
        'baltimore-1205':'Baltimore, MD',
        'edgewood-1209':'Edgewood, MD',
        'holland-1346':'Holland, MI',
        'grand-rapids-1348':'Wayland, MI',
        'charlotte-1228':'Charlotte, NC',
        'raleigh-1168':'Clayton, NC',
        'durham-1142':'Durham, NC',
        'greensboro-1226':'Greensboro, NC',
        'east-nc-1227':'East NC, NC',
        'cincinnati-1253':'Cincinnati, OH',
        'dayton-1257':'Dayton, OH',
        'oklahoma-city-1245':'Oklahoma City, OK',
        'tulsa-1746':'Tulsa, OK',
        'greer-1213':'Greer, SC',
        'greenville-1212':'Greensville, SC',
        'charleston-1220':'Charleston, SC',
        'chattanooga-1217':'Chattanooga, SC',
        'memphis-1215':'Memphis, TN',
        'nashville-1218':'Nashville, TN',
        'austin-1234':'Austin, TX',
        'houston-wallisville-1236':'Houston Wallisville, TX',
        'houston-northville-1235':'Houston Northville, TX',
        'houston-sw-1239':'Houston SW, TX',
        'milwaukee-1256':'Millwaukee, WI',
    }

    def create_browser(search_term,location):
        # Set up splinter
        browser = Browser('chrome')

        # base url
        base_url = "https://www.lkqpickyourpart.com/inventory/"

        # search parameters
        split_term = search_term.split(" ")
        search = '+'.join(split_term)

        #full url
        url = f"{base_url}/inventory/{location}/?search={search}"

        # Make new directory for the day if you have not yet
        if not os.path.exists(f'/Users/evanishibashi/Projects/insight/csv/lkq/{date.today()}'):
            os.mkdir(f'/Users/evanishibashi/Projects/insight/csv/lkq/{date.today()}')

        #visit site
        browser.visit(url)

        return browser

    def get_html(browser):
        # Parse HTML
        html = browser.html

        #create BS object from HTML
        market_soup = soup(html, "html.parser")

        return market_soup

    def parse_html(market_soup):
        """parses html into titles, prices, locations/mileage, images, urls"""

        # Extract all the info, put into lists
        listing_cards = market_soup.find_all('div', class_="pypvi_details text--small")
        img_elements = market_soup.find_all('a', class_="fancybox-thumb pypvi_image")
        img_list = [element.get('href') for element in img_elements]
        div_tags = [listing.find_all("div") for listing in listing_cards]
        titles_elements = [listing.find("a") for listing in listing_cards]
        title_list = [element.text.strip() for element in titles_elements]
        url_list = [element.get('href') for element in titles_elements]
        color_list = []
        vin_list = []
        section_list =[]
        stocknum_list = []
        available_list =[]


        for groups in div_tags:
            for i, div in enumerate(groups):
                if i == 0:
                    color_list.append(div.text.strip())
                elif i == 1:
                    vin_list.append(div.text.strip())
                elif i == 2:
                    section_list.append(div.text.strip())
                elif i == 3:
                    stocknum_list.append(div.text.strip())
                elif i == 4:
                    available_list.append(div.text.strip())

        return (title_list, url_list, color_list, vin_list, section_list, stocknum_list, available_list, img_list)

    def clean_titles(title_list):
        clean_title_list = []
        for title in title_list:
            split_title = title.split('\xa0')
            cleaned = " ".join(split_title)
            clean_title_list.append(cleaned)

        return clean_title_list

    def clean_urls(url_list):
        clean_url_list = [Lkq.base_url + url for url in url_list]
        return clean_url_list

    def clean_colors(color_list):
        clean_color_list = [color.split(' ')[1] for color in color_list]
        return clean_color_list

    def clean_vins(vin_list):
        clean_vin_list = [vin.split(' ')[1] for vin in vin_list]
        return clean_vin_list

    def clean_sections(section_list):
        split = [string.split('\n                    \xa0\xa0\n                    ') for string in section_list]
        clean_section_list = []
        clean_row_list = []
        clean_space_list = []

        for group in split:
            for info in group:
                section_match = re.match(r'\Section: .*', info)
                row_match = re.match(r'Row: ', info)
                space_match = re.match(r'\Space: .*', info)
                if section_match:
                    clean_section_list.append(info.split(' ')[1])
                if row_match:
                    clean_row_list.append(info.split(' ')[1])
                if space_match:
                    clean_space_list.append(info.split(' ')[1])

        return (clean_section_list, clean_row_list, clean_space_list)

    def clean_stocknums(stocknum_list):
        clean_stocknum_list = [stocknum.split(' ')[1] for stocknum in stocknum_list]
        return clean_stocknum_list

    def clean_availables(available_list):
        date_format = '%m/%d/%Y'
        split_available_date_list = [available.split('\n')[1] for available in available_list]
        clean_available_date_list = [datetime.strptime(date_str, date_format) for date_str in split_available_date_list]


        return clean_available_date_list

    def clean_imgs(img_list):
        clean_img_list = [img.split(' ')[0] for img in img_list]
        return clean_img_list

    def organize_data(location, clean_titles, clean_url_list, clean_color_list, clean_vin_list,
                      clean_section_list, clean_row_list, clean_space_list, clean_available_date_list, img_list):
        # add all values to a list of dictionaries

        vehicles_list = []

        for i, item in enumerate(clean_titles):
            cars_dict = {}

            year = 0
            year_pattern = r'[0-9]{4}'
            year_match = re.search(year_pattern,clean_titles[i])

            #Checks for year
            if year_match:
                year = int(year_match[0])


            #Splits up the City and State from location
            split_location = Lkq.locations[location].split(', ')
            city = split_location[0]
            state = split_location[-1]



            # Map out key value pairs
            cars_dict["date"] = date.today()
            cars_dict["available"] = clean_available_date_list[i]
            cars_dict["title"] = clean_titles[i]
            cars_dict["city"] = city
            cars_dict["state"] = state
            cars_dict["color"] = clean_color_list[i]
            cars_dict["vin"] = clean_vin_list[i]
            cars_dict["section"] = clean_section_list[i]
            cars_dict["row"] = clean_row_list[i]
            cars_dict["space"] = clean_space_list[i]
            cars_dict["url"] = clean_url_list[i]
            cars_dict["image"] = img_list[i]
            cars_dict["site"] = "lkq"
            cars_dict["year"] = year
            vehicles_list.append(cars_dict)

        return vehicles_list


    def data_to_csv(vehicles_list, path):
        """Converts Dictionary of Vehicle Listings to CSV. Takes in the Dict
        of vehicles, and the desired path that you want to store your file on"""
        vehicles_df = pd.DataFrame(vehicles_list)


        csv_file_path = path

        vehicles_df.to_csv(csv_file_path, index=False)

class Lkq_insight(Lkq):
    def organize_data(location, clean_titles, clean_url_list, clean_color_list, clean_vin_list,
                      clean_section_list, clean_row_list, clean_space_list, clean_available_date_list, img_list):
        # add all values to a list of dictionaries

        vehicles_list = []

        for i, item in enumerate(clean_titles):
            cars_dict = {}
            first_gen = False

            year = 0
            year_pattern = r'[0-9]{4}'
            year_match = re.search(year_pattern,clean_titles[i])
            first_gen_years = [2000, 2001, 2002, 2003, 2004, 2005, 2006]

            #Checks for year
            if year_match:
                year = int(year_match[0])

            #Checks if any cars are 2000 - 2006
            if year_match:
                if any(x == int(year_match[0]) for x in first_gen_years):
                    first_gen = True

            #Splits up the City and State from location
            city = location.split(', ')[0]
            state = location.split(', ')[-1]



            # Map out key value pairs
            cars_dict["date"] = date.today()
            cars_dict["available"] = clean_available_date_list[i]
            cars_dict["title"] = clean_titles[i]
            cars_dict["city"] = city
            cars_dict["state"] = state
            cars_dict["color"] = clean_color_list[i]
            cars_dict["vin"] = clean_vin_list[i]
            cars_dict["section"] = clean_section_list[i]
            cars_dict["row"] = clean_row_list[i]
            cars_dict["space"] = clean_space_list[i]
            cars_dict["url"] = clean_url_list[i]
            cars_dict["image"] = img_list[i]
            cars_dict["first_gen"] = first_gen
            cars_dict["site"] = "lkq"
            cars_dict["year"] = year
            vehicles_list.append(cars_dict)

        return vehicles_list

    def data_to_csv(vehicles_list, location):
        vehicles_df = pd.DataFrame(vehicles_list)


        filtered_df = vehicles_df[vehicles_df['insight'] == True]


        csv_file_path = f'/Users/evanishibashi/Projects/insight/csv/fb/{date.today()}/{location}.csv'

        filtered_df.to_csv(csv_file_path, index=False)



