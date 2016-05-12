# -*- coding: utf-8 -*-
import os

from flask import Flask, Blueprint

from _config import DATABASE_PATH, BITLY_KEY,BITLY_USER
from app.models import User
from db import db
from views import notifier

email_sender = Blueprint('email_sender', __name__,
                         template_folder='templates',
                         static_folder='notifier.static_folder')


def create_app():
    app = Flask(__name__)
    app.config.from_object('_config')
    app.debug=True
    db.init_app(app)
    app.register_blueprint(notifier, url_prefix='')
    app.register_blueprint(email_sender)
    return app

def create_database(app):
    with app.app_context():
        db.create_all()
    user = User()
    user.email = "noamoss@gmail.com"
    user.password = "12345"
    db.session.commit()


app = create_app()