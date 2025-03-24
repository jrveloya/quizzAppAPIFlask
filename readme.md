# Flask Quiz API

## Overview

The Flask Quiz API is a web application that allows teachers to create and manage quizzes with different types of questions, and students to take quizzes using unique access codes. This project uses containerization for deployment, ensuring consistency across different environments and easy scalability. It is designed with security and best practices in mind, deploying on AWS EC2 using Docker.

## Features

- **Teacher Features**: Create quizzes, add multiple choice and true/false questions, view quiz results.
- **Student Features**: Join quizzes using a unique code, submit answers, view scores.
- **Security Features**: API key authentication for teacher endpoints, password hashing with SHA-256 and salt for account security.
- **Deployment**: Containerized using Docker for easy deployment and scalability on AWS EC2.

## API Documentation

### Authentication

- **POST /signup** - Registers a new teacher with email and password.
- **POST /login** - Authenticates a teacher and creates a session.
- **POST /logout** - Destroys the session and logs out the user.

### Quiz Management

- **POST /quizzes** - Allows authenticated teachers to create a new quiz.
- **GET /quizzes** - Retrieves all quizzes created by the logged-in teacher.

### Question Management

- **POST /quizzes/{quiz_id}/questions** - Adds questions to a specified quiz.
- **GET /quizzes/{quiz_id}/questions** - Retrieves questions for a specified quiz.

### Quiz Participation

- **POST /join_quiz** - Allows students to join a quiz using a unique code.
- **POST /quizzes/{quiz_id}/submit** - Allows students to submit their answers and calculates the score.

## Installation

To run this project locally, follow these steps:

1. **Clone the repository:**
`git clone https://github.com/jrveloya/quizzAppAPIFlask.git`
2. **Build the Docker image:**
`docker run -p 5000:5000 quiz-app`

## Deployment on AWS EC2
1. **Set up an EC2 instance** with Docker installed.
2. **Pull the Docker image from Docker Hub:**
`docker pull jrveloya/quiz-app`
3. **Run the Docker container on the EC2 instance:**
`docker run -d -p 80:5000 jrveloya/quiz-app`

## Security Implementations

- **API Key Authentication:** Secure API endpoints accessible only to authenticated teachers.
- **Password Hashing:** Use SHA-256 hashing with salt to secure teacher passwords.
- **AWS Security Groups:** Configure to only allow traffic on necessary ports to secure the EC2 instance.

## CI/CD Integration

GitHub Actions is used to automate the testing and deployment pipeline:
- **Automated Testing:** Run tests for each commit using pytest.
- **Docker Build:** Automatically build Docker images and push to Docker Hub upon successful tests.
- **Deployment:** Automated scripts to deploy the latest Docker image to AWS EC2.

## Built With

- **Python** - The programming language used.
- **Flask** - The web framework.
- **SQLAlchemy** - The ORM used for database interactions.
- **Docker** - Used for containerization and deployment.
- **AWS EC2** - Cloud platform for deployment.
- **GitHub Actions** - CI/CD tool used for automated testing and deployment.


