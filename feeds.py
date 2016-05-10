# -*- coding: utf-8 -*-
import operator
import urllib
from datetime import datetime
from time import mktime
from urllib.parse import urlparse

import feedparser
from flask import session

from app.models import Feed
from db import db


def relevant_feeds(user_id):
    return db.session.query(Feed).filter_by(
        user_id=user_id)


def parse_feeds(feeds):
    # parse and mix opentaba feeds
    results = []

    for feed in feeds:
        feed_data = feedparser.parse(feed.url)
        for entry in feed_data.entries:
            results.append([feed.name, entry.title, entry.summary, urllib.parse.quote(entry.link),
                            datetime.fromtimestamp(
                                mktime(entry.updated_parsed)).date()])
    return sorted(results, key=operator.itemgetter(4), reverse=True)


def set_title_by_feed(url):
    # return tuple of porject name and specific title for new feeds
    project_name = get_project_by_feed_url(url)
    try:
        moreinfo = feedparser.parse(url).feed.title
    except:
        moreinfo=None
    return (project_name,moreinfo)

def relevant_feeds(user_id=None):
    if user_id == None:
        user_id = session['user_id']
    # return relevant feeds for user
    return db.session.query(Feed).filter_by(
        user_id=user_id)

def relevant_feeds_urls():
    # return relevant feeds for user
    return [x.url for x in db.session.query(Feed.url).filter_by(
        user_id=session['user_id']).distinct()]


def get_project_by_feed_url(url):
    # return project name (and subclass,if relevant, by feed address)
    print ("HEY: ",urllib.parse.urlparse(url).netloc)
    domain_first_part = urllib.parse.urlparse(url).netloc.split(".")[0]
    if "opentaba" in domain_first_part:
        return 'תב"ע פתוחה'
    else:
        return "לא ידוע"