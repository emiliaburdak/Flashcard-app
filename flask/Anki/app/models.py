from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    decks = db.relationship('Deck', backref='user', passive_deletes=True)


class FlashCard(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    back_name = db.Column(db.String(50))
    front_name = db.Column(db.String(50))
    sentence = db.Column(db.String(500))
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id', ondelete='CASCADE'), nullable=False)


class Deck(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    deck_name = db.Column(db.String(50))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    flashcards = db.relationship('FlashCard', backref='deck', passive_deletes=True)
    language = db.Column(db.String(50))


class UserProgress(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('deck.id'), nullable=False)
    last_flashcard_id = db.Column(db.Integer, db.ForeignKey('flash_card.id'), nullable=True)