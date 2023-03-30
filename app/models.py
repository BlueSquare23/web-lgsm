from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))

class MetaData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    app_install_path = db.Column(db.String(150), unique=True)

class GameServer(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    # User supplied unique name.
    install_name = db.Column(db.String(150), unique=True)
    install_path = db.Column(db.String(150))
    # The name of the lgsm game server script. For example, 'gmodserver'.
    script_name = db.Column(db.String(150))

class ControlSet(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    install_name = db.Column(db.String(150), unique=True)
    short_cmds = db.Column(db.String(150))
    long_cmds = db.Column(db.String(250))
    descriptions = db.Column(db.String(500))

class InstallServer(db.Model):
    id =  db.Column(db.Integer, primary_key=True)
    short_names = db.Column(db.String(150))
    long_names = db.Column(db.String(250))
