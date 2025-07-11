import re
import os
import json
import getpass

from cron_converter import Cron
from flask_wtf import FlaskForm
from wtforms.widgets import ColorInput

from wtforms.validators import (
    InputRequired,
    AnyOf,
    Length,
    Regexp,
    NumberRange,
    ValidationError,
    EqualTo,
)
from wtforms import (
    Form,
    PasswordField,
    RadioField,
    SubmitField,
    SelectField,
    TextAreaField,
    StringField,
    IntegerField,
    BooleanField,
    HiddenField,
    SelectMultipleField,
)

from .utils import get_servers
from .models import *


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


class AddForm(FlaskForm):
    install_type = RadioField(
        "Installation Type",
        choices=[
            ("local", "Game server is installed locally"),
            ("remote", "Game server is installed on a remote machine"),
            ("docker", "Game server is in a docker container"),
        ],
        default="local",
        validators=[
            InputRequired(),
            AnyOf(
                ["local", "remote", "docker"],
                message="Invalid installation type selected.",
            ),
        ],
    )

    # Text inputs
    install_name = StringField(
        "Installation Title",
        render_kw={
            "class": "form-control",
            "placeholder": "Enter a unique name for this install",
        },
        validators=[
            InputRequired(),
            Length(
                max=150,
                message="Invalid input! Installation Title too long. Max 150 characters.",
            ),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ],
    )

    install_path = StringField(
        "Installation directory path",
        render_kw={
            "class": "form-control",
            "placeholder": "Enter the full path to the game server directory",
        },
        validators=[
            InputRequired(),
            Length(
                max=150,
                message="Invalid input! Installation directory path too long. Max 150 characters.",
            ),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ],
    )

    servers = get_servers()
    script_name = StringField(
        "LGSM script name",
        render_kw={
            "class": "form-control",
            "placeholder": 'Enter the name of the game server script. For example, "gmodserver"',
        },
        validators=[
            InputRequired(),
            Length(
                max=150,
                message="Invalid input! LGSM script name too long. Max 150 characters.",
            ),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
            AnyOf(servers, message="Invalid script name."),
        ],
    )

    username = StringField(
        "Game server system username",
        render_kw={
            "class": "form-control",
            "placeholder": 'Enter system user game server is installed under. For example, "coolguy123"',
        },
        validators=[
            Length(
                max=150, message="Invalid input! Username too long. Max 150 characters."
            ),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ],
    )

    install_host = StringField(
        "Remote server's IP address or hostname",
        render_kw={
            "class": "form-control",
            "placeholder": 'Enter remote server\'s IP address or hostname. For example, "gmod.domain.tld"',
        },
        validators=[
            Length(
                max=150,
                message="Invalid input! Install host too long. Max 150 characters.",
            ),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ],
    )


class ColorField(StringField):
    """Custom color field using HTML5 color input"""
    widget = ColorInput()


