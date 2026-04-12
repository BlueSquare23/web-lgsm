## Form Helper Classes

import os
import json

from wtforms.validators import ValidationError

from app.container import container

# Only open read in the accepted_cfgs.json at app startup (is static).
with open("json/accepted_cfgs.json", "r") as gs_cfgs:
    VALID_CONFIGS = json.load(gs_cfgs)["accepted_cfgs"]


class ServerExists:
    """Validator that checks if a server ID exists in the database"""

    def __init__(self, message="Invalid game server ID!"):
        self.message = message

    def __call__(self, form, field):
#        server = GameServer.query.filter_by(id=field.data).first()
        server = container.get_game_server().execute(field.data)
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
