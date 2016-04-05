#!/bin/env python
import logging
import logging.handlers
import traceback
import sendgrid
from flask import Flask
from db import db
from models import User, Feed


LOG_FILENAME = 'mail_sender.log'
SENDGRID_KEY = ""
NOTIFIER_MAIL_ADDRESS = "notifier@hasadna.org.il"

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

def main():
    app = Flask(__name__)
    app.config.from_object('_config')
    db.init_app(app)
    with app.app_context():

        LOGGER.debug("starting mail_sender")
        client = sendgrid.SendGridClient(SENDGRID_KEY)
        message = sendgrid.Mail()

        LOGGER.debug("stopting mail_sender")


if '__main__' == __name__:
    try:
        main()
    except:
        exception = traceback.format_exc()
        LOGGER.error(exception)
