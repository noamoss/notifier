from flask import Flask
from flask.ext.testing import TestCase
import unittest
import os

from app import create_app
from views import db
from _config import basedir
from models import User, Feed

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
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                    os.path.join(basedir, TEST_DB)
        return app

    #executed prior to each test
    def setUp(self):
        db.create_all()

    # executed after each test
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self,email,password):
        return self.client.post('/',data=dict(email=email, password=password), follow_redirects=True)

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

    def test_users_can_login(self):
        response = self.register("noamico@here.com", "123456","123456")
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
        self.register('noamico@b.com','12345','12345')
        response = self.login('noamico@b.com','123456')
        hoped_result = ' או סיסמה שגויים'
        self.assertIn(hoped_result, response.data.decode('UTF-8'))

    def test_user_registration(self):
        response = self.register_exemple()
        hoped_result="תודה שנרשמת. כעת ניתן להתחבר לאתר"
        self.assertIn(hoped_result,response.data.decode('UTF-8'))


if __name__ == '__main__':
    unittest.main()