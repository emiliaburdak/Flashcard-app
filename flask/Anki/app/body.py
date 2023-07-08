from flask import Blueprint, render_template

body = Blueprint('body', __name__)


@body.route('/')
@body.route('/home')
def home():
    return render_template('home.html')
