from .extensions import db
from flask_login import UserMixin

log_food = db.Table('log_food',
    db.Column('log_id', db.Integer, db.ForeignKey('log.id'), primary_key=True),
    db.Column('food_id', db.Integer, db.ForeignKey('food.id'), primary_key=True)
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    confirmed = db.Column(db.Boolean, default=False)

    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    foods= db.relationship('Food', backref='user', lazy=True)  # Define relationship


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    proteins = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def calories(self):
        return self.proteins * 4 + self.carbs * 4 + self.fats * 9

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 

    user = db.relationship('User', backref=db.backref('logs', lazy=True))
    foods = db.relationship('Food', secondary=log_food, lazy='dynamic')