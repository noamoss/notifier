#!/usr/bin/env python
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
MAIL_SUBJECT = "Bla Bla"

# Set up a specific logger with our desired output level
LOGGER = logging.getLogger('maill_sender_log')
LOGGER.setLevel(logging.DEBUG)

# Add the log message handler to the logger
handler = logging.handlers.RotatingFileHandler(
              LOG_FILENAME, maxBytes=10000, backupCount=5)

LOGGER.addHandler(handler)

'''

client = sendgrid.SendGridClient("SENDGRID_APIKEY")
message = sendgrid.Mail()

message.add_to("test@sendgrid.com")
message.set_from("you@youremail.com")
message.set_subject("Sending with SendGrid is Fun")
message.set_html("and easy to do anywhere, even with Python")
 
 client.send(message)
 '''
def format_mail(feeds):
    pass

def build_mail(user):
    mail = sendgrid.Mail()
    mail.add_to(user.email)
    mail.set_from(NOTIFIER_MAIL_ADDRESS)
    mail.set_subject(MAIL_SUBJECT)

    feeds = parse_feeds(relevant_feeds(user.id))
    last_update = feeds[0][3]
    if  user.last_upadte is not None:
        feeds = [feed for feed in feeds if feed[3] > user.last_update]

    mail.set_html(render_template('email.html', feeds=feeds))

    return last_update, mail


def main():
    app = Flask(__name__)
    app.config.from_object('_config')
    db.init_app(app)
    with app.app_context():

        LOGGER.debug("starting mail_sender")
        client = sendgrid.SendGridClient(SENDGRID_KEY)
        for user in User.query:
            LOGGER.debug("sending mail to %s" %(user.email, ))
            last_update, mail = build_mail(user)
            client.send(mail)
            user.last_update = last_update
            db.session.commit()


        LOGGER.debug("stopting mail_sender")


if '__main__' == __name__:
    try:
        main()
    except:
        exception = traceback.format_exc()
        LOGGER.error(exception)
