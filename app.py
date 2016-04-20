from _config import DATABASE_PATH
from db import db
from flask import Flask
import os
from models import User, Feed
from views import notifier


def create_app():
    app = Flask(__name__)
    app.config.from_object('_config')
    app.debug=True
    db.init_app(app)
    app.register_blueprint(notifier, url_prefix='')
    return app

def create_database(app):
    with app.app_context():
        db.create_all()
    user = User()
    user.email = "noamoss@gmail.com"
    user.password = "12345"
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    if not os.path.isfile(DATABASE_PATH):
      create_database(app)
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=2525)