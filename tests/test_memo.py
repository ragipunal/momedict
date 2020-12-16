from flask import Flask

from tests import MomedictTestCase


class ApplicationTest(MomedictTestCase):
    def test_create_memo(self):
        memo = self.create_app()
        self.assertIsInstance(memo, Flask)
