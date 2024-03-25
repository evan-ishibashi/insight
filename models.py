from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)

class Listing(db.Model):
    """Honda Insight Listing"""

    __tablename__ = "listings"

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
        )

    date = db.Column(
        db.DateTime,
        nullable=False
    )

    title = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Integer,
        nullable=False,
    )

    city = db.Column(
        db.String(50),
        nullable=False
    )

    state = db.Column(
        db.String(2),
        nullable=False
    )

    mileage = db.Column(
        db.Integer,
        nullable=False
    )

    url = db.Column(
        db.String(),
        nullable=False
    )

    image = db.Column(
        db.String(),
        nullable=False
    )

    insight = db.Column(
        db.Boolean,
        nullable=False
    )

    first_gen = db.Column(
        db.Boolean,
        nullable=False
    )

    parts = db.Column(
        db.Boolean,
        nullable=False
    )

    source = db.Column(
        db.String(15),
        nullable=False
    )




