import os
import json
import base64
import onetimepass

from app import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
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

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.otp_secret is None:
            # generate a random secret
            self.otp_secret = base64.b32encode(os.urandom(10)).decode('utf-8')

    def get_totp_uri(self):
        return 'otpauth://totp/Web-LGSM:{0}?secret={1}&issuer=Web-LGSM' \
            .format(self.username, self.otp_secret)

    def verify_totp(self, token):
        return onetimepass.valid_totp(token, self.otp_secret)


    def has_access(self, route, server_id=None):
        """
        Check's if user has permissions to access various routes.
    
        Args:
            route (string): The route to apply permissions controls to.
            server_id (string): Game server id to check user has access to.
                                  Only matters for controls & delete routes.
    
        Returns:
            bool: True if user has appropriate perms, False otherwise.
    
        """
        # Admins can always do anything.
        if self.role == "admin":
            return True

        valid_routes = ["install", "edit", "add", "delete", "settings", "controls",
                        "update-console", "server-statuses", "jobs"]

        assert route in valid_routes, f"Invalid route: {route}"

        user_perms = json.loads(self.permissions)

        # Does user have access to server_id?
        if server_id:
            if server_id not in user_perms["server_ids"]:
                return False

        # Does user have access to route?
        if route not in user_perms:
            return False

        # Special case for update-console, user needs access to console control too.
        if route == "update-console":
            if "console" not in user_perms["controls"]:
                return False

        return True

