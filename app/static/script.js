document.addEventListener('DOMContentLoaded', () => {
    // ==========================
    // CREATE QUIZ (TEACHER)
    // ==========================
    const quizForm = document.getElementById('create-quiz-form');
    const questionContainer = document.getElementById('question-container');
    const addQuestionBtn = document.getElementById('add-question-btn');
    let questionIndex = 0;

    function createQuestionBlock(index) {
        const wrapper = document.createElement('div');
        wrapper.className = 'question-block';
        wrapper.dataset.index = index;

        wrapper.innerHTML = `
            <hr>
            <label>Question:</label>
            <input type="text" name="question_text_${index}" required>

            <label>Type:</label>
            <select name="question_type_${index}">
                <option value="MC">Multiple Choice</option>
                <option value="TF">True/False</option>
            </select>

            <label>Options (comma separated):</label>
            <input type="text" name="options_${index}">

            <label>Answer:</label>
            <input type="text" name="answer_${index}" required>

            <button type="button" class="remove-question-btn">− Remove</button>
        `;

        wrapper.querySelector('.remove-question-btn').addEventListener('click', () => {
            wrapper.remove();
        });

        return wrapper;
    }

    if (addQuestionBtn) {
        addQuestionBtn.addEventListener('click', () => {
            const block = createQuestionBlock(questionIndex++);
            questionContainer.appendChild(block);
        });
    }

    if (quizForm) {
        quizForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const name = document.getElementById('quizName').value;
            const questionBlocks = document.querySelectorAll('.question-block');

            const questions = Array.from(questionBlocks).map(block => {
                const index = block.dataset.index;
                return {
                    question_text: block.querySelector(`[name="question_text_${index}"]`).value,
                    question_type: block.querySelector(`[name="question_type_${index}"]`).value,
                    options: block.querySelector(`[name="options_${index}"]`).value.split(',').map(opt => opt.trim()),
                    answer: block.querySelector(`[name="answer_${index}"]`).value
                };
            });

            fetch('/create_quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-KEY': 'SECRET_API_KEY_1234'
                },
                body: JSON.stringify({ name, questions })
            })
            .then(res => res.json())
            .then(data => {
                const message = document.getElementById('response-message');
                message.textContent = data.message || "Quiz submitted.";
                message.style.color = data.error ? 'red' : 'green';
            })
            .catch(err => {
                console.error(err);
                const message = document.getElementById('response-message');
                message.textContent = "An unexpected error occurred.";
                message.style.color = 'red';
            });
        });
    }

    // ==========================
    // JOIN QUIZ (STUDENT)
    // ==========================
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
                if (!response.ok) return response.json().then(err => { throw err; });
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
            });
        });
    }

    // ==========================
    // SUBMIT QUIZ (STUDENT)
    // ==========================
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
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answers })
            })
            .then(response => {
                if (!response.ok) return response.json().then(err => { throw err; });
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

    // ==========================
    // SIGNUP
    // ==========================
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

    // ==========================
    // LOGIN
    // ==========================
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
                if (!response.ok) return response.json().then(err => { throw err; });
                return response.json();
            })
            .then(data => {
                document.getElementById('response-message').textContent = data.message;
                document.getElementById('response-message').style.color = 'green';
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            })
            .catch(error => {
                document.getElementById('response-message').textContent = error.error || "An unexpected error occurred.";
                document.getElementById('response-message').style.color = "red";
            });
        });
    }

    // ==========================
    // LOGOUT
    // ==========================
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

    // ==========================
    // VIEW PARTICIPANTS
    // ==========================
    const participantButtons = document.querySelectorAll('[data-quiz-id]');
    participantButtons.forEach(button => {
        button.addEventListener('click', () => {
            const quizId = button.dataset.quizId;
            const container = document.getElementById(`participants-${quizId}`);

            if (container.style.display === 'block') {
                container.style.display = 'none';
                container.innerHTML = '';
                return;
            }

            fetch(`/quizzes/${quizId}/participants`)
                .then(response => {
                    if (!response.ok) throw new Error("No participants found.");
                    return response.json();
                })
                .then(data => {
                    if (!data.length) {
                        container.innerHTML = "<p>No participants yet.</p>";
                    } else {
                        const list = data.map(p => `<li>${p.name} - Score: ${p.score}</li>`).join('');
                        container.innerHTML = `<ul>${list}</ul>`;
                    }
                    container.style.display = 'block';
                })
                .catch(error => {
                    container.innerHTML = `<p style="color:red;">${error.message}</p>`;
                    container.style.display = 'block';
                });
        });
    });
});