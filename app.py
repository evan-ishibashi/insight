import os

from flask import Flask, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from models import db, connect_db, Listing

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///insight')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

@app.get('/listings')
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