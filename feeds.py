# -*- coding: utf-8 -*-
import operator
import urllib
import datetime
from time import mktime
from urllib.parse import urlparse
from flask import flash, url_for, redirect,session
from bs4 import BeautifulSoup
import feedparser

from _config import relevant_days_for_feed
from app.models import Feed
from db import db


def relevant_feeds(user_id):
    return db.session.query(Feed).filter_by(
        user_id=user_id)


def parse_feeds(feeds):
    # parse and mix feeds
    results = []

    for feed in feeds:
        feed_data = feedparser.parse(feed.url)
        for entry in feed_data.entries:
            try:
                published_date = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed)).date()
            except:
                published_date = "לא ידוע"
            summary = BeautifulSoup(entry.summary).get_text()
            if datetime.datetime.today().date() - published_date <= datetime.timedelta(relevant_days_for_feed):
                results.append([feed.name, entry.title, summary, urllib.parse.quote(entry.link),published_date])
    return sorted(results, key=operator.itemgetter(4), reverse=True)


def set_title_by_feed(url):
    # return tuple of porject name and specific title for new feeds
    project_name = get_project_by_feed_url(url)
    try:
        title = feedparser.parse(url).feed.title
    except:
        title=""
    return (project_name,title)

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
    elif domain_first_part == "kikar":
        return 'כיכר המדינה'
    else:
        return "לא ידוע"


def save_feed_to_db(url, name, project,user_id,relevant_feeds):
    if url not in relevant_feeds:
        title = set_title_by_feed(url)
        try:
            title = title[1].split(" ")
        except:
            pass
        a_new_feed = Feed(
            url=url,
            name=name,
            user_id=user_id,
            project=project
        )
        db.session.add(a_new_feed)
        db.session.commit()
        flash(u'ההזנה החדשה נוספה למאגר')
        return redirect(url_for('notifier.feeds_editor'))
    else:
        flash(u'את/ה כבר עוקבים אחרי מקור מידע זה')
        return redirect(url_for('notifier.feeds_editor'))

