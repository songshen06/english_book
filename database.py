# database.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class WordRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    word = db.Column(db.String(80), nullable=False)
    book_name = db.Column(db.String(100), nullable=True)
    module = db.Column(db.String(50), nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    test_type  = db.Column(db.String(50),nullable=False)



def init_db(app):
    """Initializes the database."""
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        db.init_app(app)
        with app.app_context():
            db.create_all()
