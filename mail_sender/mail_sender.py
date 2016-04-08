#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import logging.handlers
import traceback
import sendgrid
from flask import Flask, render_template
from db import db
from models import User, Feed
from feeds import parse_feeds, relevant_feeds
from _config import SENDGRID_KEY



LOG_FILENAME = 'mail_sender.log'
NOTIFIER_MAIL_ADDRESS = "notifier@hasadna.org.il"
MAIL_SUBJECT = "עדכוני המידע הציבורי הפתוח שביקשת, מהמזכיר"

# Set up a specific logger with our desired output level
LOGGER = logging.getLogger('mail_sender_log')
LOGGER.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=10000, backupCount=5)

LOGGER.addHandler(handler)

def format_mail(feeds):
    pass

def build_mail(user):
    mail = sendgrid.Mail()
    mail.add_to(user.email)
    mail.set_from(NOTIFIER_MAIL_ADDRESS)
    mail.set_subject(MAIL_SUBJECT)

    feeds = parse_feeds(relevant_feeds(user.id))
#   last_update = feeds[0][3]
#
#   if  user.last_update is not None:
#   feeds = [feed for feed in feeds if feed[3] > user.last_update]
    if not feeds:
        return None

    mail.set_html(render_template('email.html', feeds=feeds))

    # update the update of the last_feed we sent
#   user.last_update = last_update
    db.session.commit()

    return mail


def main():
    app = Flask(__name__)
    app.config.from_object('_config')
    db.init_app(app)
    with app.app_context():

        LOGGER.debug("starting mail_sender")
        client = sendgrid.SendGridClient(SENDGRID_KEY)
        for user in User.query:
            mail = build_mail(user)
            if mail is not None:
                LOGGER.debug("sending mail to %s" %(user.email, ))
                client.send(mail)


        LOGGER.debug("stoping mail_sender")


if '__main__' == __name__:
    try:
        main()
    except:
        exception = traceback.format_exc()
        LOGGER.error(exception)
