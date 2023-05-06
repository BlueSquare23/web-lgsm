import sys
import pytest
from pathlib import Path
from app import main, db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app_path = '/home/bluesquare23/Projects/new/web-lgsm/app'

sys.path.insert(0, app_path)

@pytest.fixture
def app():
    application = main()
    application.config.update({
        "TESTING": True,
    })

    yield application

@pytest.fixture
def client(app):
    return app.test_client()
