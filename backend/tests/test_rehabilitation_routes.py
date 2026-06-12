from fastapi.testclient import TestClient

from app.app_factory import create_full_app


def test_recommended_exercises_route_is_not_parsed_as_integer_id():
    """Regression test: ensure /exercises/recommended is NOT matched by the
    dynamic /exercises/{ex_id} route (which expects an ``int`` path param).

    The static route must be registered *before* the dynamic route in
    FastAPI, otherwise a request for ``recommended`` reaches the dynamic
    route and fails with a 422 validation error.
    """
    app = create_full_app()

    # We only care about route matching, not the database backend.
    # Override the db dependency so the test works without a real PG database.
    async def override_get_db():
        raise RuntimeError("db-not-reached; this error means the static route matched")

    app.dependency_overrides.clear()
    # We need the key to be the actual function used by the route.
    # We import the one the router uses.
    from app.core.database import get_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    try:
        response = client.get("/api/rehabilitation/exercises/recommended")
        # If we got a response, ensure it's not the 422 from the dynamic route.
        assert response.status_code != 422, (
            f"Expected status != 422, got {response.status_code}. "
            "The static /exercises/recommended route was likely shadowed "
            "by the dynamic /exercises/{ex_id} route."
        )
    except RuntimeError as exc:
        # If the static route matched, get_db will be resolved, our override
        # fires, and we raise RuntimeError("db-not-reached; …"). That confirms
        # the route was *not* shadowed — the static route matched.
        assert "db-not-reached" in str(exc), (
            f"An unexpected RuntimeError occurred: {exc}"
        )
