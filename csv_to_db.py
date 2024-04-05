"""Seed database with sample data from CSV Files."""

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

offerup = f'../csv/offerup'

for location_csv in os.listdir(offerup):
    full_file_path = os.path.join(offerup,location_csv)

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