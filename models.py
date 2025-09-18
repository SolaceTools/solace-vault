from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(500), nullable=False)

class Secret(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(60), nullable=False)
    data = db.Column(db.Text, nullable=False)
    tag = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    secret_id = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(50), nullable=True)
    label = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)
