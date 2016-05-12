# notifier

## Goal
Open Knowledge and Data should reach us proactivley. 
The Notifier enables users to sign up for relevant feeds (API based) and get updates when relevant data/info is published.

## Installation
1. clone me.
2. `pip install requirements.txt`
3. `python app.py`

### mail delivery setup
1. `export PYTHONPATH=<project_path>`
2. set SENDGRID_KEY, sender address and titles on _config.py
3. use `./mail_sender/mail_sender.py` to check sending
4. add dictionary of social sharing netweork and links on _config.py:
'<# social sharing services and links
sharing_services = {
    'facebook': "https://www.facebook.com/sharer/sharer.php?u={2}",
    'email':"mailto:?&subject={0}: {1}&body={2}",
    'linkedin':"https://www.linkedin.com/shareArticle?mini=true&url={2}&title={0}:{1}&summary=&source=",
    'twitter':"https://twitter.com/intent/tweet?url={2}&text={0}:{1}.via @hasadna",
    'google': "https://plus.google.com/share?url={2}",
    }>'

### db initiation and migration
'<python db_migrate db init>' and/or '<python db_migrate db migrate>'