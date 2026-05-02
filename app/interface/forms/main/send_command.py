from ..base import *

class SendCommandForm(FlaskForm):
    send_form = HiddenField()
    server_id = HiddenField()
    control = HiddenField(default="sd")
    send_cmd = StringField(validators=[InputRequired()])
    submit = SubmitField("Send")
