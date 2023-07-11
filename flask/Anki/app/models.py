from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))


class FlashCard(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    back_name = db.Column(db.String(50))
    front_name = db.Column(db.String(50))
    sentence = db.Column(db.String(500))
    language = db.Column(db.String(50))
    deck = db.Column(db.String(50))