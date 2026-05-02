from ..base import *

class UploadForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    path = HiddenField(validators=[InputRequired()])
    file_contents = TextAreaField(validators=[InputRequired()])
    upload_submit = SubmitField("Upload File")
