from ..base import *
from wtforms import PasswordField, SelectMultipleField
from .validators.conditional_password import ConditionalPasswordRequired

class EditUsersForm(FlaskForm):
    selected_user = StringField("Selected User")
    change_username_password = BooleanField("Change Password", default=False)

    # Username and password fields
    username = StringField(
        "Username",
        validators=[
            InputRequired(),
            Length(min=4, max=150),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ],
        render_kw={"placeholder": "Enter Username", "class": "form-control"},
    )
    password1 = PasswordField(
        "Password",
        validators=[
            ConditionalPasswordRequired(),
        ],
        render_kw={"placeholder": "Enter Password", "class": "form-control"},
    )
    password2 = PasswordField(
        "Confirm Password",
        validators=[EqualTo("password1", message="Passwords must match")],
        render_kw={"placeholder": "Retype Password", "class": "form-control"},
    )

    # Admin toggle
    is_admin = RadioField(
        "User Type",
        choices=[
            ("true", "Admin User - Can do anything in the web interface"),
            ("false", "Regular User - Configure limited user permissions below"),
        ],
        default="false",
    )


    # Basic bool perms
    enable_otp = BooleanField("Enable Two Factor Auth")

    route_choices = [
        ("add", "Can add/edit existing game servers"),
        ("controls", "Can access control panel for allowed game server(s)"),
        ("install", "Can install new game servers"),
        ("settings", "Can modify web-lgsm settings page"),
        ("files", "Can browse and read files (file manager - readonly)"),
        ("files_edit", "Can edit, rename, upload, & delete files (file manager - full access)"),
        ("jobs", "Can edit game server jobs"),
        ("delete", "Can delete game servers"),
    ]

    # List of options perms (using SelectMultipleField for multiple checkboxes)
    routes = SelectMultipleField("Basic Permissions", choices=route_choices, coerce=str)
    controls = SelectMultipleField("Allowed Controls", choices=[], coerce=str)
    server_ids = SelectMultipleField("Allowed Game Servers", choices=[], coerce=str)
