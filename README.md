# notifier

## Goal
Open Knowledge and Data should reach us proactivley. 
The Notifier enables users to sign up for relevant feeds (API based) and get updates when relevant data/info is published.

## Installation
1. clone me.
2. `pip install requirements.txt`
3. `python app.py`

### mail delivery setup
3. `export PYTHONPATH=<project_path>`
4. set SENDGRID_KEY, sender address and titles on _config.py
5. use `./mail_sender/mail_sender.py` to check sending 