class SettingsForm(FlaskForm):
    # Color fields
    text_color = ColorField(
        "Output Text Color",
        validators=[
            InputRequired(),
            Regexp(VALID_HEX_COLOR, message="Invalid text color!"),
        ],
        render_kw={
            "class": "form-control form-control-color",
            "title": "Choose your color",
        },
    )

    graphs_primary = ColorField(
        "Stats Primary Color",
        validators=[
            InputRequired(),
            Regexp(VALID_HEX_COLOR, message="Invalid primary color!"),
        ],
        render_kw={
            "class": "form-control form-control-color",
            "title": "Choose your color",
        },
    )

    graphs_secondary = ColorField(
        "Stats Secondary Color",
        validators=[
            InputRequired(),
            Regexp(VALID_HEX_COLOR, message="Invalid secondary color!"),
        ],
        render_kw={
            "class": "form-control form-control-color",
            "title": "Choose your color",
        },
    )

    # Terminal settings
    terminal_height = IntegerField(
        "Default Terminal Height",
        validators=[InputRequired(), NumberRange(min=5, max=100)],
        default=10,
        render_kw={"class": "form-control", "min": "5", "max": "100"},
    )

    # Radio button options
    delete_user = RadioField(
        "Delete user on server delete",
        choices=[
            ("true", "Delete game server's system user on delete"),
            ("false", "Keep user on game server delete"),
        ],
        default="false",
        validators=[InputRequired()],
        render_kw={"class": "form-check-input", "onchange": "checkDelFiles()"},
    )

    remove_files = RadioField(
        "Remove files on delete",
        choices=[
            ("true", "Remove game server files on delete"),
            ("false", "Leave game server files on delete"),
        ],
        default="false",
        validators=[InputRequired()],
        render_kw={"class": "form-check-input", "onchange": "checkKeepUser()"},
    )

    install_new_user = RadioField(
        "User creation on install",
        choices=[
            ("true", "Setup new system user when installing new game servers"),
            ("false", f"Install new game servers under system user: {USERNAME}"),
        ],
        default="true",
        validators=[InputRequired()],
        render_kw={"class": "form-check-input"},
    )

    newline_ending = RadioField(
        "Newline termination",
        choices=[
            ("true", "Terminate lines with a newline (Classic web-lgsm term display)"),
            ("false", "Do not enforce newline termination (New web-lgsm term display)"),
        ],
        default="false",
        validators=[InputRequired()],
        render_kw={"class": "form-check-input"},
    )

    show_stderr = RadioField(
        "Error output display",
        choices=[
            ("true", "Show both stdout & stderr output streams merged"),
            ("false", "Show only stdout output stream, suppress stderr"),
        ],
        default="true",
        validators=[InputRequired()],
        render_kw={"class": "form-check-input"},
    )

    clear_output_on_reload = RadioField(
        "Terminal clearing behavior",
        choices=[
            ("true", "Clear web terminal when running new command"),
            ("false", "Do not clear web terminal after running command"),
        ],
        default="true",
        validators=[InputRequired()],
        render_kw={"class": "form-check-input"},
    )

    # Checkbox options
    show_stats = BooleanField(
        "Show Live Server Stats on Home Page", render_kw={"class": "form-check-input"}
    )

    purge_tmux_cache = BooleanField(
        "Delete local tmux socket file name cache",
        render_kw={"class": "form-check-input"},
    )

    update_weblgsm = BooleanField(
        "Check for and update the Web LGSM", render_kw={"class": "form-check-input"}
    )

    submit = SubmitField("Apply", render_kw={"class": "btn btn-outline-primary"})


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


# TODO: The below three classes for the edit page are very similar and could
# probably be more cleverly combined into one. I don't have the time to do that
# rn, so will figure that out another time. I just need a working edit page atm.
class UploadTextForm(FlaskForm):
    """Form for editing and saving config file content"""

    server_id = HiddenField(
        "Server ID",
        validators=[
            InputRequired(),
            ServerExists(),
        ],
    )
    cfg_path = HiddenField(
        "Config Path",
        validators=[
            InputRequired(),
            ValidConfigFile(),
        ],
    )
    file_contents = TextAreaField("File Contents", validators=[InputRequired()])
    save_submit = SubmitField("Save File 💾")


class DownloadCfgForm(FlaskForm):
    """Form for downloading config file"""

    server_id = HiddenField(
        "Server ID",
        validators=[
            InputRequired(),
            ServerExists(),
        ],
    )
    cfg_path = HiddenField(
        "Config Path",
        validators=[
            InputRequired(),
            ValidConfigFile(),
        ],
    )
    download_submit = SubmitField("Download Config File ⏬")


# Form instead of FlaskForm to bypass csrf validation, since just GET req to
# load page.
class SelectCfgForm(Form):
    """Form for selecting a config file to edit"""

    server_id = HiddenField(
        "Server ID",
        validators=[
            InputRequired(),
            ServerExists(),
        ],
    )
    cfg_path = HiddenField(
        "Config Path",
        validators=[
            InputRequired(),
            ValidConfigFile(),
        ],
    )


