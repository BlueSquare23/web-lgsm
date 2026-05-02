from ..base import *
from wtforms import PasswordField, SelectMultipleField
from .validators.conditional_password import ConditionalPasswordRequired

class EditUsersForm(FlaskForm):
    selected_user = StringField("Selected User")
    change_username_password = BooleanField(default=False)

    username = StringField(
        validators=[InputRequired(), Length(min=4, max=150), Regexp(BAD_CHARS, message=BAD_CHARS_MSG)],
    )

    password1 = PasswordField(validators=[ConditionalPasswordRequired()])
    password2 = PasswordField(validators=[EqualTo("password1", message="Passwords must match")])

    is_admin = RadioField(
        choices=[
            ("true", "Admin User"),
            ("false", "Regular User"),
        ],
        default="false",
    )

    enable_otp = BooleanField()

    route_choices = [
        ("add", "Can add/edit existing game servers"),
        ("controls", "Can access control panel"),
        ("install", "Can install new servers"),
        ("settings", "Can modify settings"),
        ("edit", "Can edit configs"),
        ("jobs", "Can edit jobs"),
        ("delete", "Can delete servers"),
    ]

    routes = SelectMultipleField(choices=route_choices, coerce=str)
    controls = SelectMultipleField(choices=[], coerce=str)
    server_ids = SelectMultipleField(choices=[], coerce=str)
