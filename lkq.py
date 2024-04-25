"""
This file scrapes the html from lkq car
listings. It iterates through a list of cities, grabs the info from each
respective page, and exports the cleaned data into csv file. It then inserts
the data from those CSVs into my PSQL DB.
"""

from lkq_utils import Lkq_insight as Lkq


browser = Lkq.create_browser()

for location in Lkq.locations:
    print(f'Starting process for {Lkq.locations[location]}')

    Lkq.navigate_browser(browser, 'honda insight', location)

    market_soup = Lkq.get_html(browser)

    (title_list, url_list, color_list, vin_list, section_list, stocknum_list,
     available_list, img_list) = Lkq.parse_html(market_soup)

    if len(title_list) == 0:
        print(f'No Listings for {Lkq.locations[location]}')
        if location == 'milwaukee-1256':
            browser.quit()
        continue

    clean_title_list = Lkq.clean_titles(title_list)
    clean_url_list = Lkq.clean_urls(url_list)
    clean_color_list = Lkq.clean_colors(color_list)
    clean_vin_list = Lkq.clean_vins(vin_list)
    (clean_section_list, clean_row_list,
     clean_space_list) = Lkq.clean_sections(section_list)
    clean_stocknum_list = Lkq.clean_stocknums(stocknum_list)
    clean_available_date_list = Lkq.clean_availables(available_list)
    clean_img_list = Lkq.clean_imgs(img_list)

    vehicles_list = Lkq.organize_data(Lkq.locations[location], clean_title_list, clean_url_list,
                                      clean_color_list, clean_vin_list,
                                      clean_section_list, clean_row_list,
                                      clean_space_list, clean_available_date_list,
                                      img_list)

    Lkq.data_to_csv(vehicles_list, location)

    print(f'Successfully Scraped for {Lkq.locations[location]}')

    if location == 'milwaukee-1256':
        browser.quit()


Lkq.csv_to_db()
