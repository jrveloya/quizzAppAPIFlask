# Quiz API

I have left test cases for you to run. To summarize, they are enumerated below:

1. test_create_user
   - Verifies that a user (teacher or student) can be created successfully.

2. test_create_quiz
   - Ensures that a teacher can create a quiz when providing a valid API key.

3. test_create_quiz_unauthorized
   - Ensures that quiz creation fails if the API key is missing or incorrect.

4. test_add_question
   - Confirms that a teacher can add a question to a quiz using the API key.

5. test_add_question_unauthorized
   - Ensures that adding a question fails if the API key is missing or incorrect.

6. test_get_quizzes
   - Retrieves all available quizzes and verifies the response.

7. test_add_participant
   - Ensures that a student can take a quiz and have their score recorded.

8. test_get_participants
   - Verifies that a teacher can retrieve the list of students who took a quiz.