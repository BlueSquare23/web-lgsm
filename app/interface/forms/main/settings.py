from ..base import *
from ..helpers import ColorField

class SettingsForm(FlaskForm):
    text_color = ColorField(validators=[InputRequired(), Regexp(VALID_HEX_COLOR)])
    graphs_primary = ColorField(validators=[InputRequired(), Regexp(VALID_HEX_COLOR)])
    graphs_secondary = ColorField(validators=[InputRequired(), Regexp(VALID_HEX_COLOR)])

    terminal_height = IntegerField(validators=[InputRequired(), NumberRange(min=5, max=100)], default=10)

    delete_user = RadioField(choices=[("true","Delete"),("false","Keep")], default="false", validators=[InputRequired()])
    remove_files = RadioField(choices=[("true","Remove"),("false","Keep")], default="false", validators=[InputRequired()])

    install_new_user = RadioField(
        choices=[("true","Setup"),("false", f"Use {USERNAME}")],
        default="true",
        validators=[InputRequired()],
    )

    newline_ending = RadioField(choices=[("true","Yes"),("false","No")], default="false", validators=[InputRequired()])
    show_stderr = RadioField(choices=[("true","Yes"),("false","No")], default="true", validators=[InputRequired()])
    clear_output_on_reload = RadioField(choices=[("true","Yes"),("false","No")], default="true", validators=[InputRequired()])

    show_stats = BooleanField()
    purge_cache = BooleanField()
    update_weblgsm = BooleanField()

    submit = SubmitField("Apply")
