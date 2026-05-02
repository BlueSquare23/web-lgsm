from ..base import *

class UploadForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    cfg_path = HiddenField(validators=[InputRequired(), ValidConfigFile()])
    file_contents = TextAreaField(validators=[InputRequired()])
    upload_submit = SubmitField("Upload File")
