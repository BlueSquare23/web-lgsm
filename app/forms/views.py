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
    Optional,
)
from wtforms import (
    Form,
    RadioField,
    SubmitField,
    SelectField,
    TextAreaField,
    StringField,
    IntegerField,
    BooleanField,
    HiddenField,
)

from app.utils import get_servers
from .helpers import ServerExists, ValidConfigFile

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


## Main Forms

class AddForm(FlaskForm):
    server_id = HiddenField(
        "Server ID",
        validators=[
            Optional(),
            ServerExists(),
        ],
    )

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
            Regexp(BAD_CHARS.replace(' ', ''), message=BAD_CHARS_MSG),
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

    servers = [script for script, tup in get_servers().items()]

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
    control = HiddenField("Control", default="sd")
    send_cmd = StringField("Console Command", validators=[InputRequired()])
    submit = SubmitField("Send")


class ServerControlForm(FlaskForm):
    ctrl_form = HiddenField("Control Form")
    server_id = HiddenField("Server ID")
    control = HiddenField("Control", validators=[InputRequired()])
    submit = SubmitField("Execute")


class InstallForm(FlaskForm):
    servers = get_servers()
    short_names = []
    long_names = []
    for short, (long, img) in servers.items():
        short_names.append(short)
        long_names.append(long)

    script_name = HiddenField(
        "Script Name",
        validators=[
            InputRequired(),
            Length(min=0, max=150),
            AnyOf(short_names, message="Invalid script name."),
        ],
    )

    full_name = HiddenField(
        "Full Name",
        validators=[
            InputRequired(),
            Length(min=0, max=150),
            AnyOf(long_names, message="Invalid full name."),
        ],
    )


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
        "Control",
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
