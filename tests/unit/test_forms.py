import pytest
import os
from werkzeug.datastructures import MultiDict
from app.forms import (
    LoginForm,
    SetupForm,
    AddForm,
    SettingsForm,
    UploadTextForm,
    DownloadCfgForm,
    SelectCfgForm,
    ValidateID,
    SendCommandForm,
    ServerControlForm,
    InstallForm,
    EditUsersForm,
    ServerExists,
    ValidConfigFile,
    VALID_HEX_COLOR,
    BAD_CHARS,
    BAD_CHARS_MSG
)
from app.models import GameServer


# Helper function to create form data with app context
def get_form_data(app, form_class, **kwargs):
    with app.test_request_context():
        form = form_class()
        data = {field.name: "" for field in form}
        data.update(kwargs)
        return MultiDict(data)


# Test LoginForm
def test_login_form_valid(app):
    form_data = get_form_data(app, LoginForm, username="testuser", password="validPassword123!")
    with app.test_request_context():
        form = LoginForm(formdata=form_data, meta={'csrf': False})
        assert form.validate() is True


def test_login_form_invalid_short_username(app):
    form_data = get_form_data(app, LoginForm, username="abc", password="validPassword123!")
    with app.test_request_context():
        form = LoginForm(formdata=form_data, meta={'csrf': False})
        assert form.validate() is False
        assert "Field must be between 4 and 20 characters long." in form.username.errors[0]


# Test SetupForm
def test_setup_form_valid(app):
    form_data = get_form_data(
        app,
        SetupForm,
        username="testuser",
        password1="ValidPassword123!",
        password2="ValidPassword123!"
    )
    with app.test_request_context():
        form = SetupForm(formdata=form_data, meta={'csrf': False})
        assert form.validate() is True


def test_setup_form_password_mismatch(app):
    form_data = get_form_data(
        app,
        SetupForm,
        username="testuser",
        password1="ValidPassword123!",
        password2="DifferentPassword123!"
    )
    with app.test_request_context():
        form = SetupForm(formdata=form_data, meta={'csrf': False})
        assert form.validate() is False
        assert "Passwords do not match" in form.password2.errors[0]


# Test AddForm
def test_add_form_valid_local(app, db_session, monkeypatch):
    # Mock get_servers() to return our test server name
    def mock_get_servers():
        return ["gmodserver"]  # Only include the server we're testing
    
    monkeypatch.setattr("app.forms.get_servers", mock_get_servers)

    # Create a test server in the database for the AnyOf validator
    test_server = GameServer(
        install_type='local',
        install_name='TestServer',
        install_path='/path/to/server',
        script_name='gmodserver',
        username='testuser',
        install_host='127.0.0.1'
    )
    db_session.session.add(test_server)
    db_session.session.commit()

    form_data = get_form_data(
        app,
        AddForm,
        install_type="local",
        install_name="TestServer",
        install_path="/path/to/server",
        script_name="gmodserver"
    )
    with app.test_request_context():
        form = AddForm(formdata=form_data, meta={'csrf': False})

        # Print form errors if validation fails
        if not form.validate():
            print("Form errors:", form.errors)

        assert form.validate() is True

# Test SettingsForm
def test_settings_form_valid(app):
    form_data = get_form_data(
        app,
        SettingsForm,
        text_color="#ffffff",
        graphs_primary="#000000",
        graphs_secondary="#123456",
        terminal_height=10,
        delete_user="false",
        remove_files="false",
        install_new_user="true",
        newline_ending="false",
        show_stderr="true",
        clear_output_on_reload="true"
    )
    with app.test_request_context():
        form = SettingsForm(formdata=form_data, meta={'csrf': False})
        assert form.validate() is True


# Test UploadTextForm with database validation
def test_upload_text_form_valid(app, db_session):
    # Create a test server in the database
    test_server = GameServer(
        install_type='local',
        install_name='Test Server',
        install_path='/path/to/server',
        script_name='testserver',
        username='testuser'
    )
    db_session.session.add(test_server)
    db_session.session.commit()

    form_data = get_form_data(
        app,
        UploadTextForm,
        server_id=str(test_server.id),
        cfg_path="server.cfg",
        file_contents="test content"
    )
    with app.test_request_context():
        form = UploadTextForm(formdata=form_data, meta={'csrf': False})
        assert form.validate() is True


# Test custom validators with database
def test_server_exists_validator(app, db_session):
    # Create a test server in the database
    test_server = GameServer(
        install_type='local',
        install_name='Test Server',
        install_path='/path/to/server',
        script_name='testserver',
        username='testuser'
    )
    db_session.session.add(test_server)
    db_session.session.commit()

    validator = ServerExists()
    with app.test_request_context():
        form = None  # Form not used in validator
        field = type('Field', (), {'data': str(test_server.id)})

        # Should not raise an exception
        validator(form, field)


def test_valid_config_file_validator(app):
    # Create a temporary config file
    cfg_file = "tests/test_data/Mockcraft/lgsm/config-lgsm/mcserver/common.cfg"
    
    validator = ValidConfigFile()
    with app.test_request_context():
        form = None  # Form not used in validator
        field = type('Field', (), {'data': str(cfg_file)})

        # Should not raise an exception
        validator(form, field)

