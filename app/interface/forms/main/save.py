from ..base import *
from ..helpers import FilenameLength

class SaveForm(FlaskForm):
    server_id = HiddenField(
        "Server ID",
        validators=[
            InputRequired(),
            ServerExists(),
        ],
    )
    path = HiddenField(
        "Config Path",
        validators=[
            InputRequired(),
            FilenameLength(100)
        ],
    )
    file_contents = TextAreaField(
        "File Contents",
        validators=[InputRequired()]
    )
    save_submit = SubmitField("Save File")
