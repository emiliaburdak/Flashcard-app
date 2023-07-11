from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import FlashCard, User
from . import db

body = Blueprint('body', __name__)


@body.route('/')
@body.route('/home')
@login_required
def home():
    decks_tuples = FlashCard.query.with_entities(FlashCard.deck).distinct().all()
    # decks_tuples = [("Talia 1",), ("Talia 2",), ("Talia3,)]
    decks = [deck_name[0] for deck_name in decks_tuples]
    # decks = [Talia1, Talia2, Talia3]

    # all_flashcards = FlashCard.query.all()
    # decks = {flashcard.deck for flashcard in all_flashcards}

    return render_template('home.html', user=current_user, decks=decks)

@body.route('/add-flashcard', methods=['GET', 'POST'])
@login_required
def add_flashcard():
    if request.method == 'POST':
        back_name = request.form.get('back-name')
        front_name = request.form.get('front-name')
        language = request.form.get('language')
        deck = request.form.get('flashcard-deck')
        sentence = request.form.get('example-sentence')
        if len(back_name) < 1 or len(front_name) < 1:
            flash('Word is too short!')
        else:
            new_flashcard = FlashCard(back_name=back_name, front_name=front_name, language=language, deck=deck,
                                      sentence=sentence)
            db.session.add(new_flashcard)
            db.session.commit()

    return render_template('new_flashcard.html', user=current_user)


@body.route('/deck/<deck>')
def deck(deck):
    flashcards = FlashCard.query.filter_by(deck=deck).all()
    return render_template('deck.html', deck=deck, flashcards=flashcards, user=current_user)

@body.route('/display')
def display():
    all_flashcards = FlashCard.query.all()
    return render_template('check.html', all_flashcards=all_flashcards, user=current_user)
