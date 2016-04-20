# -*- coding: utf-8 -*-
# projects/forms.py
import json, feedparser
import urllib.request
from urllib.parse import urlparse
from flask_wtf import Form
from urllib.error import URLError
from wtforms import StringField, DateField, IntegerField, \
    SelectField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo, Email, URL

class RegisterForm(Form):
    email = StringField(
        'Email',
        validators=[DataRequired(), Email(), Length(min=6, max=40)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=5, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        validators=[DataRequired(),
                    EqualTo('password',
                            message='הסיסמאות אינן תואמות')]
    )


class LoginForm(Form):
    email = StringField(
        'Email',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )

class AddFeedForm(Form):
    url = StringField(
        'כתובת URL',
        validators=[DataRequired(message="יש להזין כתובת למקור המידע"),URL(message="כתובת המקור אינה תקינה")],
        )

    name= StringField(
        'שם או כותרת',
        validators=[DataRequired(message="יש להזין כותרת למקור המידע")]
        )
    def validate(self):
        rv = Form.validate(self)
        if not rv:
            return False

        url = urlparse(self.url.data).geturl()
        try:
            myjson = urllib.request.urlopen(url).read().decode('utf-8')
        except URLError:
            self.url.errors.append("כתובת לא קיימת")
            return False
        try:
            json_object = json.loads(myjson)
            return True
        except ValueError:
            pass
        try:
            myatom = feedparser.parse(url)
            if myatom.status != 200:
                self.url.errors.append('המקור שהוזן אינו בפורמט ATOM')
                return False
        except ValueError:
            self.url.errors.append('המקור שהוזן אינו בפורמט JSON או ATOM')
            return False
        return True