# -*- coding: utf-8 -*-
# project_config.py
import os

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))

#SERVER_NAME = '0.0.0.0:2525'

DATABASE = 'notifier.db'

SENDGRID_KEY = "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"

WTF_CSRF_ENABLED = True
SECRET_KEY = """cb6ae6d9eb6c75 5998bf698dd83c 029d3d15d81f64 0bda227bc296d9 489cb25a00239c
d416c3a322804c ca5e76487dc759 4da4da9c259984 cd1df841615b63 b541db580800c0
c98f6d29cd8f27 df3cc061f81e27 26ff71cc749b9b 239f99479edf4e bea6dcabb40de6
eb9d217f188726 f759ef3b964f8c d28fcd1db52dd1 49f7f7d43438ff 731e1a576875b7
f4991d57651844 e3cbe6ff669540 295f1f4dc5468b 00057c6a2297a8 a15423aa1a459c
967a51c558c00d 78650fdaf6bcd3 f452a129907f01 4a9a5816cabe53 79c52c5684141f
d3683f5be06e1a e13b1a08bcf907 9e0f0bb14de4a2 d5bbddf64fc3f1 9ca989f8ab5a8a
1e7c1e6cfc12f2 ad0849bf11d2ca 0c58423c571358 c8077760e3fd25 0827561aac51bd
"""

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

# bitly keys
BITLY_KEY="R_aaf1429be2a44cb79cf81f7d5714b672"
BITLY_USER="hasadna"

# mail_sender setup
NOTIFIER_MAIL_ADDRESS = "notifier@hasadna.org.il"
MAIL_SUBJECT = "לחשושים חדשים מהציפור הקטנה, עדכוני המידע הציבורי שלך"

# social sharing services and links
sharing_services = {
    'facebook': "https://www.facebook.com/sharer/sharer.php?u={2}",
    'email':"mailto:?&subject={0}: {1}&body={2}",
    'linkedin':"https://www.linkedin.com/shareArticle?mini=true&url={2}&title={0}:{1}&summary=&source=",
    'twitter':"https://twitter.com/intent/tweet?url={2}&text={0}:{1}.via @hasadna",
    'google': "https://plus.google.com/share?url={2}",
    }

DEBUG = True

relevant_days_for_feed = 7