# Form instead of FlaskForm to bypass csrf validation, since just GET req to
# load page.
class ValidateID(Form):
    """Form for selecting a game server control to send"""

    server_id = HiddenField(
        "Server ID",
        validators=[
            InputRequired(),
            ServerExists(),
        ],
    )


class SendCommandForm(FlaskForm):
    send_form = HiddenField("Send Command Form")
    server_id = HiddenField("Server ID")
    command = HiddenField("Command", default="sd")
    send_cmd = StringField("Console Command", validators=[InputRequired()])
    submit = SubmitField("Send")


class ServerControlForm(FlaskForm):
    ctrl_form = HiddenField("Control Form")
    server_id = HiddenField("Server ID")
    command = HiddenField("Command", validators=[InputRequired()])
    submit = SubmitField("Execute")


class InstallForm(FlaskForm):
    servers = get_servers()
    script_name = HiddenField(
        "Script Name",
        validators=[
            InputRequired(),
            Length(min=0, max=150),
            AnyOf(servers, message="Invalid script name."),
        ],
    )

    full_name = HiddenField(
        "Full Name",
        validators=[
            InputRequired(),
            Length(min=0, max=150),
            AnyOf(list(servers.values()), message="Invalid full name."),
        ],
    )


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
    )
    password1 = PasswordField(
        "Password",
        validators=[
            ConditionalPasswordRequired(),
        ],
    )
    password2 = PasswordField(
        "Confirm Password",
        validators=[EqualTo("password1", message="Passwords must match")],
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
    install_servers = BooleanField("Can Install New Game Servers")
    add_servers = BooleanField("Can Add Existing Game Servers")
    mod_settings = BooleanField("Can Modify Web-LGSM Settings Page")
    edit_cfgs = BooleanField("Can Edit Game Server Configs")
    edit_jobs = BooleanField("Can Edit Game Server Jobs")
    delete_server = BooleanField("Can Delete Game Servers")

    # Controls and servers (using SelectMultipleField for multiple checkboxes)
    controls = SelectMultipleField("Allowed Controls", choices=[], coerce=str)
    server_ids = SelectMultipleField("Allowed Game Servers", choices=[], coerce=str)


class ValidCronExpr:
    """Validator checks cron expression is valid"""

    def __init__(self, message="Invalid cron expression!"):
        self.message = message

    def __call__(self, form, field):
        """This should raise a ValueError if invalid."""
        try:
            Cron(field.data)
        except ValueError:
            raise ValidationError(self.message)


class JobsForm(FlaskForm):
    command = SelectField(
        "Command",
        validators=[InputRequired()],
        # Just for setting defaults as good practice. Will get overwritten by
        # route logic for game server specific options.
        choices=[
            'start',
            'stop',
            'restart',
            'monitor',
            'test-alert',
            'details',
            'update-lgsm',
            'update',
            'backup',
        ],
        render_kw={
            "class": "form-select bg-dark text-light border-secondary"
        }
    )

    custom = StringField(
        "Custom Command",
        validators=[
            Length(max=150),
        ],
        render_kw={"placeholder": "Your cmd here", "class": "form-control bg-dark text-light border-secondary"},
    )

    comment = StringField(
        "Comment",
        validators=[
            Length(max=150),
            # Spaces are allowed in comments, so remove form BAD_CHARS str.
            Regexp(BAD_CHARS.replace(' ', ''), message=BAD_CHARS_MSG),
        ],
        render_kw={"placeholder": "Some comment here", "class": "form-control bg-dark text-light border-secondary"},
    )

    cron_expression = StringField(
        "Cron Expression",
        validators=[
            InputRequired(),
            ValidCronExpr(),
        ],
        render_kw={
            "class": "form-control bg-dark text-light border-secondary",
            "readonly": True
        }
    )

    server_id = HiddenField(
        "Server ID",
        validators=[
            InputRequired(),
            ServerExists(),
        ],
    )

    job_id = HiddenField("Job ID")
