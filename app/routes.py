from flask import Blueprint, request, jsonify, render_template, session, url_for
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

@routes.route("/quizzes", methods=["POST"])
def create_quiz():
    """
    Creates a quiz -- api for teacher only
    """
    auth_error = check_api_key()
    if auth_error:
        return auth_error

    data = request.get_json()
    quiz_code = generate_quiz_code()
    
    quiz = Quiz(name=data["name"], teacher_id=data["teacher_id"], quiz_code=quiz_code)
    db.session.add(quiz)
    db.session.commit()
    return jsonify({"message": "Quiz created",
                    "quiz_code" : quiz_code}), 201

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
    
    participant_list = [{"student_id" : p.student_id, "score" : p.score} for p in participants]
    return jsonify(participant_list), 200

@routes.route("/join_quiz", methods=["GET", "POST"])
def join_quiz():
    if request.method == "GET":
        # Serve the join quiz page
        return render_template("join_quiz.html")
    
    elif request.method == "POST":
        data = request.get_json()
        quiz_code = data.get("quiz_code")
        name = data.get("name")

        if not quiz_code or not name:
            return jsonify({"error": "Quiz code and name are required."}), 400

        # Check if the quiz exists
        quiz = Quiz.query.filter_by(quiz_code=quiz_code).first()
        if not quiz:
            return jsonify({"error": "Invalid quiz code."}), 404

        # Store participant information in session
        session["quiz_id"] = quiz.id
        session["participant_name"] = name

        # Check if participant already exists
        existing_participant = Participant.query.filter_by(quiz_id=quiz.id, name=name).first()
        if not existing_participant:
            participant = Participant(quiz_id=quiz.id, name=name)
            db.session.add(participant)
            db.session.commit()

        # Return the redirect URL to the quiz page
        return jsonify({
            "message": "Joined quiz successfully. Redirecting...",
            "redirect_url": f"/take_quiz/{quiz.id}"
        }), 200

@routes.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        # Serve the signup page
        return render_template("signup.html")

    elif request.method == "POST":
        # Process the signup form submission
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        # Validate inputs
        if not name or not email or not password or not role:
            return jsonify({"error": "All fields (name, email, password, role) are required."}), 400

        if role.lower() != "teacher":
            return jsonify({"error": "Only teachers can sign up."}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already exists."}), 400

        # Create and save the user with hashed password
        user = User(name=name, email=email, role=role.lower())
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Teacher signed up successfully", "user_id": user.id}), 201
        
@routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    elif request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password are required."}), 400

        user = User.query.filter_by(email=email).first()
        if user and user.verify_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            return jsonify({"message": "Login successful"}), 200

        return jsonify({"error": "Invalid email or password"}), 401
    
@routes.route("/logout", methods=["POST"])
def logout():
    db.session.clear()
    return jsonify({"message": "Logged out successfully"}), 200

@routes.route("/")
def home():
    return render_template("index.html")