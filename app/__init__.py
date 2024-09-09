import os
import sys
from flask import Flask
from pathlib import Path
from dotenv import load_dotenv
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

# Prevent creation of __pycache__. Cache messes up auth.
sys.dont_write_bytecode = True

db = SQLAlchemy()
DB_NAME = "database.db"

env_path = Path('.') / '.secret'
load_dotenv(dotenv_path=env_path)
SECRET_KEY = os.environ['SECRET_KEY']

def main():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.root_path}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

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
        print(" * Created Database!")

    # Setup LoginManager
    login_manager = LoginManager()
    # Redirect to auth.login if not already logged in.
    login_manager.login_view = "auth.login"
    login_manager.login_message = None
    login_manager.init_app(app)

    # Decorator to set up login session.
    @login_manager.user_loader
    def load_user(id):
        return db.session.get(User, int(id))

    return app
