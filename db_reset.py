
from csv import DictReader
from app import db
from models import Listing
from datetime import date, timedelta
import ast
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData

"""Drops both local and online DB, run pgdump in cli afterwards

"""


# Load environment variables from .env file
load_dotenv()

# Use the DATABASE_URL environment variable
db_url = os.environ.get('DATABASE_URL')
engine = create_engine(db_url)


db.drop_all()
db.create_all()

metadata = MetaData()

metadata.reflect(bind=engine)

metadata.drop_all(bind=engine)

#defined start date
start_date = date(2024, 4, 1)

# today's date
end_date = date.today()

#number of days between today and start
num_days = (end_date - start_date).days

for i in range(num_days + 1):
    current_date = start_date + timedelta(days=i)

    directory = f'../csv/fb/{current_date}'

    if os.path.exists(directory):
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

    offerup = f'../csv/offerup/{current_date}'

    if os.path.exists(offerup):

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
