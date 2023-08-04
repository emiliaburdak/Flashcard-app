from flask import Blueprint, render_template, request, redirect, url_for, flash, Flask, Response
from flask_login import login_required, current_user
from .models import FlashCard, User, Deck
from . import db
import datetime
from gtts import gTTS
import os
import tempfile


body = Blueprint('body', __name__)


def find_all_decks_names():
    # all_existing_decks_tuples = [("Talia 1",), ("Talia 2",), ("Talia3,)]
    all_existing_decks_tuples = Deck.query.with_entities(Deck.deck_name).all()
    all_existing_decks_names = [deck_name[0] for deck_name in all_existing_decks_tuples]
    return all_existing_decks_names


def find_deck_id_from_existing_deck(deck_name, user):
    find_selected_deck_object = list(filter(lambda x: x.deck_name == deck_name, user.decks))
    deck_id = find_selected_deck_object[0].id
    return deck_id


def find_deck_id_from_create_new_deck(created_new_deck_name, language, user):
    check_if_matching_names = list(filter(lambda x: x.deck_name == created_new_deck_name, user.decks))
    if check_if_matching_names:
        deck_id = check_if_matching_names[0].id
        flash('Your new deck name already exist - the flashcard has been assigned to the existing deck')
        return deck_id
    else:
        new_deck = Deck(deck_name=created_new_deck_name, author_id=user.id, language=language,
                        last_seen_flashcard_id=None)
        db.session.add(new_deck)
        db.session.flush()
        deck_id = new_deck.id
        return deck_id


def check_if_input_is_valid(back_name, front_name, language, create_new_deck, select_existing_deck):
    if not back_name or not front_name or not language:
        return False, 'Please completed all required fields', 'error'

    if len(back_name) < 1 or len(front_name) < 1:
        return False, 'Word must be at least 1 character long', 'error'

    if create_new_deck and select_existing_deck:
        return False, 'Please add flashcard to the one of the existing decks or add to new deck', 'error'

    if not create_new_deck and not select_existing_deck:
        return False, 'Please select deck from existing decks or create new deck', 'error'

    return True, None, None


def create_new_flashcard(back_name, front_name, deck_id, sentence):
    new_flashcard = FlashCard(back_name=back_name, front_name=front_name, sentence=sentence, deck_id=deck_id,
                              strength=1, last_day_reviewed_at=datetime.datetime.utcnow(),
                              next_review_at=datetime.datetime.utcnow())
    db.session.add(new_flashcard)
    db.session.commit()
    flash('The flashcard has been created!', category='success')
    return new_flashcard


def find_current_flashcard(flashcard_id):
    current_flashcard_object = FlashCard.query.filter_by(id=flashcard_id).first()
    return current_flashcard_object


def find_current_deck_name(flashcard_object):
    deck_id = flashcard_object.deck_id
    deck_object = Deck.query.filter_by(id=deck_id).first()
    deck_name = deck_object.deck_name
    return deck_name


def update_flashcard_strength(current_flashcard_object, new_strength):
    day_in_minutes = 60 * 24

    if new_strength == 'hard':
        current_flashcard_object.strength = 1
    elif new_strength == 'medium_hard':
        current_flashcard_object.strength = 5
    elif new_strength == 'ok':
        current_flashcard_object.strength = 10
    elif new_strength == 'easy':
        current_flashcard_object.strength *= day_in_minutes * 2
    return current_flashcard_object


def unreviewed_flashcard_from_beginning(deck_id):
    next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                            FlashCard.next_review_at <= datetime.datetime.utcnow()).first()
    return next_flashcard


def unreviewed_flashcard(deck_id, last_seen_flashcard_id,):
    next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                            FlashCard.id > last_seen_flashcard_id,
                                            FlashCard.next_review_at <= datetime.datetime.utcnow()).first()
    return next_flashcard


def update_last_seen_flashcard(deck_object, next_flashcard):
    next_flashcard_id = next_flashcard.id
    deck_object.last_seen_flashcard_id = next_flashcard_id
    db.session.commit()


def find_deck_object_by_deck_name(deck_name):
    deck_object = Deck.query.filter_by(deck_name=deck_name).first()
    return deck_object


def all_flashcards_to_review_now(deck_id):
    unreviewed_flashcards = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                            FlashCard.next_review_at <= datetime.datetime.utcnow()).all()
    return unreviewed_flashcards


def daily_rating(deck_name):
    deck_id = find_deck_id_from_existing_deck(deck_name, current_user)
    flashcards_to_review = all_flashcards_to_review_now(deck_id)
    amount_flashcards_to_review = len(flashcards_to_review)
    return amount_flashcards_to_review


@body.route('/')
@body.route('/home')
@login_required
def home():
    all_decks_names = find_all_decks_names()
    all_decks_daily_rating = {deck_name: daily_rating(deck_name) for deck_name in all_decks_names}
    return render_template('home.html', user=current_user, decks=all_decks_daily_rating)


