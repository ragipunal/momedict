from flask_testing import TestCase

from flask import g

from momedict.application import create_app
from momedict.database import db
from momedict.models import User


class MomedictTestCase(TestCase):
    def create_app(self):
        return create_app('../tests/config.py')


class DatabaseTestCase(MomedictTestCase):
    def setUp(self):
        super().setUp()
        db.create_all()

    def tearDown(self):
        super().tearDown()
        db.session.remove()
        db.drop_all()

    def set_user(self, user):
        g.user = user

    def mock_user(self, registered=False, save=False):
        user = User()
        user.registered = registered
        user.name = "Name"
        user.username = "name"
        if save:
            db.session.add(user)
            db.session.commit()
        self.set_user(user)
        return user
