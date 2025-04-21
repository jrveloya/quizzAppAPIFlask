import pytest
from app import app, db
from app.models import User, Quiz, Question, Participant
from main import insert_test_data
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            insert_test_data()
        yield client
        with app.app_context():
            db.drop_all()

def test_home_route(client):
    # Test that the homepage loads correctly
    response = client.get("/")
    assert response.status_code == 200

def test_get_quizzes(client):
    # Test that the quiz list endpoint returns the dummy quiz
    response = client.get("/quizzes")
    assert response.status_code == 200
    quizzes = response.get_json()
    assert len(quizzes) == 1
    # Adjust the quiz name if your test data uses a different one
    assert quizzes[0]["name"] == "test Quiz"

def test_get_questions(client):
    # Test retrieving questions for quiz with id=1
    response = client.get("/quizzes/1/questions")
    assert response.status_code == 200
    questions = response.get_json()
    assert len(questions) == 2
    # Verify one of the questions is as expected
    assert questions[0]["question_text"] == "What is the capital of France?"

def test_join_and_submit_quiz(client):
    from app.models import Quiz, Question, Participant

    # --- Step 1: Dynamically fetch quiz and its questions ---
    with client.application.app_context():
        quiz = Quiz.query.filter_by(quiz_code="123456").first()
        assert quiz is not None
        quiz_id = quiz.id

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        assert len(questions) == 2

        # Create answer payload using correct answers
        answers = {str(q.id): q.answer for q in questions}

    # --- Step 2: Join Quiz ---
    join_payload = {
        "quiz_code": "123456",
        "name": "Student1"
    }

    # Simulate a session for the participant
    join_response = client.post("/join_quiz", data=join_payload)
    assert join_response.status_code in (200, 302)  # Allow 302 for redirect

    # --- Step 3: Simulate session for submission ---
    with client.session_transaction() as sess:
        sess["participant_name"] = "Student1"
        sess["quiz_id"] = quiz_id

    # --- Step 4: Submit Quiz ---
    submit_payload = {
        "answers": answers
    }

    submit_response = client.post(f"/quizzes/{quiz_id}/submit", json=submit_payload)
    assert submit_response.status_code == 201
    submit_data = submit_response.get_json()
    assert "score" in submit_data
    assert submit_data["score"] == 100.0

    # --- Step 5: Confirm participant exists and scored correctly ---
    with client.application.app_context():
        participant = Participant.query.filter_by(quiz_id=quiz_id, name="Student1").first()
        assert participant is not None
        assert participant.score == 100