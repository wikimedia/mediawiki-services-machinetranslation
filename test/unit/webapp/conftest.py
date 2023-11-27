import pytest
from fastapi.testclient import TestClient

from translate import app


@pytest.fixture
def client():
    """Configures the app for testing

    Sets app config variable ``TESTING`` to ``True``

    :return: App for testing
    """

    client = TestClient(app)

    yield client
