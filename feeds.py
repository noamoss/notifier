import feedparser, operator
from models import Feed
from db import db
from time import mktime
from datetime import datetime

def relevant_feeds(user_id):
    return db.session.query(Feed).filter_by(
        user_id=user_id)

def parse_feeds(feeds):
# parse and mix opentaba feeds
    results=[]

    for feed in feeds:
        feed_data = feedparser.parse(feed.url)
        for entry in feed_data.entries:
            results.append([feed.name,entry.summary,entry.link,datetime.fromtimestamp(mktime(entry.updated_parsed))])
    return sorted(results, key=operator.itemgetter(3),reverse=True)
