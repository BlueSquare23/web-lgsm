from ..base import *
from .valid_cron_expr import ValidCronExpr

class JobsForm(FlaskForm):
    command = SelectField(
        "Control",
        validators=[InputRequired()],
        choices=[
            'start',
            'stop',
            'restart',
            'monitor',
            'test-alert',
            'details',
            'update-lgsm',
            'force-update',
            'update',
            'backup',
        ],
        render_kw={
            "class": "form-select bg-dark text-light border-secondary"
        }
    )

    custom = StringField(
        "Custom Command",
        validators=[
            Length(max=150),
        ],
        render_kw={"placeholder": "Your cmd here", "class": "form-control bg-dark text-light border-secondary"},
    )

    comment = StringField(
        "Comment",
        validators=[
            Length(max=150),
            # Spaces are allowed in comments, so remove form BAD_CHARS str.
            Regexp(BAD_CHARS.replace(' ', ''), message=BAD_CHARS_MSG),
        ],
        render_kw={"placeholder": "Some comment here", "class": "form-control bg-dark text-light border-secondary"},
    )

    schedule = StringField(
        "Cron Expression",
        validators=[
            InputRequired(),
            ValidCronExpr(),
        ],
        render_kw={
            "class": "form-control bg-dark text-light border-secondary",
            "readonly": True
        }
    )

    server_id = HiddenField(
        "Server ID",
        validators=[
            InputRequired(),
            ServerExists(),
        ],
    )

    job_id = HiddenField("Job ID")

