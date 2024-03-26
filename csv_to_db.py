"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import Listing
from datetime import date
import ast

# db.drop_all()
# db.create_all()

with open(f'../csv/fb/{date.today()}.csv') as fb_listings:
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