import os

from _config import DATABASE_PATH, BITLY_KEY, BITLY_USER
from app import app, create_app, create_database
from bitlyapi import bitlyapi
from db import db

if __name__ == '__main__':
    if not os.path.isfile(DATABASE_PATH):
        create_database(app)
    with app.app_context():
        db.create_all()

    bitlyconnection = bitlyapi.Connection(BITLY_KEY, BITLY_USER)
    app = create_app()
    app.run(host="0.0.0.0", port=2525)
