import hashlib
import os
from .database import db
import json

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def set_password(self, password):
        self.salt = os.urandom(32).hex()
        self.password_hash = hashlib.sha256((password + self.salt).encode()).hexdigest()

    def verify_password(self, password):
        return self.password_hash == hashlib.sha256((password + self.salt).encode()).hexdigest()

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quiz_code = db.Column(db.String(6), unique=True, nullable=False)

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_text = db.Column(db.String(255), nullable=False)
    question_type = db.Column(db.String(50), nullable=False)
    options = db.Column(db.Text, nullable=True)
    answer = db.Column(db.String(255))
    
    def get_options(self):
        return json.loads(self.options) if self.options else []
    
    def set_options(self, options_list):
        self.options = json.dumps(options_list)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer)