import os
import sys
import json
import logging
from flask import Flask
from pathlib import Path
from dotenv import load_dotenv
from logging.config import dictConfig
from flask.logging import default_handler
from flask_swagger_ui import get_swaggerui_blueprint

# Import extensions
from .extensions import db, login_manager, migrate, cache

# Prevent creation of __pycache__. Pycache messes up auth.
sys.dont_write_bytecode = True

DB_NAME = "database.db"

env_path = Path(".") / ".secret"
load_dotenv(dotenv_path=env_path)
SECRET_KEY = os.environ["SECRET_KEY"]
SWAGGER_URL = "/docs"
API_URL = "/api/spec"

def setup_logging():
    """Configure logging settings"""
    log_level_map = {
        "info": logging.INFO,
        "warning": logging.WARNING,
        "debug": logging.DEBUG,
    }

    # Get log_level from env var, default to info if none set.
    log_level_str = os.getenv("LOG_LEVEL", "info").lower()
    log_level = log_level_map.get(log_level_str, logging.INFO)

    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
                },
                "audit": {
                    "format": "[%(asctime)s] AUDIT: %(message)s",
                }
            },
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://flask.logging.wsgi_errors_stream",
                    "formatter": "default",
                },
                "audit_file": {
                    "class": "logging.FileHandler",
                    "filename": "logs/audit.log",
                    "formatter": "audit",
                }
            },
            "loggers": {
                "audit": {
                    "level": "INFO",
                    "handlers": ["audit_file"],
                    "propagate": False,
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["wsgi"]
            },
        }
    )

    current_log_level = logging.getLogger().getEffectiveLevel()
    print(f"Root logger level: {logging.getLevelName(current_log_level)}")

def register_extensions(app):
    """Register Flask extensions with the app"""
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    cache.init_app(app)

    # Setup LoginManager
    login_manager.login_view = "auth.login"
    login_manager.login_message = None
    login_manager.init_app(app)

def register_blueprints(app):
    """Register blueprints with the app"""
    from .views import views
    from .auth import auth
    from .api import api_bp

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Register Swagger UI blueprint
    swagger_ui = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            "app_name": "Web-LGSM API",
            "validatorUrl": None,
            "displayRequestDuration": True,
            "docExpansion": "none",
            "persistAuthorization": True,
            "supportedSubmitMethods": ["get", "post", "put", "delete", "patch"],
            "securityDefinitions": {
                "cookieAuth": {
                    "type": "apiKey",
                    "name": "session",
                    "in": "cookie",
                    "description": "Session cookie for authentication",
                }
            },
        },
    )
    app.register_blueprint(swagger_ui)

def register_template_filters(app):
    """Register custom template filters"""
    @app.template_filter("from_json")
    def from_json_filter(s):
        return json.loads(s)

def register_user_loader():
    """Register the user loader for Flask-Login"""
    from .models import User

    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

def create_app():
    """Application factory function"""
    # Setup logging first
    setup_logging()

    # Initialize app
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["REMEMBER_COOKIE_SAMESITE"] = "Lax"

    # Remove default handler and add audit logger
    app.logger.removeHandler(default_handler)
    app.audit_logger = logging.getLogger('audit')

    # Add Jinja2 extension
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')

    # Register everything
    register_extensions(app)
    register_blueprints(app)
    register_template_filters(app)
    register_user_loader()

    return app
