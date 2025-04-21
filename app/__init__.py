from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from .database import db
from .config import Config
from .routes import routes

jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")  # or redis:// for prod

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY

db.init_app(app)
jwt.init_app(app)
limiter.init_app(app)

app.register_blueprint(routes)

# ✅ Register context processor AFTER app is created
@app.context_processor
def inject_user():
    try:
        verify_jwt_in_request()
        user = get_jwt_identity()
        return {'current_user': user}
    except NoAuthorizationError:
        return {'current_user': None}