from ..base import *
from flask_wtf.file import FileField, FileRequired

class UploadForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    path = HiddenField(validators=[InputRequired()])
    file = FileField(validators=[FileRequired()])
    upload_submit = SubmitField("Upload File")
