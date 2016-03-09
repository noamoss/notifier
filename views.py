# import the Flask class from the flask module
from flask import flash, redirect, render_template, \
    request, url_for, session
from functools import wraps

from db import db
from forms import RegisterForm, LoginForm, FeedForm
from sqlalchemy.exc import IntegrityError
from flask.blueprints import Blueprint
from models import User, Feed

notifier = Blueprint('notifier', __name__,
                     template_folder='templates',
                     static_folder='static')


def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('עליך להירשם ולהתחבר לאתר.')
            return redirect(url_for('login'))

    return wrap


@notifier.route('/', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(email=request.form['email']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['user_id'] = user.id
                flash('ברוכים הבאים, תהנו!')
                return redirect(url_for('notifier.feed'))
            else:
                error = 'כתובת דוא"ל או סיסמה שגויים'
        else:
            error = "שני השדות דרושים להתחברות."
    return render_template("login.html", form=form, error=error)


@notifier.route('/logout/')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash('להתראות!')
    return redirect(url_for('notifier.login'))


@notifier.route('/register/', methods=['GET', 'POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user = User(
                form.email.data,
                form.password.data,
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash("תודה שנרשמת. כעת ניתן להתחבר לאתר")
                return redirect(url_for('notifier.login'))
            except IntegrityError:
                error = 'כתובת הדוא"ל הזו כבר קיימת באתר.'
                return render_template('register.html', form=form, error=error)
    return render_template("register.html", form=form, error=error)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"תקלה בשדה %s - %s" % (
                getattr(form, field).label.text, error), 'error')


@notifier.route('/feed')
@login_required
def feed():
    error = None
    form = FeedForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_feed = Feed(
                session['user_id'],
                form.url.data,
            )

    return render_template('feed.html')
