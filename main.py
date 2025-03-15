import json
from app import app, db
from app.models import User, Quiz, Question
import hashlib
import os
import random
import string

def insert_test_data():
    if not User.query.filter_by(email="teacher@example.com").first():
        
        teacher = User(
            name="Teacher One",
            email="teacher@example.com",
            role="teacher",
            salt=os.urandom(32).hex()
        )
        teacher.password_hash = hashlib.sha256(("password123" + teacher.salt).encode()).hexdigest()
        db.session.add(teacher)
        db.session.commit()

        quiz_code = '123456'
        quiz = Quiz(name="test Quiz", teacher_id=teacher.id, quiz_code=quiz_code)
        db.session.add(quiz)
        db.session.commit()

        question1 = Question(
            quiz_id=quiz.id,
            question_text="What is the capital of France?",
            question_type="MC",
            options=json.dumps(["Paris", "London", "Berlin", "Madrid"]),
            answer="Paris"
        )
        question2 = Question(
            quiz_id=quiz.id,
            question_text="Is Python a programming language?",
            question_type="TF",
            options=json.dumps(["True", "False"]),
            answer="True"
        )
        db.session.add_all([question1, question2])
        db.session.commit()

        print(f"Test teacher, quiz, and questions created successfully.")
        print(f"Quiz Code for Joining: {quiz_code}")

    else:
        print("Test data already exists.")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        insert_test_data()
    app.run(debug=True)