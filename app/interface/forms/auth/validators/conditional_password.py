import re
from ...base import ValidationError

class ConditionalPasswordRequired:
    def __init__(self, message=None):
        self.message = message or "Password is required when changing password or creating new user"

    def __call__(self, form, field):
        if (
            not form.change_username_password.data
            and form.selected_user.data != "newuser"
        ):
            return

        if not field.data:
            raise ValidationError(self.message)

        password = field.data

        if len(password) < 12 or len(password) > 150:
            raise ValidationError("Password must be at least 12 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError("Password must contain at least one special character")
