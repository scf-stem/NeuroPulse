from fastapi.testclient import TestClient

from app.app_factory import create_full_app


def test_test_routes_not_available_in_production(monkeypatch):
    monkeypatch.setattr("app.app_factory.settings.APP_ENV", "production")
    monkeypatch.setattr("app.core.security.settings.APP_ENV", "production")
    monkeypatch.setattr("app.core.security.settings.DEBUG", False)
    monkeypatch.setattr("app.core.security.settings.JWT_SECRET_KEY", "safe-jwt-secret")
    monkeypatch.setattr("app.core.security.settings.SECRET_KEY", "safe-app-secret")
    monkeypatch.setattr("app.core.security.settings.DEVICE_API_KEY", "safe-device-key")

    app = create_full_app()
    routes = [r.path for r in app.routes if hasattr(r, "path")]
    test_routes = [p for p in routes if "/api/test/" in p]

    assert not test_routes, f"Test routes found in production app: {test_routes}"


def test_test_routes_available_in_non_production():
    """Sanity check: test routes exist when APP_ENV is not production (default)."""
    client = TestClient(create_full_app())
    response = client.get("/api/test/stats")
    # The route exists (even if app-level issues affect the response body,
    # we verify the route was registered).
    assert response.status_code in (200, 422, 500)
