import pytest
from starlette.testclient import TestClient
import time
import urllib3

from app.main import app

@pytest.fixture(scope="module")
def test_app():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    client = TestClient(app)
    time.sleep(5) # wait 10s for the authentication
    yield client

def test_example(test_app):
    response = test_app.get("/v1/example")
    assert response.status_code == 200
    assert response.json()['slideshow']