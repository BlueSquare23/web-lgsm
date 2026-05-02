from ..base import *

class DownloadForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    path = HiddenField(validators=[InputRequired()])
    download_submit = SubmitField("Download Config File")
