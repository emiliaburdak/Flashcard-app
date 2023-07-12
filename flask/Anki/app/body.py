from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import FlashCard, User, Deck
from . import db

body = Blueprint('body', __name__)


@body.route('/')
@body.route('/home')
@login_required
def home():
    # deck_names = list(map(lambda x: x.deck_name, user.decks))
    # all_decks = Deck.query.with_entities(FlashCard.deck).distinct().all()

    all_decks_tuples = Deck.query.with_entities(Deck.deck_name).all()
    all_decks_names = [deck_name[0] for deck_name in all_decks_tuples]

    # all_decks_tuples = [("Talia 1",), ("Talia 2",), ("Talia3,)]
    return render_template('home.html', user=current_user, decks=all_decks_names)


@body.route('/add-flashcard', methods=['GET', 'POST'])
@login_required
def add_flashcard():
    if request.method == 'POST':
        back_name = request.form.get('back-name')
        front_name = request.form.get('front-name')
        language = request.form.get('language')
        sentence = request.form.get('example-sentence')
        form_deck_name = request.form.get('flashcard-deck')
        user = current_user

        if not back_name or not front_name or not language or not sentence or not form_deck_name:
            flash('All fields are required!')
            return redirect(url_for('new_flashcard.html'))

        if len(back_name) < 1 or len(front_name) < 1:
            flash('Word is too short!')
            return redirect(url_for('new_flashcard.html'))

        else:
            decks_matching_name = list(filter(lambda x: x.deck_name == form_deck_name, user.decks))
            if decks_matching_name:
                deck_id = decks_matching_name[0].id

            else:
                new_deck = Deck(deck_name=form_deck_name, author_id=user.id, language=language)
                db.session.add(new_deck)
                db.session.flush()
                deck_id = new_deck.id

            new_flashcard = FlashCard(back_name=back_name, front_name=front_name, sentence=sentence,
                                          author_id=user.id, deck_id=deck_id)
            db.session.add(new_flashcard)
            db.session.commit()

    return render_template('new_flashcard.html', user=current_user)


@body.route('/deck/<deck>')
def deck(deck):
    deck_object = Deck.query.filter_by(deck_name=deck).first()
    if not deck_object:
        flash('No such deck')
        return redirect(url_for('home.html'))
    deck_id = deck_object.id
    flashcards = FlashCard.query.filter_by(deck_id=deck_id).all()
    return render_template('deck.html', deck=deck, flashcards=flashcards, user=current_user)


@body.route('/display')
def display():
    all_flashcards = FlashCard.query.all()
    return render_template('check.html', all_flashcards=all_flashcards, user=current_user)

