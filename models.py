from sqlalchemy import Column, Integer, String, create_engine, ForeignKey
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy
from db import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password = db.Column(String, nullable=False)

    def __init__(self, email=None, password=None):
        self.email = email
        self.password = password

    def __repr__(self):
        return '<email %s>' % (self.email)

class Feed(db.Model):
    __tablename__ = 'feeds'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    feedxx
    url = db.Column(String, nullable=False)

    def __init(self, user_id, url):
        self.user_id = user_id
        self.url = url

    def __repr__(self):
        return '<user: %s, url %s>' % (self.user,self.url)
