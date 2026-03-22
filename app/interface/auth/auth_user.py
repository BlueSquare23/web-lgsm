from flask_login import UserMixin

from app.container import container

class AuthUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

        user = container.get_user().execute(user_id)
        self.__dict__.update(user.__dict__)

    def get_id(self):
        return str(self.id)

