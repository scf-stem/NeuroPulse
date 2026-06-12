from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.app_factory import create_full_app
from app.core.database import get_db


@pytest.fixture
def mock_session():
    """Create a mock async session that keeps the endpoint happy.

    The trick: the *root* session mock is an AsyncMock (so ``await
    session.execute(...)`` yields its ``return_value``), but every
    *chained* attribute we call synchronously (``scalar_one_or_none``,
    ``scalars``, ``one``) is a plain ``MagicMock`` so calling it returns
    the configured value immediately rather than a coroutine.
    """
    session = AsyncMock()

    # --- Result for ``select(Device).where(...)`` used by get_or_create_device ---
    device_result = MagicMock()
    device_result.scalar_one_or_none.return_value = None  # device not found → creates new
    # needed after create: flush + refresh
    session.flush = AsyncMock()
    session.refresh = AsyncMock()

    # --- Result for ``select(TremorSession).where(...)`` used by get_or_create_active_session ---
    session_result = MagicMock()
    session_result.scalar_one_or_none.return_value = None  # session not found → creates new

    # --- General fallback for any ``execute`` call ---
    # Configure execute.return_value so that ``await session.execute(...)``
    # returns the MagicMock, and the first call returns device_result for
    # get_or_create_device's select(Device) query.
    session.execute = AsyncMock()
    # When called without specific args, return the default
    session.execute.return_value = device_result
    # Also handle specific query patterns via side_effect
    session.execute.side_effect = None  # default: always device_result

    # We need the mock to be flexible enough to handle multiple execute calls
    # within a single request.  Use side_effect list to return different results.
    session.execute.side_effect = [
        device_result,    # get_or_create_device: select(Device)
        session_result,   # get_or_create_active_session: select(TremorSession)
    ]

    session.add = MagicMock()
    session.commit = AsyncMock()
    session.close = AsyncMock()
    session.rollback = AsyncMock()

    return session


@pytest.fixture
def app_with_mock_db(mock_session):
    """Return a TestClient-ready app whose ``get_db`` dependency is
    overridden to yield *mock_session* (never touches a real DB)."""
    app = create_full_app()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    return app


def test_device_upload_requires_device_key(monkeypatch):
    monkeypatch.setattr("app.core.security.settings.DEVICE_API_KEY", "secret-device-key")
    client = TestClient(create_full_app())

    response = client.post(
        "/api/data/upload",
        json={
            "device_id": "TG-ESP32-001",
            "detected": False,
            "valid": True,
            "severity": 0,
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid device key"


def test_device_upload_accepts_valid_device_key(monkeypatch, app_with_mock_db):
    monkeypatch.setattr("app.core.security.settings.DEVICE_API_KEY", "secret-device-key")
    client = TestClient(app_with_mock_db)

    response = client.post(
        "/api/data/upload",
        headers={"X-Device-Key": "secret-device-key"},
        json={
            "device_id": "TG-ESP32-001",
            "detected": False,
            "valid": True,
            "severity": 0,
        },
    )

    assert response.status_code == 201


def test_device_batch_upload_requires_device_key(monkeypatch):
    monkeypatch.setattr("app.core.security.settings.DEVICE_API_KEY", "secret-device-key")
    client = TestClient(create_full_app())

    response = client.post(
        "/api/data/upload/batch",
        json={
            "device_id": "TG-ESP32-001",
            "data": [
                {"detected": False, "valid": True, "severity": 0},
            ],
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid device key"


def test_device_batch_upload_accepts_valid_key(monkeypatch, app_with_mock_db):
    monkeypatch.setattr("app.core.security.settings.DEVICE_API_KEY", "secret-device-key")
    client = TestClient(app_with_mock_db)

    response = client.post(
        "/api/data/upload/batch",
        headers={"X-Device-Key": "secret-device-key"},
        json={
            "device_id": "TG-ESP32-001",
            "data": [
                {"detected": False, "valid": True, "severity": 0},
            ],
        },
    )

    assert response.status_code != 401
