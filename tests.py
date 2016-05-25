# -*- coding: utf-8 -*-
import datetime
import os
import unittest

import flask_bcrypt as bcrypt
from flask_testing import TestCase

from _config import basedir
from app import create_app
from app.models import User
from views import db

TEST_DB = 'test.db'

class UserTests(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        basedir, TEST_DB)
    TESTING = True

    def create_app(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, TEST_DB)
        self.app = app.test_client()
        return app

    # executed prior to each test
    def setUp(self):
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self, email, password):
        return self.client.post('/', data=dict(email=email, password=password),
                                follow_redirects=True)

    def logout(self):
        return self.client.get('logout/', follow_redirects=True)

    def register(self, email, password, confirm):
        return self.client.post('/register',
                                data=dict(email=email,
                                          password=password,
                                          confirm=confirm),
                                follow_redirects=True)

    def register_exemple(self):
        self.client.get('register/', follow_redirects=True)
        return self.register("noam@there.com", "123456", "123456")

    def test_user_setup(self):
        new_user = User('noamico@here.com', 'noamico')
        db.session.add(new_user)
        db.session.commit()
        test = db.session.query(User).all()
        for t in test:
            t.email
        assert t.email == 'noamico@here.com'

    def test_users_can_register(self):
        response = self.register("noamico@here.com", "123456", "123456")
        hoped_result = "תודה שנרשמת. כעת ניתן להתחבר לאתר".encode("UTF-8")
        self.assertIn(hoped_result, response.data)

    def test_users_cannot_login_unless_registered(self):
        response = self.login('foo', 'bar')
        hoped_result = ' או סיסמה שגויים'
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_form_is_present_on_login_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        hoped_result = "אנא התחבר/י כדי לצפות ברשימת מקורות המידע שלך."
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_form_is_present_on_register_page(self):
        response = self.client.get('register')
        self.assertEqual(response.status_code, 200)
        hoped_result = " אנא הירשמו כדי כדי להגיע לרשימת מקורות המידע שלכם."
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_invalid_form_data(self):
        self.register('noamico@b.com', '12345', '12345')
        response = self.login('noamico@b.com', '123456')
        hoped_result = ' או סיסמה שגויים'
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_user_registration(self):
        response = self.register_exemple()
        hoped_result = "תודה שנרשמת. כעת ניתן להתחבר לאתר"
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_user_duplicate_registration_error(self):
        self.register_exemple()
        response = self.register_exemple()
        hoped_result = 'הזו כבר קיימת באתר.'
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_logged_in_users_can_logout(self):
        self.register_exemple()
        self.login("noam@there.com", "123456")
        response = self.logout()
        hoped_result = "להתראות!"
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_not_logged_in_users_can_not_logout(self):
        response = self.logout()
        self.assertNotIn("להתראות!", response.data.decode('UTF-8'))
    """
    def test_logged_in_users_can_access_feeds_page(self):
        self.register_exemple()
        self.login("noam@there.com", "123456")
        response = self.client.get('feeds_editor', follow_redirects=True)
        hoped_text = "ברוכים הבאים, תהנו!"
        self.assertIn(hoped_text, response.data.decode('UTF-8'))
    """

    def test_logged_out_users_can_not_access_feeds_page(self):
        response = self.client.get('feeds_editor', follow_redirects=True)
        self.assertIn('עליך להירשם ולהתחבר לאתר.',
                      response.data.decode('UTF-8'))


    def create_user(self, email,password):
        new_user = User(email = email,
                        password=bcrypt.generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

    def create_feed(self):
        return self.client.post('addfeed/opentaba/ירושלים/http://opentaba-server-jerusalem.herokuapp.com/gush/30712/plans.atom', follow_redirects=True)
    """
    def test_users_can_add_feeds(self):
        self.create_user("noam@there.com","12345")
        self.login("noam@there.com","12345")
        self.client.get('feeds/',follow_redirects=True)
        response = self.create_feed()
        self.assertIn("ההזנה החדשה נוספה למאגר",response.data.decode('UTF-8'))

    def test_users_cannot_add_feeds_when_no_path(self):
        self.create_user("noam@there.com","12345")
        self.login("noam@there.com","12345")
        self.client.get("feeds/",follow_redirects = True)
        response = self.client.post('/addfeed/opentaba/ירושלים/',data=dict(
                path='',
                title='תב"ע פתוחה (ירושלים), גוש 30118'
        ))
        self.assertIn('יש להזין כתובת למקור המידע',response.data.decode('UTF-8'))
    """

    def test_404_error(self):
        response = self.client.get('/this-route-does-not-exist/')
        self.assertEquals(response.status_code,404)
        self.assertIn("בעיה", response.data.decode('utf-8'))

    def test_500_error(self):
        bad_user = User(
            email = 'noamoss@a.b.com',
            password = 'flask',
            last_update=datetime.date.today()
        )
        db.session.add(bad_user)
        db.session.commit()
        response = self.login('noamoss@a.b.com','flask')
        self.assertEquals(response.status_code, 500)
        self.assertNotIn(b'ValueError: Invalid salt', response.data)
        self.assertIn(str(bytes('משהו השתגע לנו','utf-8'),response.data.decode('utf-8')))


if __name__ == '__main__':
    unittest.main()
