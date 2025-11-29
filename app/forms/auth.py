# TODO: Breakup each of these into its own class file eventually.

import re
import os
import json
import getpass

from flask_wtf import FlaskForm

from wtforms.validators import (
    InputRequired,
    Length,
    Regexp,
    ValidationError,
    EqualTo,
    Optional,
)
from wtforms import (
    PasswordField,
    RadioField,
    SubmitField,
    StringField,
    IntegerField,
    BooleanField,
    SelectMultipleField,
)

from app.models import User, GameServer
from .helpers import ValidateOTPCode

USERNAME = getpass.getuser()

VALID_HEX_COLOR = r"^#(?:[0-9a-fA-F]{1,2}){3}$"

# Input bad char regex stuff.
BAD_CHARS = r'^[^ \$\'"\\#=\[\]!<>|;{}()*,?~&]*$'
BAD_CHARS_MSG = (
    "Input contains invalid characters. "
    + r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &"""
)

# Only open read in the accepted_cfgs.json at app startup (is static).
with open("json/accepted_cfgs.json", "r") as gs_cfgs:
    VALID_CONFIGS = json.load(gs_cfgs)["accepted_cfgs"]

## Helper Classes

class ServerExists:
    """Validator that checks if a server ID exists in the database"""

    def __init__(self, message="Invalid game server ID!"):
        self.message = message

    def __call__(self, form, field):
        server = GameServer.query.filter_by(id=field.data).first()
        if server is None:
            raise ValidationError(self.message)


class ValidConfigFile:
    """Validator that checks if a config path is in the accepted list"""

    def __init__(self, message="Invalid config file name!"):
        self.message = message

    def __call__(self, form, field):
        cfg_file = os.path.basename(field.data)
        if cfg_file not in VALID_CONFIGS:
            raise ValidationError(self.message)


class ValidateOTPCode:
    """Validator that checks if 2fa otp code in form is valid"""

    def __init__(self, user_id=None, message="Invalid otp code!"):
        self.message = message
        self.user_id = user_id

    def __call__(self, form, field):
        if not hasattr(form, 'user_id') or not form.user_id:
            raise ValidationError("User ID is required for OTP validation")

        user = User.query.filter_by(id=form.user_id).first()

        if not user:
            raise ValidationError("User not found")

        if not user.verify_totp(field.data):
            raise ValidationError(self.message)


## Main Forms

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


class OTPSetupForm(FlaskForm):
    user_id = None

    otp_code = IntegerField(
        "OTP Code",
        validators=[
            InputRequired(),
            ValidateOTPCode(),
        ],
    )

    submit = SubmitField("Submit", render_kw={"class": "btn btn-outline-primary"})


class ConditionalPasswordRequired:
    """Validator that makes password required only if changing password or creating new user"""

    def __init__(self, message=None):
        if not message:
            message = "Password is required when changing password or creating new user"
        self.message = message

    def __call__(self, form, field):
        # Skip validation if neither condition is true
        if (
            not form.change_username_password.data
            and form.selected_user.data != "newuser"
        ):
            return

        # Check if password is empty when required
        if not field.data:
            raise ValidationError(self.message)

        # Additional password complexity checks
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
            raise ValidationError(
                "Password must contain at least one special character"
            )


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


    # Permissions
    enable_otp = BooleanField("Enable Two Factor Auth")
    install_servers = BooleanField("Can Install New Game Servers")
    add_servers = BooleanField("Can Add/Edit Existing Game Servers")
    mod_settings = BooleanField("Can Modify Web-LGSM Settings Page")
    edit_cfgs = BooleanField("Can Edit Game Server Configs")
    edit_jobs = BooleanField("Can Edit Game Server Jobs")
    delete_server = BooleanField("Can Delete Game Servers")

    # Controls and servers (using SelectMultipleField for multiple checkboxes)
    controls = SelectMultipleField("Allowed Controls", choices=[], coerce=str)
    server_ids = SelectMultipleField("Allowed Game Servers", choices=[], coerce=str)