@body.route('/add_flashcard', methods=['GET', 'POST'])
@login_required
def add_flashcard():
    all_existing_decks_names = find_all_decks_names()

    if request.method == 'POST':
        back_name = request.form.get('back-name')
        front_name = request.form.get('front-name')
        language = request.form.get('language')
        sentence = request.form.get('example-sentence')
        select_existing_deck = request.form.get('existing-deck')
        create_new_deck = request.form.get('new-deck')
        user = current_user

        valid_input, message, flash_category = check_if_input_is_valid(back_name, front_name, language, create_new_deck,
                                                                       select_existing_deck)
        if not valid_input:
            flash(message, category=flash_category)
            return redirect(url_for('body.add_flashcard'))

        # Depending on chosen field find deck_id to create_new_flashcard
        else:
            if select_existing_deck and not create_new_deck:
                deck_id = find_deck_id_from_existing_deck(select_existing_deck, user)
            else:
                deck_id = find_deck_id_from_create_new_deck(create_new_deck, language, user)

        create_new_flashcard(back_name, front_name, deck_id, sentence)

    return render_template('new_flashcard.html', user=current_user, existing_decks=all_existing_decks_names)


@body.route('/update_flashcard/<flashcard_id>', methods=['GET', 'POST'])
@login_required
def update_flashcard(flashcard_id):
    current_flashcard_object = find_current_flashcard(flashcard_id)
    deck_name = find_current_deck_name(current_flashcard_object)

    new_strength = request.form.get('strength')
    # update parameters
    current_flashcard_object = update_flashcard_strength(current_flashcard_object, new_strength)
    current_flashcard_object.last_day_review_at = datetime.datetime.utcnow
    current_flashcard_object.next_review_at = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=current_flashcard_object.strength)

    db.session.commit()
    return redirect(url_for('body.display_flashcard', deck_name=deck_name))


@body.route('/display_flashcard/<deck_name>', methods=["GET", "POST"])
@login_required
def display_flashcard(deck_name):
    deck_object = find_deck_object_by_deck_name(deck_name)
    if not deck_object:
        flash('No such deck')
        return redirect(url_for('body.home'))

    deck_id = deck_object.id
    user_id = deck_object.author_id
    last_seen_flashcard_id = deck_object.last_seen_flashcard_id

    if last_seen_flashcard_id is None:
        next_flashcard = unreviewed_flashcard_from_beginning(deck_id)
    else:
        next_flashcard = unreviewed_flashcard(deck_id, last_seen_flashcard_id)

    # if you have reach end of the deck, but you have flashcards to review from beginning of the deck.
    if next_flashcard is None:
        next_flashcard = unreviewed_flashcard_from_beginning(deck_id)
        # there is no flashcard to review in this deck
        if next_flashcard is None:
            flash('This deck is empty')
            return redirect(url_for('body.home'))

    update_last_seen_flashcard(deck_object, next_flashcard)

    return render_template('display_flashcard.html', user_id=user_id, user=current_user, flashcard=next_flashcard,
                           deck_name=deck_name)


@body.route('/render_edit_flashcard_template/<flashcard_id>', methods=['GET'])
@login_required
def render_edit_flashcard_template(flashcard_id):
    existing_decks = find_all_decks_names()
    flashcard = find_current_flashcard(flashcard_id)

    return render_template('edit_flashcard.html', user=current_user, flashcard=flashcard, existing_decks=existing_decks)


@body.route('/edit_flashcard/<flashcard_id>', methods=['POST'])
@login_required
def edit_flashcard(flashcard_id):
    flashcard = find_current_flashcard(flashcard_id)
    deck_name = find_current_deck_name(flashcard)

    if request.method == 'POST':
        new_front_name = request.form.get('new-front-name')
        new_back_name = request.form.get('new-back-name')
        new_sentence = request.form.get('new-example-sentence')
        new_selected_deck = request.form.get('new-selected-deck')

        if new_front_name:
            flashcard.front_name = new_front_name
        if new_back_name:
            flashcard.back_name = new_back_name
        if new_sentence:
            flashcard.sentence = new_sentence
        if new_selected_deck:
            new_deck_id = find_deck_object_by_deck_name(new_selected_deck)
            flashcard.deck_id = new_deck_id
            deck_name = new_selected_deck

        db.session.commit()
    return render_template('display_flashcard.html', user=current_user, flashcard=flashcard, deck_name=deck_name)


@body.route('/delete_flashcard/<flashcard_id>', methods=['GET'])
@login_required
def delete_flashcard(flashcard_id):
    flashcard = find_current_flashcard(flashcard_id)
    deck_name = find_current_deck_name(flashcard)

    db.session.delete(flashcard)
    db.session.commit()

    return redirect(url_for('body.display_flashcard', deck_name=deck_name))


@body.route('/speak/<flashcard_id>', methods=['GET'])
@login_required
def speak(flashcard_id):
    flashcard_object = find_current_flashcard(flashcard_id)
    to_speak = flashcard_object.back_name + flashcard_object.sentence
    tts = gTTS(text=to_speak, lang='es')
    with tempfile.NamedTemporaryFile(delete=True) as fp:
        tts.save(fp.name)
        fp.seek(0)
        audio = fp.read()
    return Response(audio, mimetype="audio/mp3")


@body.route('/display')
def display():
    all_flashcards = FlashCard.query.all()
    return render_template('check.html', all_flashcards=all_flashcards, user=current_user)
