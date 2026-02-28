import os
import json
import base64
import onetimepass

from app.domain.repositories.user_repo import UserRepository
from app.domain.entities.user import User
from app.infrastructure.persistence.models.user_model import UserModel
from app import db

class SqlAlchemyUserRepository(UserRepository):

    def add(self, user):
        model = UserModel(
            id = user.id,
            username = user.username,
            password = user.password,
            role = user.role,
            permissions = user.permissions,
            otp_secret = user.otp_secret,
            otp_enabled = user.otp_enabled
        )
        db.session.add(model)
        db.session.commit()
        return model.id


    def update(self, user):
        model = UserModel.query.filter_by(id=user.id).first()

        # If user doesn't exist, add them.
        if model == None:
            return self.add(user)

        for key, value in user.__dict__.items():
            setattr(model, key, value)

        db.session.commit()
        return True


    def get(self, user_id):
        """Convert user_id into User entity"""
        model = UserModel.query.filter_by(id=user_id).first()

        if model == None:
            return None

        # Convert model object to Job entity.
        data = {
            'id': model.id,
            'username': model.username,
            'password': model.password,
            'role': model.role,
            'permissions':model.permissions,
            'otp_secret': model.otp_secret,
            'otp_enabled': model.otp_enabled,
            'otp_setup': model.otp_setup,

        }
        user = User(**data)

        return user


    def query(self, key, value):
        """Get User entity by key value"""
        model = UserModel.query.filter_by(**{key: value}).first()

        if model == None:
            return None

        # Use existing get user to convert model id to domain User entity.
        return self.get(model.id)


    def delete(self, user_id):
        model = UserModel.query.filter_by(id=user_id).first()

        if not model:
            return False

        db.session.delete(model)
        db.session.commit()
        return True


    def list(self):
        """
        Fetches list of all users from DB and converts them to list of User
        entity objects.
        """
        all_models = UserModel.query.all()
        all_users = []

        for model in all_models:
            all_users.append(self.get(model.id))
            
        return all_users


    def to_domain(self, model):
        """
        Converts sqlalchemy model object into domain layer representation.
        Even though this is basically just a get, its nice to have an explicit
        wrapper name to provide context.
        """
        model = UserModel.query.filter_by(id=model.id).first()
        if not model:
            return None

        return self.get(model.id)


    def get_totp_uri(self, user_id):
        user = self.get(user_id)
        return 'otpauth://totp/Web-LGSM:{0}?secret={1}&issuer=Web-LGSM' \
            .format(user.username, user.otp_secret)


    def verify_totp(self, user_id, token):
        user = self.get(user_id)
        return onetimepass.valid_totp(token, user.otp_secret)


    def has_access(self, user_id, route, server_id=None):
        """
        Check's if user has permissions to access various routes.
    
        Args:
            route (string): The route to apply permissions controls to.
            server_id (string): Game server id to check user has access to.
                                  Only matters for controls & delete routes.
    
        Returns:
            bool: True if user has appropriate perms, False otherwise.
    
        """
        user = self.get(user_id)
        if not user:
            return False

        # Admins can always do anything.
        if user.role == "admin":
            return True

        valid_routes = ["install", "edit", "add", "delete", "settings", "controls",
                        "update-console", "cmd-output", "server-statuses", "jobs"]

        assert route in valid_routes, f"Invalid route: {route}"

        user_perms = json.loads(user.permissions)

        # Does user have access to server_id?
        if server_id:
            if server_id not in user_perms["server_ids"]:
                return False

        # Does user have access to route?
        if route not in user_perms["routes"]:
            return False

        # Special case for update-console, user needs access to console control too.
        if route == "update-console":
            if "console" not in user_perms["controls"]:
                return False

        return True

