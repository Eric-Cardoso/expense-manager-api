import pytest
from app.app import app as flask_app

@pytest.fixture()
def app():
    return flask_app