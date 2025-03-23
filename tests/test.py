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
    # --- Test Joining the Quiz ---
    join_payload = {
        "quiz_code": "123456",  # This should match the dummy quiz code from insert_test_data()
        "name": "Student1"
    }
    join_response = client.post("/join_quiz", json=join_payload)
    assert join_response.status_code == 200
    join_data = join_response.get_json()
    # Check that we received a redirect URL in the response
    assert "redirect_url" in join_data
    assert join_data["message"].startswith("Joined quiz successfully")
    
    # Simulate that the student's name is stored in the session for quiz submission
    with client.session_transaction() as sess:
        sess["participant_name"] = "Student1"
        sess["quiz_id"] = 1

    # --- Test Submitting the Quiz ---
    submit_payload = {
        "answers": {
            "1": "Paris",  # Correct answer for question 1
            "2": "True"    # Correct answer for question 2
        }
    }
    submit_response = client.post("/quizzes/1/submit", json=submit_payload)
    assert submit_response.status_code == 201
    submit_data = submit_response.get_json()
    assert "score" in submit_data
    # Assuming both questions are answered correctly, score should be 100%
    assert submit_data["score"] == 100.0