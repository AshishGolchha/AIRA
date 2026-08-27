import json
from app.services.notifications.webhook import WebhookNotificationProvider


def test_webhook_url_validation_and_ssrf_protection():
    """Verify SSRF defense blocks private, loopback, cloud metadata IPs and bad schemes."""
    provider = WebhookNotificationProvider()

    # Valid HTTPS public URL
    safe, err = provider.is_safe_url("https://webhook.site/abc-123")
    assert safe is True

    # Bad schemes
    safe, err = provider.is_safe_url("http://example.com", allow_http=False)
    assert safe is False
    assert "scheme must be HTTPS" in err

    safe, err = provider.is_safe_url("file:///etc/passwd")
    assert safe is False

    safe, err = provider.is_safe_url("ftp://server.example.com/alerts")
    assert safe is False

    # Blocked hosts
    safe, err = provider.is_safe_url("https://localhost/webhook")
    assert safe is False

    safe, err = provider.is_safe_url("https://127.0.0.1:8000/webhook")
    assert safe is False

    safe, err = provider.is_safe_url("https://10.0.0.5/api")
    assert safe is False

    safe, err = provider.is_safe_url("https://192.168.1.100/webhook")
    assert safe is False

    safe, err = provider.is_safe_url("https://169.254.169.254/latest/meta-data")
    assert safe is False


def test_webhook_payload_and_hmac_signing():
    """Verify payload generation and HMAC SHA256 signature calculation."""
    dispatched = []

    def mock_dispatch(record):
        dispatched.append(record)
        return True

    provider = WebhookNotificationProvider(dispatch_fn=mock_dispatch, allow_http_in_tests=True)

    alert = {
        "id": 99,
        "symbol": "TSLA",
        "company_name": "Tesla Inc",
        "alert_type": "watchlist_move",
        "severity": "critical",
        "title": "Watchlist Drop",
        "message": "TSLA dropped 12%",
        "facts": {"symbol": "TSLA", "change_percent": -12.0},
        "sources": [{"name": "Yahoo", "url": "https://finance.yahoo.com"}],
        "created_at": "2026-08-27T10:00:00Z",
    }

    secret = "my_webhook_secret_key"
    success = provider.send_alert_notification(
        user_id=1,
        alert=alert,
        endpoint_url="https://api.example.com/alerts",
        secret_key=secret,
    )
    assert success is True
    assert len(dispatched) == 1

    record = dispatched[0]
    assert record["user_id"] == 1
    assert record["endpoint_url"] == "https://api.example.com/alerts"
    assert record["payload"]["event"] == "investment_alert"
    assert record["payload"]["alert"]["symbol"] == "TSLA"
    assert record["headers"]["Content-Type"] == "application/json"

    # Verify HMAC signature
    sig_header = record["headers"]["X-AIRA-Signature"]
    assert sig_header.startswith("sha256=")
    expected_sig = provider.compute_signature(
        json.dumps(record["payload"], sort_keys=True).encode("utf-8"),
        secret,
    )
    assert sig_header == expected_sig
