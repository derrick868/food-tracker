import os
import re
from dotenv import load_dotenv  # ✅ Load .env file
load_dotenv()

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from foodtracker.models import User
from foodtracker.extensions import db, mail
from .main.routes import main

def create_app():
    app = Flask(__name__)

    # ✅ General Config
    app.config['DEBUG'] = True
    app.config['TESTING'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

    # ✅ Mail Configuration
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEBUG'] = app.config['DEBUG']
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = (
        'Derrick from Entry Pro Services', 
        os.getenv('MAIL_USERNAME')
    )

    # ✅ Database Configuration - use Supabase URL
    uri = os.getenv('DATABASE_URL')
    if uri and uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ✅ Initialize Extensions
    db.init_app(app)
    mail.init_app(app)

    # ✅ Flask-Login Configuration
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Register Blueprints
    app.register_blueprint(main)

    return app
