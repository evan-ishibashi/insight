"""
This file scrapes the html from lkq car
listings. It iterates through a list of cities, grabs the info from each
respective page, and exports the cleaned data into csv file. It then inserts
the data from those CSVs into my PSQL DB.
"""

from lkq_utils import Lkq_insight as Lkq

for location in Lkq.locations:

    browser = Lkq.create_browser('honda insight',location)