from app.models.notification_endpoint import NotificationEndpoint
from app.models.notification_preference import NotificationPreference


def test_notification_preference_model_defaults_and_dict():
    """Verify NotificationPreference default fields and dictionary representation."""
    pref = NotificationPreference(user_id=42)
    assert pref.user_id == 42
    assert pref.in_app_enabled is True
    assert pref.email_enabled is True
    assert pref.webhook_enabled is False
    assert pref.minimum_severity == "info"
    assert pref.alert_types is None

    d = pref.to_dict()
    assert d["user_id"] == 42
    assert d["in_app_enabled"] is True
    assert d["email_enabled"] is True
    assert d["webhook_enabled"] is False
    assert d["minimum_severity"] == "info"
    assert d["alert_types"] is None


def test_notification_endpoint_model_hides_secret():
    """Verify NotificationEndpoint never leaks secret_key in to_dict()."""
    endpoint = NotificationEndpoint(
        user_id=42,
        endpoint_url="https://api.example.com/alerts/webhook",
        channel="webhook",
        secret_key="super_secret_signing_key",
        is_enabled=True,
    )
    assert endpoint.secret_key == "super_secret_signing_key"

    d = endpoint.to_dict()
    assert "secret_key" not in d
    assert d["has_secret"] is True
    assert d["endpoint_url"] == "https://api.example.com/alerts/webhook"
    assert d["channel"] == "webhook"
    assert d["is_enabled"] is True
