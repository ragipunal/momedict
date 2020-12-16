import logging
from logging.handlers import SMTPHandler

from flask import Flask
from flask_assets import Bundle, Environment
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from werkzeug.middleware.proxy_fix import ProxyFix

from momedict.importer import ImportCommand
from momedict.user import get_user
from momedict.utils import datetimeformat
from momedict.views.api import api
from momedict.views.memo import memo
from momedict.views.auth import auth


def create_app(config_filename='config.py'):
    from .database import db
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    db.init_app(app)
    migrate.init_app(app, db)
    manager(app)
    assets.init_app(app)

    app.register_blueprint(memo)
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api, url_prefix='/api')

    if app.debug:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except ImportError:
            pass
    else:
        app.logger.addHandler(mail_handler)

    @app.context_processor
    def utility_processor():
        return dict(user=get_user())

    app.jinja_env.filters['datetimeformat'] = datetimeformat
    return app


migrate = Migrate()
manager = Manager(create_app)
manager.add_command('db', MigrateCommand)
manager.add_command('import', ImportCommand)

assets = Environment()
js = Bundle(
    'js/jquery.min.js', 'js/bootstrap.bundle.min.js', 'js/moment.js',
    'vendor/slimscroll/slimscroll.min.js', 'vendor/slimscroll/custom-scrollbar.js',
    filters='jsmin', output='js/min.%(version)s.js'
)
app_js = Bundle('js/main.js', filters='jsmin', output='js/app.min.%(version)s.js')
css = Bundle(
     'css/bootstrap.min.css', 'css/main.css', 'fonts/style.css', filters='cssmin', output='css/min.%(version)s.css'
)

auth_css = Bundle(
    'css/bootstrap.min.css', 'css/main.css', filters='cssmin', output='css/min.%(version)s.css'
)
assets.register('js', js)
assets.register('app_js', app_js)
assets.register('css', css)
assets.register('auth_css', auth_css)

ADMINS = ['ragip@ragipunal.com']
mail_handler = SMTPHandler(
    '127.0.0.1',
    'ragip@ragipunal.com',
    ADMINS, '[Flask] Momedict ERROR'
)
mail_handler.setLevel(logging.ERROR)
