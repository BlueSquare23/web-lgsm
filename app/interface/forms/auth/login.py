from ..base import *
from wtforms import PasswordField, IntegerField

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            InputRequired(message="Missing required form field(s)!"),
            Length(min=4, max=20),
        ],
        render_kw={"placeholder": "Enter Username", "class": "form-control"},
    )

    password = PasswordField(
        "Password",
        validators=[
            InputRequired(message="Missing required form field(s)!"),
            Length(min=12, max=150),
        ],
        render_kw={"placeholder": "Enter Password", "class": "form-control"},
    )

    otp_code = IntegerField(
        "OTP Code",
        validators=[
            Optional(),  # We validate in route code for login totp validation
        ],
    )

    submit = SubmitField("Login", render_kw={"class": "btn btn-outline-primary"})

