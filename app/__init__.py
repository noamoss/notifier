# -*- coding: utf-8 -*-
import os

from flask import Flask, render_template
from flask_wtf.csrf  import CsrfProtect
from sendgrid import Mail

from _config import DATABASE_PATH, BITLY_KEY,BITLY_USER
from app.models import User
from db import db
from views import notifier

csrf = CsrfProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object('_config')
    app.debug=True
    db.init_app(app)
    app.register_blueprint(notifier, url_prefix='')
    csrf.init_app(app)
    return app

def create_database(app):
    with app.app_context():
        db.create_all()
    db.session.commit()

app = create_app()
