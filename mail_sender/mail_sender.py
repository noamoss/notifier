#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging.handlers
import traceback
from datetime import datetime

import sendgrid
from flask import Flask, render_template

from _config import SENDGRID_KEY
from app.models import User
from db import db
from feeds import parse_feeds, relevant_feeds

LOG_FILENAME = 'mail_sender.log'
NOTIFIER_MAIL_ADDRESS = "notifier@hasadna.org.il"
MAIL_SUBJECT = "לחשושים חדשים מהציפור הקטנה, עדכוני המידע הציבורי שלך"

# Set up a specific logger with our desired output level
LOGGER = logging.getLogger('mail_sender_log')
LOGGER.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=10000, backupCount=5)

handler.setFormatter(formatter)
LOGGER.addHandler(handler)


def build_mail(user):
    mail = sendgrid.Mail()
    mail.add_to(user.email)
    mail.set_from(NOTIFIER_MAIL_ADDRESS)
    mail.set_subject(MAIL_SUBJECT)

    feeds = parse_feeds(relevant_feeds(user.id))
    if not feeds:
        return None

    last_feed = feeds[0][4]
    """
    if  user.last_feed is not None:
        feeds = [feed for feed in feeds if feed[4] > user.last_feed.date()]
    if not feeds:
        return None
    """
    try:
        last_update_date = datetime.strftime(user.last_update.date(), '%d/%m/%Y')
    except:
        last_update_date = "01/01/1980"
    mail.set_html(render_template('email.html', last_update_date=last_update_date, user=user, feeds=feeds))

    # update the update of the last_feed we sent
    user.last_feed = last_feed

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
                user.last_update = datetime.today()


        db.session.commit()
        LOGGER.debug("stoping mail_sender")


if '__main__' == __name__:
    try:
        main()
    except:
        exception = traceback.format_exc()
        LOGGER.error(exception)
