from flask_wtf import FlaskForm
from wtforms import DecimalField, RadioField, SelectField, TextAreaField, StringField
from wtforms.validators import InputRequired, Optional, AnyOf, Length, Regexp

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
            InputRequired(),
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
