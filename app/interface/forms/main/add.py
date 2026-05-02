from ..base import *

class AddForm(FlaskForm):
    server_id = HiddenField("Server ID", validators=[Optional(), ServerExists()])

    install_type = RadioField(
        "Installation Type",
        choices=[
            ("local", "Game server is installed locally"),
            ("remote", "Game server is installed on a remote machine"),
            ("docker", "Game server is in a docker container"),
        ],
        default="local",
        validators=[
            InputRequired(),
            AnyOf(["local", "remote", "docker"]),
        ],
    )

    install_name = StringField(
        "Installation Title",
        render_kw={"class": "form-control"},
        validators=[InputRequired(), Length(max=150), Regexp(BAD_CHARS.replace(' ', ''), message=BAD_CHARS_MSG)],
    )

    install_path = StringField(
        "Installation directory path",
        render_kw={"class": "form-control"},
        validators=[InputRequired(), Length(max=150), Regexp(BAD_CHARS, message=BAD_CHARS_MSG)],
    )

    installable = container.list_installable_game_servers().execute()
    servers = [script for script in installable] if installable else []

    script_name = StringField(
        "LGSM script name",
        validators=[InputRequired(), Length(max=150), Regexp(BAD_CHARS), AnyOf(servers)],
    )

    username = StringField("Game server system username", validators=[Length(max=150), Regexp(BAD_CHARS)])
    install_host = StringField("Remote server's IP address or hostname", validators=[Length(max=150), Regexp(BAD_CHARS)])
