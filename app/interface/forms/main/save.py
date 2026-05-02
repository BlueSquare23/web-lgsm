from ..base import *

class SaveForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    path = HiddenField(validators=[InputRequired()])
    file_contents = TextAreaField(validators=[InputRequired()])
    save_submit = SubmitField("Save File")
