from ..base import *

class SaveForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    cfg_path = HiddenField(validators=[InputRequired(), ValidConfigFile()])
    file_contents = TextAreaField(validators=[InputRequired()])
    save_submit = SubmitField("Save File")
