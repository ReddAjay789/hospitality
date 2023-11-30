# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)

    role = db.relationship('Role', backref=db.backref('users', lazy=True))

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    image_urls = db.Column(db.JSON)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(255))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    num_guests = db.Column(db.Integer)
    checkin_date = db.Column(db.Date)
    checkout_date = db.Column(db.Date)
