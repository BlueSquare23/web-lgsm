from ..base import *

class DownloadForm(FlaskForm):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    cfg_path = HiddenField(validators=[InputRequired(), ValidConfigFile()])
    download_submit = SubmitField("Download Config File")
