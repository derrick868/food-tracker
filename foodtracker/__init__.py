from flask import Flask
from foodtracker.extensions import db
  # Import User model


from .main.routes import main
import os
from flask_login import LoginManager
from foodtracker.models import User

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    app.register_blueprint(main)

    # Ensure the database is created
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    return app

def create_database(app):
    with app.app_context(): 
        db.create_all()  
        print('Ensured Database Tables Exist!')


