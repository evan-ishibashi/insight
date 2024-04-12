import os

from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Listing
from flask_cors import CORS, cross_origin

from datetime import date, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///insight')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

connect_db(app)

YESTERDAY = date.today() + timedelta(days=-1)

print(app.config['SQLALCHEMY_DATABASE_URI'])

@app.get('/wakeup')
def wakeup():
    """Pokes the server to spin up
    """

    return "waking up"

@app.get('/listings/all')
def get_all_listings():
    """Returns list of listings.

    Can take a 'q' param in querystring to search for listing.
    """
    search = request.args.get('q')

    if not search:
        listings = Listing.query.all()
    else:
        listings = Listing.query.filter(
            Listing.name.ilike(f"%{search}%")).all()

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get('/listings/fb')
def get_all_fb_listings():
    """Returns list of listings from source fb.

    Can take a 'q' param in querystring to search for listing.
    """
    search = request.args.get('q')

    if not search:
        listings = Listing.query.filter(Listing.date>=YESTERDAY).filter(Listing.site=='fb').all()
    else:
        listings = Listing.query.filter(Listing.date>=YESTERDAY).filter(
            Listing.title.ilike(f"%{search}%")).all()

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get('/listings/fb/1g')
def get_all_fb_listings_1g_only():
    """Returns list of listings from source fb.

    Can take a 'q' param in querystring to search for listing.
    """
    search = request.args.get('q')

    if not search:
        listings = Listing.query.distinct(
            Listing.url).filter(Listing.date>=YESTERDAY).filter(
            Listing.site=='fb').filter(Listing.first_gen).all()
    else:
        listings = Listing.query.distinct(
            Listing.url).filter(Listing.date>=YESTERDAY).filter(
            Listing.title.ilike(f"%{search}%")).filter(Listing.first_gen).all()

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get('/listings/offerup')
def get_all_offerup_listings():
    """Returns list of listings from source offerup.

    Can take a 'q' param in querystring to search for listing.
    """
    search = request.args.get('q')

    if not search:
        listings = Listing.query.filter(Listing.date==date.today()).filter(Listing.site=='offerup').all()
    else:
        listings = Listing.query.filter(Listing.date==date.today()).filter(
            Listing.title.ilike(f"%{search}%")).all()

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get('/listings/offerup/1g')
def get_all_offerup_listings_1g_only():
    """Returns list of listings from source offerup.

    Can take a 'q' param in querystring to search for listing.
    """
    search = request.args.get('q')

    if not search:
        listings = Listing.query.distinct(
            Listing.url).filter(Listing.date>=YESTERDAY).filter(
            Listing.site=='offerup').filter(Listing.first_gen).all()
    else:
        listings = Listing.query.distinct(
            Listing.url).filter(Listing.date>=YESTERDAY).filter(
            Listing.title.ilike(f"%{search}%")).filter(Listing.first_gen).all()

    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)

@app.get('/listings/data')
def get_listing_data():
    """Returns list of listings for data visualization.

    """

    listings = Listing.query.distinct(
            Listing.url).all()

    # listings = Listing.query.distinct(
    #         Listing.url).filter(Listing.first_gen).filter(
    #         Listing.mileage > 0).filter(Listing.price > 1).order_by(Listing.date.desc()).all()


    serialized = [listing.serialize() for listing in listings]

    return jsonify(listings=serialized)