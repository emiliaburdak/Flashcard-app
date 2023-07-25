from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import FlashCard, User, Deck
from . import db
import datetime

body = Blueprint('body', __name__)


@body.route('/')
@body.route('/home')
@login_required
def home():
    all_decks_tuples = Deck.query.with_entities(Deck.deck_name).all()
    all_decks_names = [deck_name[0] for deck_name in all_decks_tuples]

    # all_decks_tuples = [("Talia 1",), ("Talia 2",), ("Talia3,)]
    return render_template('home.html', user=current_user, decks_names=all_decks_names)


def find_all_decks_names():
    all_existing_decks_tuples = Deck.query.with_entities(Deck.deck_name).all()
    all_existing_decks_names = [deck_name[0] for deck_name in all_existing_decks_tuples]
    return all_existing_decks_names


def find_deck_id_from_existing_deck(select_existing_deck, user):
    find_selected_deck_object = list(filter(lambda x: x.deck_name == select_existing_deck, user.decks))
    deck_id = find_selected_deck_object[0].id
    return deck_id


def find_deck_id_from_create_new_deck(create_new_deck, language, user):
    check_if_matching_names = list(filter(lambda x: x.deck_name == create_new_deck, user.decks))
    if check_if_matching_names:
        deck_id = check_if_matching_names[0].id
        flash('Your new deck name already exist - the flashcard has been assigned to the existing deck')
        return deck_id
    else:
        new_deck = Deck(deck_name=create_new_deck, author_id=user.id, language=language,
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


@body.route('/add-flashcard', methods=['GET', 'POST'])
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

        valid_input, message, flash_category = check_if_input_is_valid(back_name, front_name, language, create_new_deck, select_existing_deck)
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
    current_flashcard_object = FlashCard.query.filter_by(id=flashcard_id).first()

    deck_id = current_flashcard_object.deck_id
    deck_object = Deck.query.filter_by(id=deck_id).first()
    deck_name = deck_object.deck_name

    new_strength = request.form.get('strength')
    if new_strength == 'hard':
        current_flashcard_object.strength = 1
    elif new_strength == 'medium_hard':
        current_flashcard_object.strength = 5
    elif new_strength == 'ok':
        current_flashcard_object.strength = 10
    elif new_strength == 'easy':
        current_flashcard_object.strength *= 60 * 24 * 2

    current_flashcard_object.last_day_review_at = datetime.datetime.utcnow
    current_flashcard_object.next_review_at = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=current_flashcard_object.strength)

    db.session.commit()
    return redirect(url_for('body.display_flashcard', deck_name=deck_name))


@body.route('/display_flashcard/<deck_name>', methods=["GET", "POST"])
def display_flashcard(deck_name):
    deck_object = Deck.query.filter_by(deck_name=deck_name).first()
    if not deck_object:
        flash('No such deck')
        return redirect(url_for('body.home'))

    deck_id = deck_object.id
    user_id = deck_object.author_id

    last_seen_flashcard_id = deck_object.last_seen_flashcard_id
    if last_seen_flashcard_id is None:
        # jesli nie były przeglądane fiszki i nie ma żadnej kartki w decku
        if not deck_object.flashcards[0].id:
            flash('This deck is empty')
            return redirect(url_for('body.home'))
        next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                                FlashCard.next_review_at <= datetime.datetime.utcnow()).first()
    else:
        # kolejna fiszka musi należeć do tej talii, tam gdzie skończyliśmy i tylko z tych co są do powtórki
        next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                                FlashCard.id > last_seen_flashcard_id,
                                                FlashCard.next_review_at <= datetime.datetime.utcnow()).first()

    if next_flashcard is None:
        # jeśli skończyły się w decku fiszki to zacznij od początku te do powtórki
        next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                                FlashCard.next_review_at <= datetime.datetime.utcnow()).first()

        if next_flashcard is None:
            flash('This deck is empty')
            return redirect(url_for('body.home'))

    next_flashcard_id = next_flashcard.id
    deck_object.last_seen_flashcard_id = next_flashcard_id
    db.session.commit()

    return render_template('display_flashcard.html', user_id=user_id, user=current_user, flashcard=next_flashcard,
                           deck_name=deck_name)


@body.route('/display')
def display():
    all_flashcards = FlashCard.query.all()
    return render_template('check.html', all_flashcards=all_flashcards, user=current_user)
