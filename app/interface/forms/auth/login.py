from ..base import *
from wtforms import PasswordField, IntegerField

class LoginForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[InputRequired(message="Missing required form field(s)!"), Length(min=4, max=20)],
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(message="Missing required form field(s)!"), Length(min=12, max=150)],
    )

    otp_code = IntegerField(validators=[Optional()])

    submit = SubmitField("Login")
