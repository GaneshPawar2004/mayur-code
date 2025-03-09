import sys
import os

# Get the absolute path of the directory containing this script.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the parent directory to the Python path.
sys.path.append(os.path.join(script_dir, ".."))

# Necessary import statements
from flask import Flask, jsonify
from exts import db
from flask_jwt_extended import JWTManager
from flask_restx import Api
from flask_cors import CORS
from backend.routes.auth import auth_ns
from backend.routes.payment import payment_ns
from backend.routes.common import common_ns
from backend.routes.admin import admin_ns
from backend.routes.lesson import lesson_ns
from backend.routes.serve_static_media import media_ns
from backend.routes.user_features import user_features_ns
from backend.routes.dashboard import dashboard_ns
from backend.routes.social import social_ns
from backend.routes.content_management import content_management_ns
from backend.routes.cdp import cdp_ns
from backend.helpers.log_config import get_logger
from db_helper import db_url
from backend.helpers.utils import settings
from flask_mail import Mail, Message
from helpers.limiter import limiter
import json
from decimal import Decimal
from datetime import timedelta
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import ExpiredSignatureError
from werkzeug.exceptions import Unauthorized
from backend.routes.ai_toolbox_api import ai_toolbox_api_ns
from backend.routes.ai_toolbox_payment import ai_toolbox_payment_ns
#ganesh
from routes.follow_routes import follow_ns



logger = get_logger(name=__name__)
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


app = Flask(__name__)
app.secret_key = settings.secret_key  # For encrept & decrept session data on a server.
app.json_encoder = CustomJSONEncoder
# app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = settings.sqlalchemy_track_modifications


if os.environ.get('ENVIRONMENT') == 'production':
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    # CORS(app, resources={r"/api/*": {"origins": "https://app.aileela.com"}})
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=90)
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["https://aileela.com", "https://www.aileela.com"], "allow_headers": "*"}})
else:
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=60)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=2)
    # CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})
    CORS(app, supports_credentials=True, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://aileela.com"], "allow_headers": "*"}})

db.init_app(app)


# app.config['MAIL_SERVER'] = 'smtp.google.com'  # The mail server
# app.config['MAIL_PORT'] = 587                  # The mail server port
# app.config['MAIL_USE_TLS'] = True              # Enable TLS
# app.config['MAIL_USE_SSL'] = False             # Disable SSL
# app.config['MAIL_USERNAME'] = 'daminimsurwase@gmail.com'  # Your email
# app.config['MAIL_PASSWORD'] = 'Damini@05#'           # Your email password
# app.config['MAIL_DEFAULT_SENDER'] = 'ai@aileela.com' # Default sender
# mail = Mail(app)
# JWTManager(app)

app.config['JWT_SECRET_KEY'] = settings.jwt_secret_key
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
jwt = JWTManager(app)
limiter.init_app(app)

# @jwt.token_in_blocklist_loader
# def check_if_token_in_blacklist(jwt_header, jwt_payload):
#     jti = jwt_payload["jti"]
#     token = BlacklistedToken.query.filter_by(jti=jti).first()
#     return token is not None

@app.errorhandler(JWTExtendedException)
def handle_jwt_extended_error(e):
    if isinstance(e, ExpiredSignatureError):
        return jsonify({"message": "Token has expired, please log in again."}), 401
    else:
        # Handle other JWTExtendedException errors
        return jsonify({"message": "JWT error: {}".format(str(e))}), 500

# class UserNotFoundException(Exception):
#     pass

# @app.errorhandler(UserNotFoundException)
# def handle_user_not_found_exception(error):
#     logger.error(f"User not found: {error}")
#     # Returning a 401 Unauthorized response
#     return jsonify({"error": "User not found. Please login again.", "code": "USER_NOT_FOUND"}), Unauthorized.code

api = Api(app, prefix='/api', doc='/api/docs') # Useful for show swagger UI documentation.

# Define namespaces
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(payment_ns, path='/payment')
api.add_namespace(common_ns, path='/common')
api.add_namespace(admin_ns, path='/admin')
api.add_namespace(user_features_ns, path='/user-features')
api.add_namespace(lesson_ns, path='/lesson')
api.add_namespace(media_ns, path='/media')
api.add_namespace(dashboard_ns, path='/dashboard')
api.add_namespace(social_ns, path='/social')
api.add_namespace(content_management_ns, path='/cms')
api.add_namespace(cdp_ns, path='/cdp')
api.add_namespace(ai_toolbox_api_ns, path='/ai_toolbox_api')
api.add_namespace(ai_toolbox_payment_ns, path='/ai_toolbox_payment')
# api.add_namespace(section_ns, path='/sections')
# api.add_namespace(menus_ns)
# api.add_namespace(api_ns)
# api.add_namespace(rzp_ns)
api.add_namespace(follow_ns, path="/api/follow")#ganesh
