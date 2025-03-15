document.addEventListener('DOMContentLoaded', () => {

    // Create Quiz (Teacher Only)
    const quizForm = document.getElementById('create-quiz-form');
    if (quizForm) {
        quizForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const name = document.getElementById('quizName').value;
            const teacherId = document.getElementById('teacherId').value;

            fetch('/quizzes', {
                method: 'POST',
                headers: { 
                    'X-API-KEY': 'SECRET_API_KEY_1234',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ name, teacher_id: teacherId })
            })
            .then(response => response.json())
            .then(data => {
                const responseMessage = document.getElementById('response-message');
                responseMessage.textContent = data.quiz_code 
                    ? `Quiz Created. Code: ${data.quiz_code}`
                    : (data.error || "An unexpected error occurred.");
                responseMessage.style.color = data.error ? 'red' : 'green';
            })
            .catch(error => {
                console.error('Error creating quiz:', error);
                document.getElementById('response-message').textContent = "An unexpected error occurred.";
                document.getElementById('response-message').style.color = "red";
            });
        });
    }

    // Join Quiz (Student)
    const joinQuizForm = document.getElementById('join-quiz-form');
    if (joinQuizForm) {
        joinQuizForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const quizCode = document.getElementById('quizCode').value;
            const name = document.getElementById('studentName').value;

            fetch('/join_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ quiz_code: quizCode, name })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                if (data.redirect_url) {
                    window.location.href = data.redirect_url;
                } else {
                    const responseMessage = document.getElementById('response-message');
                    responseMessage.textContent = data.message || data.error;
                    responseMessage.style.color = data.error ? 'red' : 'green';
                }
            })
            .catch(error => {
                const responseMessage = document.getElementById('response-message');
                responseMessage.textContent = error.error || "An unexpected error occurred.";
                responseMessage.style.color = "red";
                console.error('Error joining quiz:', error);
            });
        });
    }

    // Submit Quiz (Student)
    const submitQuizForm = document.getElementById('submit-quiz-form');
    if (submitQuizForm) {
        submitQuizForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const quizId = document.getElementById('quizId').value;
            const answers = {};

            const selectedAnswers = document.querySelectorAll('input[type="radio"]:checked');
            selectedAnswers.forEach(answer => {
                const questionId = answer.name.split('_')[1];
                answers[questionId] = answer.value;
            });

            fetch(`/quizzes/${quizId}/submit`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ answers })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                const responseMessage = document.getElementById('response-message');
                responseMessage.textContent = data.message || data.error;
                responseMessage.style.color = data.error ? 'red' : 'green';
            })
            .catch(error => {
                console.error('Error submitting quiz:', error);
                const responseMessage = document.getElementById('response-message');
                responseMessage.textContent = "An unexpected error occurred.";
                responseMessage.style.color = "red";
            });
        });
    }

    // Handle Teacher Signup
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const role = document.getElementById('role').value;

            fetch('/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, password, role })
            })
            .then(response => response.json())
            .then(data => {
                const responseMessage = document.getElementById('response-message');
                responseMessage.textContent = data.message || data.error;
                responseMessage.style.color = data.error ? 'red' : 'green';
            });
        });
    }

    // Handle Teacher Login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                document.getElementById('response-message').textContent = data.message;
                document.getElementById('response-message').style.color = 'green';
                setTimeout(() => {
                    window.location.href = '/';
                }, 1000);
            })
            .catch(error => {
                document.getElementById('response-message').textContent = error.error || "An unexpected error occurred.";
                document.getElementById('response-message').style.color = "red";
            });
        });
    }

    // Handle Logout
    const logoutButton = document.getElementById('logout-btn');
    if (logoutButton) {
        logoutButton.addEventListener('click', function () {
            fetch('/logout', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                window.location.href = '/login';
            });
        });
    }

});