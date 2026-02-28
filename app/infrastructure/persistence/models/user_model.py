import os
import json
import base64

from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class UserModel(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    role = db.Column(db.String(150))
    permissions = db.Column(db.String(600))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    otp_secret = db.Column(db.String(16))
    otp_enabled = db.Column(db.Boolean(), default=False) 
    otp_setup = db.Column(db.Boolean(), default=False) 

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}', date_created='{self.date_created}')>"

    def __str__(self):
        return f"User {self.username} (ID: {self.id}, Role: {self.role}, Created: {self.date_created})"

    # TODO: I think this should be moved into SqlAlchemyUserRepository, still thinking about it...
    def __init__(self, **kwargs):
        super(UserModel, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random secret
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

