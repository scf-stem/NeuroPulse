import pytest
from fastapi import HTTPException, Header
from unittest.mock import MagicMock

from app.core.security import (
    _DEFAULT_SECRETS,
    assert_safe_production_settings,
    require_privileged_user,
    verify_device_key,
    verify_device_key_value,
)
from app.models.user import User


class TestVerifyDeviceKeyValue:
    def test_rejects_missing_config(self):
        with pytest.raises(HTTPException) as exc:
            verify_device_key_value(None, "")
        assert exc.value.status_code == 401

    def test_rejects_wrong_key(self):
        with pytest.raises(HTTPException) as exc:
            verify_device_key_value("wrong", "expected")
        assert exc.value.status_code == 401

    def test_accepts_exact_key(self):
        assert verify_device_key_value("expected", "expected") is None


class TestAssertSafeProductionSettings:
    def test_rejects_default_jwt_secret(self):
        class Settings:
            APP_ENV = "production"
            JWT_SECRET_KEY = "your-jwt-secret-key"
            SECRET_KEY = "not-default"
            DEVICE_API_KEY = "device-key"
            DEBUG = False

        with pytest.raises(RuntimeError) as exc:
            assert_safe_production_settings(Settings())
        assert "JWT_SECRET_KEY" in str(exc.value)

    def test_rejects_default_secret_key(self):
        class Settings:
            APP_ENV = "production"
            JWT_SECRET_KEY = "something-secure"
            SECRET_KEY = "your-jwt-secret-key"
            DEVICE_API_KEY = "device-key"
            DEBUG = False

        with pytest.raises(RuntimeError) as exc:
            assert_safe_production_settings(Settings())
        assert "SECRET_KEY" in str(exc.value)

    def test_rejects_empty_device_api_key(self):
        class Settings:
            APP_ENV = "production"
            JWT_SECRET_KEY = "something-secure"
            SECRET_KEY = "something-secure"
            DEVICE_API_KEY = ""
            DEBUG = False

        with pytest.raises(RuntimeError) as exc:
            assert_safe_production_settings(Settings())
        assert "DEVICE_API_KEY" in str(exc.value)

    def test_rejects_debug_mode_in_production(self):
        class Settings:
            APP_ENV = "production"
            JWT_SECRET_KEY = "something-secure"
            SECRET_KEY = "something-secure"
            DEVICE_API_KEY = "device-key"
            DEBUG = True

        with pytest.raises(RuntimeError) as exc:
            assert_safe_production_settings(Settings())
        assert "DEBUG" in str(exc.value)

    def test_happy_path_all_settings_valid(self):
        class Settings:
            APP_ENV = "production"
            JWT_SECRET_KEY = "a-strong-jwt-secret"
            SECRET_KEY = "a-strong-secret-key"
            DEVICE_API_KEY = "device-api-key-123"
            DEBUG = False

        assert assert_safe_production_settings(Settings()) is None

    def test_skips_checks_when_not_production(self):
        class Settings:
            APP_ENV = "development"
            JWT_SECRET_KEY = "your-jwt-secret-key"
            SECRET_KEY = ""
            DEVICE_API_KEY = ""
            DEBUG = True

        assert assert_safe_production_settings(Settings()) is None


class TestRequirePrivilegedUser:
    def test_rejects_non_privileged_role(self):
        user = MagicMock(spec=User, role="user")
        with pytest.raises(HTTPException) as exc:
            require_privileged_user(user)
        assert exc.value.status_code == 403

    def test_accepts_admin_role(self):
        user = MagicMock(spec=User, role="admin")
        assert require_privileged_user(user) is None

    def test_accepts_doctor_role(self):
        user = MagicMock(spec=User, role="doctor")
        assert require_privileged_user(user) is None


class TestVerifyDeviceKeyDependency:
    def test_rejects_missing_header(self, monkeypatch):
        async def fake_header(x_device_key=None):
            return x_device_key

        monkeypatch.setattr(
            "app.core.security.settings",
            MagicMock(DEVICE_API_KEY="expected-device-key"),
        )

        import asyncio

        with pytest.raises(HTTPException) as exc:
            asyncio.run(verify_device_key(x_device_key=None))
        assert exc.value.status_code == 401

    def test_rejects_wrong_header(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.security.settings",
            MagicMock(DEVICE_API_KEY="expected-device-key"),
        )

        import asyncio

        with pytest.raises(HTTPException) as exc:
            asyncio.run(verify_device_key(x_device_key="wrong-key"))
        assert exc.value.status_code == 401

    def test_accepts_correct_header(self, monkeypatch):
        monkeypatch.setattr(
            "app.core.security.settings",
            MagicMock(DEVICE_API_KEY="expected-device-key"),
        )

        import asyncio

        result = asyncio.run(verify_device_key(x_device_key="expected-device-key"))
        assert result is None


class TestDEFAULT_SECRETS_is_private:
    def test_default_secrets_is_module_private(self):
        with pytest.raises(ImportError):
            from app.core.security import DEFAULT_SECRETS  # noqa: F811
