from app.services.notifications.email import EmailNotificationProvider


def test_email_provider_content_formatting():
    """Verify clean plain text email formatting with verified facts and sources."""
    provider = EmailNotificationProvider(enabled=True, api_key="test_key")

    alert = {
        "id": 1,
        "symbol": "NVDA",
        "company_name": "NVIDIA Corporation",
        "alert_type": "portfolio_gain",
        "severity": "info",
        "title": "Gain Alert: NVDA (+15.00%)",
        "message": "Holding NVDA has an unrealized gain of 15.00%.",
        "facts": {
            "symbol": "NVDA",
            "quantity": 10,
            "current_price": 115.0,
            "unrealized_gain_loss_percent": 15.0,
        },
        "sources": [
            {"name": "Yahoo Finance Quote", "url": "https://finance.yahoo.com/quote/NVDA"}
        ],
    }

    content = provider.format_email_content(alert)
    assert "[INFO] AIRA Alert: NVDA - Gain Alert: NVDA (+15.00%)" in content["subject"]
    assert "Symbol: NVDA (NVIDIA Corporation)" in content["body_text"]
    assert "Holding NVDA has an unrealized gain of 15.00%." in content["body_text"]
    assert "unrealized_gain_loss_percent: 15.0" in content["body_text"]
    assert "Yahoo Finance Quote: https://finance.yahoo.com/quote/NVDA" in content["body_text"]


def test_email_provider_dispatch_validation_and_mock():
    """Verify email delivery input validation and mock dispatch."""
    sent = []

    def mock_send(payload):
        sent.append(payload)
        return True

    provider = EmailNotificationProvider(enabled=True, send_fn=mock_send)

    # Missing user/alert
    assert provider.send_alert_notification(user_id=0, alert={}) is False
    assert provider.send_alert_notification(user_id=1, alert={"id": 1}, recipient="invalid_email") is False

    # Valid dispatch
    alert = {
        "id": 10,
        "symbol": "AAPL",
        "title": "Apple Alert",
        "severity": "warning",
        "message": "Price drop",
    }
    success = provider.send_alert_notification(
        user_id=1,
        alert=alert,
        recipient="investor@example.com",
    )
    assert success is True
    assert len(sent) == 1
    assert sent[0]["recipient"] == "investor@example.com"
    assert "Apple Alert" in sent[0]["subject"]


def test_email_provider_disabled_returns_false():
    """Verify disabled email provider returns False without sending."""
    provider = EmailNotificationProvider(enabled=False)
    assert provider.send_alert_notification(
        user_id=1,
        alert={"id": 1, "title": "Test"},
        recipient="test@example.com",
    ) is False
