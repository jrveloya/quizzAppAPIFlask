FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 5000
# the port that my flask app is running on

CMD [ "python", "main.py" ]