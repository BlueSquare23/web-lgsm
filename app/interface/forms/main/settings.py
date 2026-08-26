from ..base import *
from ..helpers import ColorField

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
        "Show Live Server Stats on Home Page",
        render_kw={"class": "form-check-input"}
    )

    purge_cache = BooleanField(
        "Delete server side cache",
        render_kw={"class": "form-check-input"},
    )

    reset_rpc_servers = BooleanField(
        "Reset RPC servers (used by file manager)",
        render_kw={"class": "form-check-input"},
    )

    update_weblgsm = BooleanField(
        "Check for and update the Web LGSM",
        render_kw={"class": "form-check-input"}
    )

    submit = SubmitField("Apply", render_kw={"class": "btn btn-outline-primary"})

