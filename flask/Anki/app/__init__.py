from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'mysecretkey'

    from .body import body
    from .authentication import authentication

    app.register_blueprint(body, url_prefix='/')
    app.register_blueprint(authentication, url_prefix='/')

    return app
