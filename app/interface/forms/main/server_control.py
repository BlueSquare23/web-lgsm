from ..base import *

class ServerControlForm(FlaskForm):
    ctrl_form = HiddenField()
    server_id = HiddenField()
    control = HiddenField(validators=[InputRequired()])
    submit = SubmitField("Execute")
