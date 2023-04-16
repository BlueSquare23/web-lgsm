import sys
import pytest
from pathlib import Path
from app import main

app_path = '/home/bluesquare23/Projects/new/web-lgsm/app'

sys.path.insert(0, app_path)

application = main()

@pytest.fixture
def app():
    yield application

@pytest.fixture
def client(app):
    return app.test_client()
