## Form Helper Classes

import os
import json

from wtforms.validators import ValidationError

from .base import *

from app.interface.use_cases import is_filename_length_valid, get_game_server, verify_user_totp

with open("json/accepted_cfgs.json", "r") as gs_cfgs:
    VALID_CONFIGS = json.load(gs_cfgs)["accepted_cfgs"]


class ServerExists:
    """Validator that checks if a server ID exists in the database"""

    def __init__(self, message="Invalid game server ID!"):
        self.message = message

    def __call__(self, form, field):
        server = get_game_server(field.data)
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

        if not verify_user_totp(form.user_id, field.data):
            raise ValidationError(self.message)


class ColorField(StringField):
    widget = ColorInput()


class ValidateID(Form):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])


class FilenameLength:
    def __init__(self, max_length=100, message=None):
        self.max_length = max_length
        self.message = message

    def __call__(self, form, field):
        raw = field.data.filename if hasattr(field.data, "filename") else field.data

        valid, error = is_filename_length_valid(raw, self.max_length)

        if not valid:
            raise ValidationError(self.message or error)

