# -*- coding: utf-8 -*-
# import the Flask class from the flask module
import datetime
import urllib
from functools import wraps

import flask_bcrypt as bcrypt
import sendgrid
from flask import flash, redirect, render_template, \
    request, url_for, session, Blueprint

from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from _config import basedir, BITLY_USER, BITLY_KEY, sharing_services, relevant_days_for_feed, \
    NOTIFIER_MAIL_ADDRESS, MAIL_SUBJECT, SENDGRID_KEY
from app.models import User, Feed, SharedItem
from bitlyapi import bitlyapi
from db import db
from feeds import parse_feeds, set_title_by_feed, relevant_feeds,relevant_feeds_urls, get_project_by_feed_url, \
    save_feed_to_db
from forms import RegisterForm, LoginForm, AddFeedForm
from tokenit import generate_confirmation_token, confirmed_token

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
            if user is not None and bcrypt.check_password_hash(user.password, request.form['password']):
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
                bcrypt.generate_password_hash(form.password.data),
                confirmed=False,
            )
            try:
                db.session.add(new_user)
                db.session.commit()

            except IntegrityError:
                error = 'כתובת הדוא"ל הזו כבר קיימת באתר.'
                return render_template('register.html', form=form, error=error)

            token = generate_confirmation_token(new_user.email)
            confirm_url = url_for('notifier.confirmed_email',token=token,_external=True)

            session['logged_in'] = True
            session['user_id'] = new_user.id
            session['user_email'] = new_user.email

            client = sendgrid.SendGridClient(SENDGRID_KEY)
            conf_mail = sendgrid.Mail()
            conf_mail.add_to(new_user.email)
            conf_mail.set_from(NOTIFIER_MAIL_ADDRESS)
            conf_mail.set_subject(MAIL_SUBJECT)
            conf_mail.set_html(render_template('user/activate.html',confirm_url=confirm_url))
            client.send(conf_mail)

            flash(u'תודה שנרשמת. כעת ניתן להתחבר לאתר')
            return redirect(url_for('notifier.feeds_editor'))
        else:
            print(form.errors)
    return render_template("register.html", form=form, error=error)


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"תקלה בשדה %s - %s" % (
                getattr(form, field).label.text, error), 'error')


@notifier.route('/feeds_editor', methods=["GET","POST"])
@login_required
def feeds_editor():
    user_email = session['user_email']
    return render_template('feeds_editor.html', user_email=user_email,
        form=AddFeedForm(request.form),
        feeds=relevant_feeds(),
        parsed_feeds=parse_feeds(relevant_feeds()),
        days_no=relevant_days_for_feed
        )

@notifier.route('/addfeed/kikar', methods=['GET'])
def kikar_feed():
    url = request.args.get('link','')
    relevantfeeds = relevant_feeds_urls()
    name = set_title_by_feed(url)[1]
    print (set_title_by_feed(url))
    user_id = session['user_id']
    save_feed_to_db(url=url, name=name, project="כיכר המדינה", user_id=user_id,relevant_feeds=relevantfeeds)
    return redirect(url_for('notifier.feeds_editor'))


@notifier.route('/addfeed/opentaba', methods=['GET'])
def opentaba_feed():
    url = request.args.get('link','')
    relevantfeeds = relevant_feeds_urls()
    if url not in relevantfeeds:
        title = set_title_by_feed(url)
        title = title[1].split(" ")
        try:
            city = request.args.get('city','')
            title.insert(2," "+city+" ")
        except:
            city=" "
        name = " ".join(title)
        a_new_feed = Feed(
            user_id=session['user_id'],
            url = request.args.get('link',''),
            name=name,
            project='תב"ע פתוחה '+city,
        )
        db.session.add(a_new_feed)
        db.session.commit()
        flash(u'ההזנה החדשה נוספה למאגר')
        return redirect(url_for('notifier.feeds_editor'))
    else:
        flash(u'את/ה כבר עוקבים אחרי מקור מידע זה')
        return redirect(url_for('notifier.feeds_editor'))


@notifier.route('/addfeed', methods=['GET', 'POST'])
@login_required
def new_feed():
    error = None
    form = AddFeedForm(request.form)
    try:
        project = get_project_by_feed_url(url)

    except:
        project =''

    if request.method == 'POST':
        url = form.url.data
        name = " ".join(set_title_by_feed(url))
        if project==u'תב"ע פתוחה':
            return redirect(url_for('notifier.opentaba_feed', link= url))
        elif project==u'כיכר המדינה':
            return redirect(url_for('notifier.kikar_feed', link= url))

        elif form.validate_on_submit():
            a_new_feed = Feed(
                user_id=session['user_id'],
                name=name,
                url=url,
                project=project,
                )
            db.session.add(a_new_feed)
            db.session.commit()
            flash(u'ההזנה החדשה נוספה למאגר')
            return redirect(url_for('notifier.feeds_editor'))

    elif request.method == 'GET':
        if project == u'תב"ע פתוחה':
            return redirect(url_for('notifier.opentaba_feed',link=request.args.get('link')))
        elif project == u'כיכר המדינה':
            return redirect(url_for('notifier.kikar_feed',link=request.args.get('link'), type=request.args.get('type')))

    user_email = session['user_email']
    return redirect(url_for('notifier.feeds_editor'))




@notifier.route('/delete_feed/<int:feed_id>/')
@login_required
def delete_feed(feed_id):
    feed_id = feed_id
    db.session.query(Feed).filter_by(id=feed_id).delete()
    db.session.commit()
    flash(u'מקור זה הוסר מהרשימה שלך')
    return redirect(url_for("notifier.feeds_editor"))


@notifier.route('/share')
# check if a bitly shorten url was already made (and shard) - if it was, add 1 to counter, if not, create one
def share_item(service=None, title=None, project=None, link=None):
    service = request.args.get('service')
    link=urllib.parse.unquote_plus(request.args.get('link'))
    feed_title = request.args.get('title',title)
    project = request.args.get('project',project)
    locate_link = SharedItem.query.filter_by(full_url=link).first()
    if locate_link is not None:   #if it is not the first time item/link is shared
        locate_link.add_share(service)
        bitly_link=locate_link.bitly
        feed_title=locate_link.feed_title
        project=locate_link.project
        print(service,":",locate_link.service_share_counter[service])

    else:                          # if item/link wasn't shared before -
        bitlyconnection = bitlyapi.Connection(BITLY_USER, BITLY_KEY)
        bitly_link = bitlyconnection.shorten(link)['url']
        new_item=SharedItem(feed_title=feed_title,
                            full_url=link,
                            bitly=bitly_link,
                            project=project,
                            shares_count=1,
                            )
        new_item.service_share_counter[service] = 1
        db.session.add(new_item)
        print(service,":",new_item.service_share_counter[service])
    db.session.commit()    # save changes to db

    return redirect(sharing_services[service].format(project,feed_title,bitly_link))


@notifier.route('/confirm/<token>')
@login_required
def confirmed_email(token):
    try:
        email = confirmed_token(token)
    except:
        flash("הקישור לאישור ההרשמה אינו תקין או שפג תוקפו", "תקלה")
    user = User.query.filter_by(email=email).first_or_404()
    if user.confirmed():
        flash("החשבון כבר אושר בעבר. אנא התחבר/י","הצלחה")
    else:
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        db.session.add(User)
        db.session.commit()
        flash("אישרת את חשבונך, תודה!", "הצלחה")
    return redirect(url_for('notifier.login'))
