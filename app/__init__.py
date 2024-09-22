import os
import sys
import json
import logging
from flask import Flask
from pathlib import Path
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from logging.config import dictConfig
from flask.logging import default_handler

# Prevent creation of __pycache__. Cache messes up auth.
sys.dont_write_bytecode = True

db = SQLAlchemy()
DB_NAME = "database.db"

env_path = Path(".") / ".secret"
load_dotenv(dotenv_path=env_path)
SECRET_KEY = os.environ["SECRET_KEY"]


def main():
    # Setup logging.
    log_level_map = {
        'debug': logging.DEBUG,        # Most verbose (Level 1).
        'info': logging.INFO,          # General operational info (Level 2).
        'warning': logging.WARNING     # Warnings and above (Level 3).
    }

    if "DEBUG" in os.environ:
        # Get log_level from env var, default to info if none set.
        log_level_str = os.getenv("LOG_LEVEL", "info").lower()
        log_level = log_level_map.get(log_level_str, logging.INFO)
        dictConfig({
            'version': 1,
            'formatters': {'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }},
            'handlers': {'wsgi': {
                'class': 'logging.StreamHandler',
                'stream': 'ext://flask.logging.wsgi_errors_stream',
                'formatter': 'default'
            }},
            'root': {
                'level': log_level,
                'handlers': ['wsgi']
            }
        })
    current_log_level = logging.getLogger().getEffectiveLevel()
    
    # Print the human-readable log level name
    print(f"Root logger level: {logging.getLevelName(current_log_level)}")

    # Initialize app.
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{app.root_path}/{DB_NAME}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.logger.removeHandler(default_handler)

    # Pull in our views route(s).
    from .views import views

    app.register_blueprint(views, url_prefix="/")

    # Pull in our auth route(s).
    from .auth import auth

    app.register_blueprint(auth, url_prefix="/")

    # Initialize DB.
    from .models import User, GameServer

    with app.app_context():
        db.create_all()
        print(" * Database Loaded!")

    # Setup LoginManager.
    login_manager = LoginManager()
    # Redirect to auth.login if not already logged in.
    login_manager.login_view = "auth.login"
    login_manager.login_message = None
    login_manager.init_app(app)

    # Decorator to set up login session.
    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

    # Filter for jinja2 json parsing for user permissions.
    @app.template_filter("from_json")
    def from_json_filter(s):
        return json.loads(s)

    return app
