from ..base import *
from ..helpers import FilenameLength

class SaveForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    path = HiddenField(validators=[InputRequired(), FilenameLength(100)])
    file_contents = TextAreaField(validators=[InputRequired()])
    save_submit = SubmitField("Save File")
