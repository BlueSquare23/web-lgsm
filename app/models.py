from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(150))
    permissions = db.Column(db.String(300))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())


class GameServer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Unique name.
    install_name = db.Column(db.String(150), unique=True)
    # Install path.
    install_path = db.Column(db.String(150))
    # The name of the lgsm game server script. For example, 'gmodserver'.
    script_name = db.Column(db.String(150))
    # Username of game server user.
    username = db.Column(db.String(150))
