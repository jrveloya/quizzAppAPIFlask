import pytest
from app import app, db
from app.models import User, Quiz, Question, Participant

API_KEY = "SECRET_API_KEY_1234"

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

# Test creating a user (teacher)
def test_create_user(client):
    response = client.post("/users", json={"name": "Alice", "role": "teacher"})
    assert response.status_code == 201
    assert response.json["message"] == "User created"

# Test creating a quiz (teacher only)
def test_create_quiz(client):
    client.post("/users", json={"name": "Alice", "role": "teacher"})
    response = client.post("/quizzes", json={"name": "Math Test", "teacher_id": 1}, headers={"X-API-KEY": API_KEY})
    assert response.status_code == 201
    assert response.json["message"] == "Quiz created"

# Test unauthorized quiz creation (should fail)
def test_create_quiz_unauthorized(client):
    response = client.post("/quizzes", json={"name": "Unauthorized Test", "teacher_id": 1})
    assert response.status_code == 403

# Test adding a question to a quiz (teacher only)
def test_add_question(client):
    client.post("/users", json={"name": "Alice", "role": "teacher"})
    client.post("/quizzes", json={"name": "Math Test", "teacher_id": 1}, headers={"X-API-KEY": API_KEY})
    
    response = client.post("/quizzes/1/questions", json={
        "question_text": "2+2?",
        "question_type": "MC",
        "options": '["1", "2", "4"]',
        "answer": "4"
    }, headers={"X-API-KEY": API_KEY})

    assert response.status_code == 201
    assert response.json["message"] == "Question added"

# Test unauthorized question addition (should fail)
def test_add_question_unauthorized(client):
    response = client.post("/quizzes/1/questions", json={
        "question_text": "Unauthorized Question",
        "question_type": "MC",
        "options": '["A", "B", "C"]',
        "answer": "A"
    })
    assert response.status_code == 403  # Should be unauthorized

# Test retrieving quizzes (any user can access)
def test_get_quizzes(client):
    client.post("/users", json={"name": "Alice", "role": "teacher"})
    client.post("/quizzes", json={"name": "Math Test", "teacher_id": 1}, headers={"X-API-KEY": API_KEY})
    
    response = client.get("/quizzes")
    assert response.status_code == 200
    quizzes = response.json
    assert len(quizzes) == 1
    assert quizzes[0]["name"] == "Math Test"

# Test adding a participant (student takes a quiz)
def test_add_participant(client):
    client.post("/users", json={"name": "Alice", "role": "teacher"})
    client.post("/quizzes", json={"name": "Math Test", "teacher_id": 1}, headers={"X-API-KEY": API_KEY})
    client.post("/users", json={"name": "Bob", "role": "student"})

    response = client.post("/quizzes/1/participants", json={"student_id": 2, "score": 90})
    assert response.status_code == 201
    assert response.json["message"] == "Participant added"

# Test retrieving participants (teacher only)
def test_get_participants(client):
    client.post("/users", json={"name": "Alice", "role": "teacher"})
    client.post("/quizzes", json={"name": "Math Test", "teacher_id": 1}, headers={"X-API-KEY": API_KEY})
    client.post("/users", json={"name": "Bob", "role": "student"})
    client.post("/quizzes/1/participants", json={"student_id": 2, "score": 85})

    response = client.get("/quizzes/1/participants", headers={"X-API-KEY": API_KEY})
    assert response.status_code == 200
    participants = response.json
    assert len(participants) == 1
    assert participants[0]["score"] == 85