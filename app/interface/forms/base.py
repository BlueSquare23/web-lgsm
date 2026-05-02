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
    PasswordField,
    SelectMultipleField,
)

from .helpers import ServerExists, ValidConfigFile
from app.container import container

USERNAME = getpass.getuser()

VALID_HEX_COLOR = r"^#(?:[0-9a-fA-F]{1,2}){3}$"

BAD_CHARS = r'^[^ \$\'"\\#=\[\]!<>|;{}()*,?~&]*$'
BAD_CHARS_MSG = (
    "Input contains invalid characters. "
    + r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &"""
)

with open("json/accepted_cfgs.json", "r") as gs_cfgs:
    VALID_CONFIGS = json.load(gs_cfgs)["accepted_cfgs"]

