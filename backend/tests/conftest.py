import pytest
from fastapi.testclient import TestClient

from app.app_factory import create_full_app


@pytest.fixture()
def client():
    return TestClient(create_full_app())
