# -*- coding: utf-8 -*-
# import the Flask class from the flask module
from flask import flash, redirect, render_template, \
    request, url_for, session
from functools import wraps

from _config import basedir
from db import db
from forms import RegisterForm, LoginForm, AddFeedForm
from sqlalchemy.exc import IntegrityError
from flask.blueprints import Blueprint
from models import User, Feed, Projects
import feedparser
from feeds import parse_feeds


notifier = Blueprint('notifier', __name__,
                     template_folder='templates',
                     static_folder='static',
                     )

def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash(u'עליך להירשם ולהתחבר לאתר.')
            return redirect(url_for('notifier.login'))

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
                session['user_email'] = user.email
                flash(u'ברוכים הבאים, תהנו!')
                return redirect(url_for('notifier.feeds_editor'))
            else:
                error = 'כתובת דוא"ל או סיסמה שגויים'
        else:
            error = "שני השדות דרושים להתחברות."
    return render_template("login.html", form=form, error=error)


@notifier.route('/logout/')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)
    flash(u'להתראות!')
    return redirect(url_for('notifier.login'))


@notifier.route('/register', methods=['GET', 'POST'])
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
                flash(u'תודה שנרשמת. כעת ניתן להתחבר לאתר')
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


@notifier.route('/feeds_editor')
@login_required
def feeds_editor():
    user_email = session['user_email']
    return render_template('feeds_editor.html', user_email=user_email,
                           form=AddFeedForm(request.form),
                           feeds=relevant_feeds(),
                           parsed_feeds=parse_feeds(relevant_feeds())
                           )


@notifier.route('/addfeed/opentaba/<city>/<path:feed_url>', methods=['GET', 'POST'])
@login_required
def new_feed(feed_url, city):
    error = None
    form = AddFeedForm(request.form)

    try:
        feed_title = city+ ": "+feedparser.parse(feed_url).feed.title
    except:
        feed_title = 'תב"ע פתוחה '+city+ ":"

    if form.validate_on_submit():
        a_new_feed = Feed(
            user_id=session['user_id'],
            name=form.name.data,
            url=form.url.data,
            project="opentaba"
        )
        db.session.add(a_new_feed)
        db.session.commit()
        flash(u'ההזנה החדשה נוספה למאגר')
        return redirect(url_for('notifier.feeds_editor'))

    user_email = session['user_email']
    return render_template('feeds_editor.html',
                           feed_title=feed_title,
                           feed_url=feed_url,
                           form=form,
                           project = "opentaba",
                           feeds=relevant_feeds(),
                           parsed_feeds=parse_feeds(relevant_feeds()),
                           user_email=user_email,
                           )

"""
@notifier.route('/addfeed/', methods=['GET', 'POST'])
@login_required
def no_new_feed():
    error = None
    form = AddFeedForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            a_new_feed = Feed(
                user_id=session['user_id'],
                name=form.name.data,
                url=form.url.data
            )
            db.session.add(a_new_feed)
            db.session.commit()
            flash(u'ההזנה החדשה נוספה למאגר')
            return redirect(url_for('notifier.feeds_editor'))

        user_email = session['user_email']
        return render_template('feeds_editor.html',
                          feed_title=form.name.data,
                          feed_url=form.url.data,
                          form=form,
                          feeds=relevant_feeds(),
                          parsed_feeds=parse_feeds(relevant_feeds()),
                          user_email=user_email,
                          )

"""
def relevant_feeds():
    return db.session.query(Feed).filter_by(
        user_id=session['user_id'])


@notifier.route('/delete_feed/<int:feed_id>/')
@login_required
def delete_feed(feed_id):
    feed_id = feed_id
    db.session.query(Feed).filter_by(id=feed_id).delete()
    db.session.commit()
    flash(u'מקור זה הוסר מהרשימה שלך')
    return redirect(url_for("notifier.feeds_editor"))


@notifier.route('/logos/<image>')
def logos(image):
    print(basedir+"/templates/images/"+image)
    return(basedir+"/templates/images/"+image)
