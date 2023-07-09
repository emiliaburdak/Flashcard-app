from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

authentication = Blueprint('authentication', __name__)


@authentication.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("first_name")
        username = request.form.get("username")
        password = request.form.get("password")
        password2 = request.form.get("password2")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('Email is already in use.', category='error')
        elif username_exists:
            flash('Username is already in use.', category='error')
        elif password != password2:
            flash('Password don\'t match!', category='error')
        elif len(username) < 2:
            flash('Username is too short.', category='error')
        elif len(first_name) < 2:
            flash('First name is too short.', category='error')
            flash('Password is too short.', category='error')
        elif len(email) < 4:
            flash("Email is invalid.", category='error')
        else:
            new_user = User(email=email, username=username, password=generate_password_hash(
                password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('User created!')
            return redirect(url_for('body.home'))

    return render_template("signup.html", user=current_user)


@authentication.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('You have successfully loge in', category='success')
                login_user(user, remember=True)
                return redirect(url_for('body.home'))
            else:
                flash('Password is incorrect', category='error')
        else:
            flash('Email does not exist', category='error')

    return render_template("login.html", user=current_user)


@authentication.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("authentication.login"))
