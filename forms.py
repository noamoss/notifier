# projects/forms.py

from flask_wtf import Form
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
        'URL',
        validators=[DataRequired(),URL()]
        )

    name= StringField(
        'Name',
        validators=[DataRequired()]
        )