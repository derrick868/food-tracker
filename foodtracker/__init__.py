from flask import Flask
from foodtracker.extensions import db

from .main.routes import main

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'


    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main)

    # Ensure the database is created
    create_database(app)

    return app

def create_database(app):
    with app.app_context(): 
        db.create_all()  
        print('Ensured Database Tables Exist!')

