from datetime import timedelta
from os import pardir
from os.path import abspath, dirname, join

PROJECT_PATH = abspath(join(dirname(__file__), pardir))

DEBUG = True
ASSETS_DEBUG = True
SECRET_KEY = 'rebumd8xvrywgkvufsnrtvji7fyjeu4tue'
PERMAMENT_SESSION_LIFETIME = timedelta(days=60)  # around two months

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(PROJECT_PATH, 'momedict.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

RAPIDAPI_KEY = '44a6254049mshc2ba581a4a78e0ap1e3892jsnb1eb91c5e252'
RAPIDAPI_HOST = 'wordsapiv1.p.rapidapi.com'

try:
    from momedict.localconfig import *  # NOQA
except ImportError:
    pass
