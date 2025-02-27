from flask import Blueprint, request, jsonify
from .models import db, User, Quiz, Question, Participant
from .config import Config

routes = Blueprint("routes", __name__)  # FIX: Using Blueprint

# Helper function to check API key
def check_api_key():
    api_key = request.headers.get("X-API-KEY")
    if api_key != Config.API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return None

#  User creation (Open to all)
@routes.route("/users", methods=["POST"])
def create_user():
    data = request.json
    user = User(name=data["name"], role=data["role"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


@routes.route("/quizzes", methods=["POST"])
def create_quiz():
    """
    Creates a quiz -- api for teacher only
    """
    auth_error = check_api_key()
    if auth_error:
        return auth_error

    data = request.json
    quiz = Quiz(name=data["name"], teacher_id=data["teacher_id"])
    db.session.add(quiz)
    db.session.commit()
    return jsonify({"message": "Quiz created"}), 201

@routes.route("/quizzes/<int:quiz_id>/questions", methods=["POST"])
def add_question(quiz_id):
    """
    Adds a question to a quiz (API for teacher only)
    """
    auth_error = check_api_key()
    if auth_error:
        return auth_error

    data = request.json
    question = Question(
        quiz_id=quiz_id,
        question_text=data["question_text"],
        question_type=data["question_type"],
        options=data.get("options"),
        answer=data.get("answer")
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({"message": "Question added"}), 201

@routes.route("/quizzes", methods=["GET"])
def get_quizzes():
    """
    Get a list of quizzes (method open to all)
    """
    quizzes = Quiz.query.all()
    return jsonify([{"id": q.id, "name": q.name, "teacher_id": q.teacher_id} for q in quizzes])

@routes.route("/quizzes/<int:quiz_id>/participants", methods=["POST"])
def add_participant(quiz_id):
    """
    Adds a participant to a quiz
    """
    data = request.json
    participant = Participant(quiz_id=quiz_id, student_id=data["student_id"], score=data.get("score"))
    db.session.add(participant)
    db.session.commit()
    return jsonify({"message": "Participant added"}), 201

# gets a list of all participants
@routes.route("/quizzes/<int:quiz_id>/participants", methods=["GET"])
def get_participants(quiz_id):
    """
    Returns a list of students
    """
    participants = Participant.query.filter_by(quiz_id=quiz_id).all()
    if not participants:
        return jsonify({"message" : "No participants found"}), 404
    
    participant_list = [{"student_id" : p.student_id, "score" : p.score} for p in participants]
    return jsonify(participant_list), 200