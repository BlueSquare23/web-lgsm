from ..base import *
import re

class SetupForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(message="Missing required form field(s)!"),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG.replace("Input", "Username")),
            Length(min=4, max=20),
        ],
        render_kw={"placeholder": "Enter Username", "class": "form-control"},
    )

    password1 = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Missing required form field(s)!"),
            Length(min=12, max=150),
        ],
        render_kw={"placeholder": "Enter Password", "class": "form-control"},
    )

    password2 = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(message="Missing required form field(s)!"),
            Length(min=12, max=150),
        ],
        render_kw={"placeholder": "Retype Password", "class": "form-control"},
    )

    enable_otp = BooleanField("Enable Two Factor Auth")

    submit = SubmitField("Submit", render_kw={"class": "btn btn-outline-primary"})

    def validate_password1(self, field):
        password = field.data
        # Check for at least one uppercase letter
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter")
        # Check for at least one lowercase letter
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter")
        # Check for at least one digit
        if not re.search(r"[0-9]", password):
            raise ValidationError("Password must contain at least one number")
        # Check for at least one special character
        if not re.search(r"[^A-Za-z0-9]", password):
            raise ValidationError(
                "Password must contain at least one special character"
            )

    def validate_password2(self, field):
        if self.password1.data != field.data:
            raise ValidationError("Passwords do not match")

