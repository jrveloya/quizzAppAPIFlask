from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .database import db
from .config import Config
from .routes import routes

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="memory://"  # Change to "redis://localhost:6379" for production
)

app.register_blueprint(routes) 