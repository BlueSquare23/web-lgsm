import os
import sys
import time
import shutil
import pytest
from pathlib import Path
from app import main
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

app_path = os.path.abspath('../app')

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
