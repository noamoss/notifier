# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, create_engine, ForeignKey
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy
from db import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(Integer, primary_key=True)
    email = db.Column(String(120), unique=True, nullable=False)
    password = db.Column(String, nullable=False)
    last_update = db.Column(DateTime, nullable=True)
    last_feed = db.Column(DateTime, nullable=True)

    def __init__(self, email=None, password=None, last_update=None):
        self.email = email
        self.password = password
        self.last_update = last_update

    def __repr__(self):
        return '<email %s>' % (self.email)

class Feed(db.Model):
    __tablename__ = 'feeds'
    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(String, nullable=False)
    url = db.Column(String, nullable=False)
    project = db.Column(String, nullable=False)

    def __init__(self, user_id, name, url, project):
        self.user_id = user_id
        self.name = name
        self.url = url
        self.project=project

    def __repr__(self):
        return '<user: %s, url %s, project %s>' % (self.user, self.url, self.project)

Projects = {
    "opentaba":'תב"ע פתוחה'
}