from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import FlashCard, User
from . import db

body = Blueprint('body', __name__)


@body.route('/')
@body.route('/home')
@login_required
def home():
    all_flashcards = FlashCard.query.all()
    return render_template('home.html', user=current_user, flashcards=all_flashcards)


@body.route('/add-flashcard', methods=['GET', 'POST'])
@login_required
def add_flashcard():
    if request.method == 'POST':
        back_name = request.form.get('back-name')
        front_name = request.form.get('front-name')
        language = request.form.get('language')
        deck = request.form.get('deck')
        sentence = request.form.get('example-sentence')
        if len(back_name) < 1 or len(front_name) < 1:
            flash('Word is too short!')
        else:
            new_flashcard = FlashCard(back_name=back_name, front_name=front_name, language=language, deck=deck,
                                      sentence=sentence)
            db.session.add(new_flashcard)
            db.session.commit()
            return render_template('new_flashcard.html', user=current_user)

    return render_template('new_flashcard.html', user=current_user)



