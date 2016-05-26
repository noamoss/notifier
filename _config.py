import os

# grab the folder where this script lives
basedir = os.path.abspath(os.path.dirname(__file__))


# Instance specific config
# Override these using a local_config.py file

# Server
# SERVER_NAME = '0.0.0.0:2525'

# Database
DATABASE = ''

# SendGrid key
SENDGRID_KEY = ''

# CSRF
WTF_CSRF_ENABLED = True
SECRET_KEY = ''

# Bitly key
BITLY_KEY = ''
BITLY_USER = ''

# mail_sender setup
NOTIFIER_MAIL_ADDRESS = ''
MAIL_SUBJECT = ''

# End of instance specific config

# Now import and override from local_config.py
try:
    from local_config import *
except ImportError:
    # Nothing should happen if we don't have this file locally
    # Or, you may choose to throw here an exception
    pass


# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

# the database uri
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

# social sharing services and links
sharing_services = {
    'facebook': "https://www.facebook.com/sharer/sharer.php?u={2}",
    'email': "mailto:?&subject={0}: {1}&body={2}",
    'linkedin': "https://www.linkedin.com/shareArticle?mini=true&url={2}&title={0}:{1}&summary=&source=",
    'twitter': "https://twitter.com/intent/tweet?url={2}&text={0}:{1}.via @hasadna",
    'google': "https://plus.google.com/share?url={2}",
}

DEBUG = True

relevant_days_for_feed = 7
