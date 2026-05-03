from ..base import *
from ..helpers import ValidateOTPCode

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

