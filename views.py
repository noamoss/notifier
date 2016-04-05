# import the Flask class from the flask module
from flask import flash, redirect, render_template, \
    request, url_for, session
from functools import wraps

from db import db
from forms import RegisterForm, LoginForm, AddFeedForm
from sqlalchemy.exc import IntegrityError
from flask.blueprints import Blueprint
from models import User, Feed
import feedparser, operator


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
                flash('ברוכים הבאים, תהנו!')
                return redirect(url_for('notifier.feeds_editor'))
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


@notifier.route('/feeds_editor')
@login_required
def feeds_editor():
    return render_template('feeds_editor.html', form=AddFeedForm(request.form),
                                                feeds = relevant_feeds(),
                                                parsed_feeds = parse_feeds(relevant_feeds())
                           )

@notifier.route('/addfeed/<path:feed_url>',methods=['GET','POST'])
@login_required
def new_feed(feed_url):
    feed_title = feedparser.parse(feed_url).feed.title
    return render_template('feeds_editor.html',feed_url=feed_url,
                                                feed_title=feed_title,
                                                form=AddFeedForm(request.form),
                                                feeds=relevant_feeds(),
                                                parsed_feeds=parse_feeds(relevant_feeds())
                                )

@notifier.route('/addfeed/', methods=['GET', 'POST'])
@login_required
def no_new_feed():
    error = None
    form = AddFeedForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            new_feed = Feed(
                user_id = session['user_id'],
                name = form.name.data,
                url = form.url.data
            )
            db.session.add(new_feed)
            db.session.commit()
            flash("ההזנה החדשה נוספה למאגר")
            return redirect(url_for('notifier.feeds_editor'))


def relevant_feeds():
    return db.session.query(Feed).filter_by(
        user_id=session['user_id'])

@notifier.route('/delete_feed/<int:feed_id>/')
@login_required
def delete_feed(feed_id):
    feed_id = feed_id
    db.session.query(Feed).filter_by(id=feed_id).delete()
    db.session.commit()
    flash("מקור זה הוסר מהרשימה שלך")
    return redirect(url_for("notifier.feeds_editor"))


def parse_feeds(feeds):
# parse and mix opentaba feeds
    results=[]

    for feed in feeds:
        feed_data = feedparser.parse(feed.url)
        for entry in feed_data.entries:
            results.append([feed.name,entry.summary,entry.link,entry.updated])
    return sorted(results, key=operator.itemgetter(3),reverse=True)
