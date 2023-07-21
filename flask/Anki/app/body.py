from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import FlashCard, User, Deck, UserProgress
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
            if select_existing_deck and not create_new_deck:
                find_selected_deck_object = list(filter(lambda x: x.deck_name == select_existing_deck, user.decks))
                deck_id = find_selected_deck_object[0].id

            elif create_new_deck and not select_existing_deck:

                check_if_matching_names = list(filter(lambda x: x.deck_name == create_new_deck, user.decks))
                if check_if_matching_names:
                    deck_id = check_if_matching_names[0].id
                    flash('Your new deck name already exist - the flashcard has been assigned to the existing deck')
                else:
                    new_deck = Deck(deck_name=create_new_deck, author_id=user.id, language=language,
                                    last_seen_flashcard_id=None)
                    db.session.add(new_deck)
                    db.session.flush()
                    deck_id = new_deck.id

            # te dwa warunki daj wyżej dla bardziej czytelnego kodu
            elif create_new_deck and select_existing_deck:
                flash('Please add flashcard to the one of the existing decks or add to new deck', category='error')
                return redirect(url_for('body.add_flashcard'))

            else:
                flash('Select deck from existing decks or create new deck', category='error')
                return redirect(url_for('body.add_flashcard'))

            new_flashcard = FlashCard(back_name=back_name, front_name=front_name, sentence=sentence, deck_id=deck_id)
            db.session.add(new_flashcard)
            db.session.commit()
            flash('The flashcard has been created!', category='success')

    return render_template('new_flashcard.html', user=current_user, existing_decks=all_existing_decks_names)


@body.route('/update_flashcard/flashcard_id', methods=['GET', 'POST'])
@login_required
def update_flashcard(flashcard_id):
    current_flashcard_object = FlashCard.query.filter_by(flashcard_id=flashcard_id).first()

    progress = request.form.get('progress')
    if progress == 'hard':
        current_flashcard_object.strength = 1
    elif progress == 'so so':
        current_flashcard_object.strength = 2
    elif progress == 'easy':
        current_flashcard_object.strength = 3

    current_flashcard_object.strength = min(2.5, max(1.3, current_flashcard_object.strength))
    current_flashcard_object.last_day_review_at = datetime.datetime.utcnow
    current_flashcard_object.next_review_at = datetime.datetime.utcnow() + datetime.timedelta(
        days=current_flashcard_object.strength)


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
        if not deck_object.flaschcards[0].id:
            flash('This deck is empty')
            return redirect(url_for('body.home'))
        next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                                FlashCard.next_review_at <= datetime.datetime.utcnow()).first()
        next_flashcard_id = next_flashcard.id
    else:
        # kolejna fiszka musi należeć do tej talii, tam gdzie skończyliśmy i tylko z tych co są do powtórki
        next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                                FlashCard.id > last_seen_flashcard_id,
                                                FlashCard.next_review_at <= datetime.datetime.utcnow()).first()
        next_flashcard_id = next_flashcard.id

    if next_flashcard_id is None:
        # jeśli skończyły się w decku fiszki to zacznij od początku te do powtórki
        next_flashcard = FlashCard.query.filter(FlashCard.deck_id == deck_id,
                                                FlashCard.next_review_at <= datetime.datetime.utcnow()).first()
        next_flashcard_id = next_flashcard.id

    deck_object.last_seen_flashcard_id = next_flashcard_id
    db.session.commit()

    return render_template('display_flashcard.html', user_id=user_id, user=current_user, flashcard=next_flashcard_id,
                           deck_name=deck_name)


@body.route('/display')
def display():
    all_flashcards = FlashCard.query.all()
    return render_template('check.html', all_flashcards=all_flashcards, user=current_user)
