# database.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # 其他用户相关字段

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    # 其他书籍相关字段

class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    book = db.relationship('Book', backref=db.backref('modules', lazy=True))

class TestRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Float, nullable=False)  # Score as a percentage
    user = db.relationship('User', backref=db.backref('test_records', lazy=True))
    module = db.relationship('Module', backref=db.backref('test_records', lazy=True))

class IncorrectWord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_record_id = db.Column(db.Integer, db.ForeignKey('test_record.id'), nullable=False)
    word = db.Column(db.String(80), nullable=False)
    test_record = db.relationship('TestRecord', backref=db.backref('incorrect_words', lazy=True))

def init_db(app):
    """Initializes the database."""
    with app.app_context():
        db.create_all()
