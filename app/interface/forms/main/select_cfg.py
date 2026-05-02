from ..base import *

class SelectCfgForm(Form):
    server_id = HiddenField(validators=[InputRequired(), ServerExists()])
    cfg_path = HiddenField(validators=[InputRequired(), ValidConfigFile()])
