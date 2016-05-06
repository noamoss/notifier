# -*- coding: utf-8 -*-
import feedparser
import operator

from flask import session

from models import Feed
from db import db
from time import mktime
from datetime import datetime
from urllib.parse import urlparse

def relevant_feeds(user_id):
    return db.session.query(Feed).filter_by(
        user_id=user_id)


def parse_feeds(feeds):
    # parse and mix opentaba feeds
    results = []

    for feed in feeds:
        feed_data = feedparser.parse(feed.url)
        for entry in feed_data.entries:
            results.append([feed.name, entry.title, entry.summary, entry.link,
                            datetime.fromtimestamp(
                                mktime(entry.updated_parsed)).date()])
    return sorted(results, key=operator.itemgetter(4), reverse=True)


def get_project_name_by_feed(path):
    # return project name (and subclass,if relevant, by feed address)
    first_part_of_path = urlparse(path).netloc.split(".")[0]
    if "opentaba" in first_part_of_path:
        city = first_part_of_path.split("-")[1]
        return "opentaba/"+city

def relevant_feeds():
    # return relevant feeds for user
    return db.session.query(Feed).filter_by(
        user_id=session['user_id'])
