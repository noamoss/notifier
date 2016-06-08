# -*- coding: utf-8 -*-
# import the Flask class from the flask module

import datetime, urllib, sys
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
                login_user(user)
            else:
                error = u'כתובת דוא"ל או סיסמה שגויים'
        else:
            error = u"שני השדות דרושים להתחברות."

    if 'logged_in' in session:  #if already logged in:
        flash(u'ברוכים השבים, את/ה כבר מחוברת!')
        return redirect(url_for('notifier.feeds_editor'))
    else:
        return render_template("login.html", form=form, error=error)


@notifier.route('/logout')
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
                error = u'כתובת הדוא"ל הזו כבר קיימת באתר.'
                return render_template('register.html', form=form, error=error)

            token = generate_confirmation_token(new_user.email)
            confirm_url = url_for('notifier.confirmed_email',token=token,_external=True)

            login_user(new_user)

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
            pass #(instead of printing error)
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
@login_required
def add_feed_kikar():
    url = request.args.get('link','')
    relevantfeeds = relevant_feeds_urls()
    name = set_title_by_feed(url)[1]
    user_id = session['user_id']
    save_feed_to_db(url=url, name=name, project=u"כיכר המדינה", user_id=user_id,relevant_feeds=relevantfeeds)
    return redirect(url_for('notifier.feeds_editor'))


@notifier.route('/addfeed/opentaba', methods=['GET'])
@login_required
def add_feed_opentaba():
    try:
        url = request.args.get('link','')
        city = request.args.get('city')
        if city is None:
            city=""
        relevantfeeds = relevant_feeds_urls()
        if url not in relevantfeeds:
            name = set_title_by_feed(url,city=city)[1]
            a_new_feed = Feed(
                user_id=session['user_id'],
                url=request.args.get('link', ''),
                name=name,
                project=get_project_by_feed_url(url).encode('utf8'),
                )
            db.session.add(a_new_feed)
            db.session.commit()
            flash(u'ההזנה החדשה נוספה למאגר')
            return redirect(url_for('notifier.feeds_editor'))

        else:
            flash(u'את/ה כבר עוקבים אחרי מקור מידע זה')
            return redirect(url_for('notifier.feeds_editor'))
    except (ValueError, KeyError, TypeError):
        errormsg = "type: " + str(sys.exc_info()[0]) + ", value: " + str(sys.exc_info()[1]) + ", traceback: " + str(sys.exc_info()[2])
        return render_template('error.html', errormsg=errormsg)


def login_user(user):
    session['logged_in'] = True
    session['user_id'] = user.id
    session['user_email'] = user.email


@notifier.route('/add/<string:projectname>', methods=['GET','POST'])
def trying(projectname=None):
    if 'logged_in' in session and projectname!=None:  # if already logged in
        return redirect(
            url_for('notifier.add_feed_' + projectname, **request.args))
    else:                          # if not logged in - either login and add feed or register and add feed
        error= None
        login_form=LoginForm(request.form)
        register_form=RegisterForm(request.form)
        if request.method == "POST":
            if request.form['btn'] == 'login':    #for returning users
                if login_form.validate_on_submit():
                    user = User.query.filter_by(email=request.form['email']).first()
                    if user is not None and bcrypt.check_password_hash(user.password,
                                                                       request.form[
                                                                           'password']):
                        login_user(user)
                        return redirect(
                            url_for('notifier.add_feed_' + projectname, **request.args))
                    else:
                        error = u'כתובת דוא"ל או סיסמה שגויים'
                else:
                    error = u"שני השדות דרושים להתחברות."

                return render_template('add_feed_and_register.html',
                                       register_form=register_form,
                                       login_form=login_form,
                                       error=error)

            elif request.form['btn'] == 'register':        # for new users
                if register_form.validate_on_submit():
                    new_user = User(
                        register_form.email.data,
                        bcrypt.generate_password_hash(register_form.password.data),
                     confirmed=False,
                    )
                    try:
                        db.session.add(new_user)
                        db.session.commit()

                    except IntegrityError:
                        error = u'כתובת הדוא"ל הזו כבר קיימת באתר.'
                        return render_template('add_feed_and_register.html',
                                   set_tab=1,
                                   register_form=register_form,
                                   login_form=login_form,
                                   error=error)

                    token = generate_confirmation_token(new_user.email)
                    confirm_url = url_for('notifier.confirmed_email', token=token,
                                          _external=True)

                    client = sendgrid.SendGridClient(SENDGRID_KEY)
                    conf_mail = sendgrid.Mail()
                    conf_mail.add_to(new_user.email)
                    conf_mail.set_from(NOTIFIER_MAIL_ADDRESS)
                    conf_mail.set_subject(MAIL_SUBJECT)
                    conf_mail.set_html(render_template('user/activate.html',
                                                       confirm_url=confirm_url))
                    client.send(conf_mail)

                    flash(u'תודה שנרשמת.')
                    login_user(new_user)
                    return redirect(
                        url_for('notifier.add_feed_' + projectname,**request.args))

                return render_template('add_feed_and_register.html',
                                       set_tab=1,
                                       register_form=register_form,
                                       login_form=login_form,
                                       error=error)

        elif request.method == "GET":
            return render_template('add_feed_and_register.html',
                               register_form=register_form,
                               login_form=login_form,
                               error=error)


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


@notifier.app_errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@notifier.app_errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@notifier.app_errorhandler(502)
def feed_error(error):
    return render_template('502.html'), 502
