from ..base import *
from wtforms import PasswordField
import re

class SetupForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG.replace("Input", "Username")),
            Length(min=4, max=20),
        ],
    )

    password1 = PasswordField(validators=[InputRequired(), Length(min=12, max=150)])
    password2 = PasswordField(validators=[InputRequired(), Length(min=12, max=150)])

    enable_otp = BooleanField()
    submit = SubmitField("Submit")

    def validate_password1(self, field):
        password = field.data
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError("Password must contain at least one special character")

    def validate_password2(self, field):
        if self.password1.data != field.data:
            raise ValidationError("Passwords do not match")
