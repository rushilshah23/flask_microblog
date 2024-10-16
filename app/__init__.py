import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l

def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

# declare main flask app
app = Flask(__name__)



# setting config of the app
app.config.from_object(Config)

# Set babel to the app
babel = Babel(app, locale_selector=get_locale)

# declaring db to use database with ORM ie SQLAlchemy which gets its config from app which helps us to write pythonic code
db = SQLAlchemy(app)

# Migrations to easily handle changes in structures of database in parts
migrate = Migrate(app,db)

# login manager to maintain user sessions
login = LoginManager(app)

# redirect unauthenticated user to this route
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')

mail = Mail(app)

# For managing timezones in the client side by providing js script
moment = Moment(app)


if not app.debug:

    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@'+ app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'],
            subject='Blog app failure',
            credentials=auth, secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        filename='logs/microblog.log',
        backupCount=10,
        maxBytes=10240
    )

    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s : %(message)s [in %(pathname)s:%(lineno)d]'
    ))

    file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)

    app.logger.info("MIcroblog app stated !")


from app import routes, models, errors
