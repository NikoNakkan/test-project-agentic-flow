import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import hello_world as hello_world_service


@pytest.fixture(autouse=True)
def reset_counter():
    hello_world_service.reset_count()
    yield
    hello_world_service.reset_count()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
