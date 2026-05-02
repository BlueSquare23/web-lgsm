from ..base import *
from ..helpers import ValidateOTPCode

class OTPSetupForm(FlaskForm):
    user_id = None

    otp_code = IntegerField(
        validators=[
            InputRequired(),
            ValidateOTPCode(),
        ],
    )

    submit = SubmitField("Submit")
