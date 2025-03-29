from flask import Flask
from foodtracker.extensions import db, mail  # ✅ Import mail from extensions.py
from itsdangerous import URLSafeTimedSerializer
from .main.routes import main
import os
from flask_login import LoginManager
from foodtracker.models import User

def create_app():
    app = Flask(__name__)

    # ✅ App Configurations
    app.config['DEBUG'] = True  
    app.config['TESTING'] = False  

    # ✅ Mail Server Settings
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'  
    app.config['MAIL_PORT'] = 587  
    app.config['MAIL_USE_TLS'] = True  
    app.config['MAIL_USE_SSL'] = False  
    app.config['MAIL_DEBUG'] = app.config['DEBUG']  

    # ✅ Authentication Details
    app.config['MAIL_USERNAME'] = 'derrickmacha1@gmail.com'  
    app.config['MAIL_PASSWORD'] = 'glcl uqqf zsli xfsw'  # Use an app password

    # ✅ Default Sender
    app.config['MAIL_DEFAULT_SENDER'] = ('Derrick from Entry Pro Services', 'derrickmacha1@gmail.com')

    # ✅ Database Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ✅ Initialize Extensions
    db.init_app(app)
    mail.init_app(app)  # ✅ Initialize mail

    # ✅ Flask-Login Configuration
    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # ✅ Register Blueprints
    app.register_blueprint(main)

    # ✅ Ensure Database Tables Exist
    create_database(app)

    return app

def create_database(app):
    with app.app_context(): 
        db.create_all()  
        print('✅ Ensured Database Tables Exist!')
