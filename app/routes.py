from flask import Blueprint, redirect, request, jsonify, render_template, session, url_for, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, set_access_cookies, unset_jwt_cookies
from .models import db, User, Quiz, Question, Participant
from .config import Config
import json
import random
import string


routes = Blueprint("routes", __name__)

# Helper function to check API key
def check_api_key():
    api_key = request.headers.get("X-API-KEY")
    if api_key != Config.API_KEY:
        return jsonify({"error": "Unauthorized"}), 403
    return None

def generate_quiz_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

#  User creation (Open to all)
@routes.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(name=data["name"], role=data["role"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201

@routes.route("/create_quiz", methods=["GET", "POST"])
@jwt_required()
def create_quiz():
    if request.method == "GET":
        return render_template("create_quiz.html")

    elif request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        teacher_id = get_jwt_identity()
        questions = data.get("questions", [])

        quiz_code = generate_quiz_code()
        quiz = Quiz(name=name, teacher_id=teacher_id, quiz_code=quiz_code)
        db.session.add(quiz)
        db.session.commit()

        for q in questions:
            question = Question(
                quiz_id=quiz.id,
                question_text=q["question_text"],
                question_type=q["question_type"],
                options=json.dumps(q["options"]),
                answer=q["answer"]
            )
            db.session.add(question)

        db.session.commit()

        return jsonify({
            "message": "Quiz created",
            "quiz_code": quiz.quiz_code
        }), 201

@routes.route("/quizzes/<int:quiz_id>/questions", methods=["POST"])
def add_question(quiz_id):
    """
    Adds a question to a quiz (API for teacher only)
    """
    auth_error = check_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    question_type = data["question_type"]
    if question_type == 'MC':
        if "options" not in data or not isinstance(data["options"], list):
            return jsonify({
                    "error" : "MC questions require a list of options"
                }), 400
        if "answer" not in data or data["answer"] not in data["options"]:
            return jsonify({
                "error" : "Answer must be one of the options"
                }), 400
        
        options_json = json.dumps(data.get("options", []))
    elif question_type == "TF":
        if "answer" not in data or data["answer"] not in data["options"]:
            return jsonify({
                "error" : "answer must be a part of the options"
            }), 400
        options_json = json.dumps(['True', 'False'])
    else:
        return jsonify({
            "error" : "Invalid question type"
        }), 400
    
    question = Question(
        quiz_id=quiz_id,
        question_text=data["question_text"],
        question_type=data["question_type"],
        options=options_json,
        answer=data.get("answer")
    )
    db.session.add(question)
    db.session.commit()
    return jsonify({"message": "Question added"}), 201

@routes.route("/quizzes/<int:quiz_id>/questions", methods=["GET"])
def get_questions(quiz_id):
    # retrieves all questions from a quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify([
        {
            "id" : q.id,
            "question_type" : q.question_type,
            "question_text" : q.question_text,
            "options" : json.loads(q.options) if q.options else None,
            "answer" : q.answer
        }
        for q in questions
    ])

@routes.route("/quizzes/<int:quiz_id>/submit", methods=["POST"])
def submit_quiz(quiz_id):
    # Retrieve participant name from session
    name = session.get("participant_name")
    
    if not name:
        return jsonify({"error": "No participant found in session. Please join the quiz first."}), 400

    data = request.get_json()
    submitted_answers = data.get("answers", {})

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    # Calculate the score
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    total_questions = len(questions)
    correct_answers = sum(1 for q in questions if submitted_answers.get(str(q.id)) == q.answer)
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0

    # Update participant's score
    participant = Participant.query.filter_by(quiz_id=quiz_id, name=name).first()
    if participant:
        participant.score = score
        db.session.commit()
    else:
        return jsonify({"error": "Participant not found"}), 404

    # Clear session after submission
    session.pop("participant_name", None)
    session.pop("quiz_id", None)

    return jsonify({
        "message": "Quiz submitted successfully",
        "score": score
    }), 201

@routes.route("/take_quiz/<int:quiz_id>", methods=["GET"])
def take_quiz_page(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found."}), 404

    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    for q in questions:
        q.options = q.get_options()

    return render_template("take_quiz.html", quiz=quiz, questions=questions)

@routes.route("/quizzes", methods=["GET"])
def get_quizzes():
    # Get a list of quizzes (method open to all)
    quizzes = Quiz.query.all()
    return jsonify([{"id": q.id, "name": q.name, "quiz_code": q.quiz_code} for q in quizzes])

@routes.route("/quizzes/<int:quiz_id>/participants", methods=["GET"])
def get_participants(quiz_id):
    # Returns a list of students
    participants = Participant.query.filter_by(quiz_id=quiz_id).all()
    if not participants:
        return jsonify({"message" : "No participants found"}), 404
    
    participant_list = [{"name" : p.name, "score" : p.score} for p in participants]
    return jsonify(participant_list), 200

@routes.route("/join_quiz", methods=["GET", "POST"])
def join_quiz():
    if request.method == "GET":
        return render_template("join_quiz.html")

    elif request.method == "POST":
        quiz_code = request.form.get("quiz_code")
        name = request.form.get("name")

        if not quiz_code or not name:
            return jsonify({"error": "Quiz code and name are required."}), 400

        quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
        if not quiz:
            return jsonify({"error": "Invalid quiz code."}), 404

        session["quiz_id"] = quiz.id
        session["participant_name"] = name

        existing_participant = Participant.query.filter_by(quiz_id=quiz.id, name=name).first()
        if not existing_participant:
            participant = Participant(quiz_id=quiz.id, name=name)
            db.session.add(participant)
            db.session.commit()

        return redirect(f"/take_quiz/{quiz.id}")
    
@routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")

    elif request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Set role to 'teacher' by default or via hidden field
        role = "teacher"

        if not username or not email or not password:
            return jsonify({"error": "All fields are required."}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists."}), 400

        user = User(name=username, email=email, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("teacher_dashboard"))
        
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            access_token = create_access_token(identity=str(user.id))
            
            response = make_response(redirect(url_for('routes.dashboard')))
            set_access_cookies(response, access_token)

            return response

        return render_template("login.html", error="Invalid credentials.")
    
@routes.route("/logout", methods=["POST"])
def logout():
    response = redirect("/")
    unset_jwt_cookies(response)
    session.clear()
    return response

@routes.route("/")
def home():
    return render_template("index.html")

@routes.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or user.role != 'teacher':
        return render_template('dashboard.html', quizzes=[], user=None)

    quizzes = Quiz.query.filter_by(teacher_id=user.id).all()

    return render_template('dashboard.html', quizzes=quizzes, user=user)