from ..base import *
from ..helpers import FilenameLength
from flask_wtf.file import FileField, FileRequired

class UploadForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    path = HiddenField(validators=[InputRequired(), FilenameLength(100)])
    file = FileField(validators=[FileRequired(), FilenameLength(100)])
    upload_submit = SubmitField("Upload File")
