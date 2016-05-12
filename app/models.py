# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, PickleType, ForeignKey

from _config import BITLY_USER, BITLY_KEY
from bitlyapi import bitlyapi
from db import db
from _config import sharing_services

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
    bitly = db.Column(String)

    def __init__(self, user_id, name, url, project):
        bitlyconnection = bitlyapi.Connection(BITLY_USER,BITLY_KEY)
        self.user_id = user_id
        self.name = name
        self.url = url
        self.bitly = bitlyconnection.shorten(url)['url']
        self.project=project

    def __repr__(self):
        return '<user: %s, url %s, project %s>' % (self.user_id, self.url, self.project)

class SharedItem(db.Model):
    __tablename__ = 'shared_items'
    id = db.Column(Integer, primary_key=True)
    full_url = db.Column(String, nullable=False)
    bitly = db.Column(String, nullable=False)
    shares_count = db.Column(Integer)
    feed_title= db.Column(String)
    project= db.Column(String,nullable=False)
    service_share_counter = db.Column(PickleType)

    def __init__(self, full_url, bitly, shares_count,feed_title,project):
        self.full_url=full_url
        self.bitly = bitly
        self.shares_count = 1
        self.feed_title = feed_title
        self.project = project
        sharing_services_list = list(sharing_services.keys())
        self.service_share_counter=dict.fromkeys(sharing_services_list,0)

    def add_share(self):
        self.shares_count+=1
