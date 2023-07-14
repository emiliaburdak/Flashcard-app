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
    all_existing_decks_tuples = Deck.query.with_entities(Deck.deck_name).all()
    all_existing_decks_names = [deck_name[0] for deck_name in all_existing_decks_tuples]

    if request.method == 'POST':
        back_name = request.form.get('back-name')
        front_name = request.form.get('front-name')
        language = request.form.get('language')
        sentence = request.form.get('example-sentence')
        select_existing_deck = request.form.get('existing-deck')
        create_new_deck = request.form.get('new-deck')
        user = current_user

        if not back_name or not front_name or not language:
            flash('You have not completed all required fields', category='error')
            return redirect(url_for('body.add_flashcard'))

        if len(back_name) < 1 or len(front_name) < 1:
            flash('Word is too short!', category='error')
            return redirect(url_for('body.add_flashcard'))

        else:
            if select_existing_deck:
                find_selected_deck_object = list(filter(lambda x: x.deck_name == select_existing_deck, user.decks))
                deck_id = find_selected_deck_object[0].id

            elif create_new_deck:

                check_if_matching_names = list(filter(lambda x: x.deck_name == create_new_deck, user.decks))
                if check_if_matching_names:
                    deck_id = check_if_matching_names[0].id
                    flash('Your new deck name already exist - the flashcard has been assigned to the existing deck')

                else:
                    new_deck = Deck(deck_name=create_new_deck, author_id=user.id, language=language)
                    db.session.add(new_deck)
                    db.session.flush()
                    deck_id = new_deck.id

            else:
                flash('Select deck from existing decks or create new deck', category='error')
                return redirect(url_for('body.add_flashcard'))

            new_flashcard = FlashCard(back_name=back_name, front_name=front_name, sentence=sentence, deck_id=deck_id)
            db.session.add(new_flashcard)
            db.session.commit()
            flash('The flashcard has been created!', category='success')

    return render_template('new_flashcard.html', user=current_user, existing_decks=all_existing_decks_names)


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
