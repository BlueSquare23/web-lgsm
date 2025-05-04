from flask_wtf import FlaskForm
#from wtforms import DecimalField, RadioField, SelectField, TextAreaField, StringField
from wtforms.validators import InputRequired, Optional, AnyOf, Length, Regexp, NumberRange
from wtforms.widgets import ColorInput
from wtforms import (
    DecimalField,
    StringField,
    IntegerField,
    BooleanField,
    RadioField,
    SelectField,
    SubmitField,
    TextAreaField,
)

from .utils import get_servers

# Input bad char regex stuff.
BAD_CHARS = r'^[^ \$\'"\\#=\[\]!<>|;{}()*,?~&]*$'
BAD_CHARS_MSG = "Input contains invalid characters. " + \
     r"""Bad Chars: $ ' " \ # = [ ] ! < > | ; { } ( ) * , ? ~ &"""

class AddForm(FlaskForm):

    install_type = RadioField(
        'Installation Type',
        choices=[
            ('local', 'Game server is installed locally'),
            ('remote', 'Game server is installed on a remote machine'),
            ('docker', 'Game server is in a docker container')
        ],
        default='local',
        validators=[
            InputRequired(), 
            AnyOf(['local', 'remote', 'docker'], message='Invalid installation type selected.')
        ]
    )

    # Text inputs
    install_name = StringField(
        'Installation Title',
        render_kw={
            'class': 'form-control',
            'placeholder': 'Enter a unique name for this install'
        },
        validators=[
            InputRequired(),
            Length(max=150, message="Invalid input! Installation Title too long. Max 150 characters."),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ]
    )
    
    install_path = StringField(
        'Installation directory path',
        render_kw={
            'class': 'form-control',
            'placeholder': 'Enter the full path to the game server directory'
        },
        validators=[
            InputRequired(),
            Length(max=150, message="Invalid input! Installation directory path too long. Max 150 characters."),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ]
    )
    
    servers = get_servers()
    script_name = StringField(
        'LGSM script name',
        render_kw={
            'class': 'form-control',
            'placeholder': 'Enter the name of the game server script. For example, "gmodserver"'
        },
        validators=[
            InputRequired(),
            Length(max=150, message="Invalid input! LGSM script name too long. Max 150 characters."),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
            AnyOf(servers, message='Invalid script name.')
        ]
    )
    
    username = StringField(
        'Game server system username',
        render_kw={
            'class': 'form-control',
            'placeholder': 'Enter system user game server is installed under. For example, "coolguy123"'
        },
        validators=[
            Length(max=150, message="Invalid input! Username too long. Max 150 characters."),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ]
    )
    
    install_host = StringField(
        'Remote server\'s IP address or hostname',
        render_kw={
            'class': 'form-control',
            'placeholder': 'Enter remote server\'s IP address or hostname. For example, "gmod.domain.tld"'
        },
        validators=[
            Length(max=150, message="Invalid input! Install host too long. Max 150 characters."),
            Regexp(BAD_CHARS, message=BAD_CHARS_MSG),
        ]
    )

VALID_HEX_COLOR = r'^#(?:[0-9a-fA-F]{1,2}){3}$'

class ColorField(StringField):
    """Custom color field using HTML5 color input"""
    widget = ColorInput()


class SettingsForm(FlaskForm):
    # Color fields
    text_color = ColorField(
        'Output Text Color',
        validators=[
            InputRequired(),
            Regexp(VALID_HEX_COLOR, message='Invalid text color!'),
        ],
        render_kw={
            'class': 'form-control form-control-color',
            'title': 'Choose your color'
        }
    )

    graphs_primary = ColorField(
        'Stats Primary Color',
        validators=[
            InputRequired(),
            Regexp(VALID_HEX_COLOR, message='Invalid primary color!'),
        ],
        render_kw={
            'class': 'form-control form-control-color',
            'title': 'Choose your color'
        }
    )

    graphs_secondary = ColorField(
        'Stats Secondary Color',
        validators=[
            InputRequired(),
            Regexp(VALID_HEX_COLOR, message='Invalid secondary color!'),
        ],
        render_kw={
            'class': 'form-control form-control-color',
            'title': 'Choose your color'
        }
    )

    # Terminal settings
    terminal_height = IntegerField(
        'Default Terminal Height',
        validators=[
            InputRequired(),
            NumberRange(min=5, max=100)
        ],
        default=10,
        render_kw={
            'class': 'form-control',
            'min': '5',
            'max': '100'
        }
    )

    # Radio button options
    delete_user = RadioField(
        'Delete user on server delete',
        choices=[
            ('true', 'Delete game server\'s system user on delete'),
            ('false', 'Keep user on game server delete')
        ],
        default='false',
        validators=[InputRequired()],
        render_kw={
            'class': 'form-check-input',
            'onchange': 'checkDelFiles()'
        }
    )

    remove_files = RadioField(
        'Remove files on delete',
        choices=[
            ('true', 'Remove game server files on delete'),
            ('false', 'Leave game server files on delete')
        ],
        default='false',
        validators=[InputRequired()],
        render_kw={
            'class': 'form-check-input',
            'onchange': 'checkKeepUser()'
        }
    )

    install_new_user = RadioField(
        'User creation on install',
        choices=[
            ('true', 'Setup new system user when installing new game servers'),
            ('false', f'Install new game servers under the system user')
        ],
        default='true',
        validators=[InputRequired()],
        render_kw={'class': 'form-check-input'}
    )

    newline_ending = RadioField(
        'Newline termination',
        choices=[
            ('true', 'Terminate lines with a newline (Classic web-lgsm term display)'),
            ('false', 'Do not enforce newline termination (New web-lgsm term display)')
        ],
        default='false',
        validators=[InputRequired()],
        render_kw={'class': 'form-check-input'}
    )

    show_stderr = RadioField(
        'Error output display',
        choices=[
            ('true', 'Show both stdout & stderr output streams merged'),
            ('false', 'Show only stdout output stream, suppress stderr')
        ],
        default='true',
        validators=[InputRequired()],
        render_kw={'class': 'form-check-input'}
    )

    clear_output_on_reload = RadioField(
        'Terminal clearing behavior',
        choices=[
            ('true', 'Clear web terminal when running new command'),
            ('false', 'Do not clear web terminal after running command')
        ],
        default='true',
        validators=[InputRequired()],
        render_kw={'class': 'form-check-input'}
    )

    # Checkbox options
    show_stats = BooleanField(
        'Show Live Server Stats on Home Page',
        render_kw={
            'class': 'form-check-input'
        }
    )

    purge_tmux_cache = BooleanField(
        'Delete local tmux socket file name cache',
        render_kw={
            'class': 'form-check-input'
        }
    )

    update_weblgsm = BooleanField(
        'Check for and update the Web LGSM',
        render_kw={
            'class': 'form-check-input'
        }
    )

    submit = SubmitField(
        'Apply',
        render_kw={
            'class': 'btn btn-outline-primary'
        }
    )
