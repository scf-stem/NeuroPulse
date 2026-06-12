import pytest
from fastapi import HTTPException

from app.api.auth import DEMO_ACCESS_TOKEN, get_current_user_from_token


@pytest.mark.asyncio
async def test_demo_token_disabled_in_production(monkeypatch):
    monkeypatch.setattr("app.api.auth.settings.APP_ENV", "production")

    class Request:
        headers = {}

    with pytest.raises(HTTPException) as exc:
        await get_current_user_from_token(Request(), token=DEMO_ACCESS_TOKEN, db=None)

    assert exc.value.status_code == 401
