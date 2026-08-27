from app.services.notifications.service import calculate_backoff_delay, is_retryable_error


def test_calculate_backoff_delay():
    """Verify exponential backoff calculation and cap."""
    base = 10.0
    max_d = 100.0

    assert calculate_backoff_delay(1, base_delay=base, max_delay=max_d) == 10.0
    assert calculate_backoff_delay(2, base_delay=base, max_delay=max_d) == 20.0
    assert calculate_backoff_delay(3, base_delay=base, max_delay=max_d) == 40.0
    assert calculate_backoff_delay(4, base_delay=base, max_delay=max_d) == 80.0
    assert calculate_backoff_delay(5, base_delay=base, max_delay=max_d) == 100.0  # Capped at max_delay


def test_is_retryable_error():
    """Verify classification of transient vs permanent non-retryable errors."""
    # Transient / retryable
    assert is_retryable_error("Connection timed out after 5.0s") is True
    assert is_retryable_error("503 Service Unavailable") is True
    assert is_retryable_error("429 Too Many Requests") is True
    assert is_retryable_error("Network unreachable") is True

    # Permanent / non-retryable
    assert is_retryable_error("SSRF validation failed for URL") is False
    assert is_retryable_error("Invalid endpoint URL: private/loopback IP address is blocked.") is False
    assert is_retryable_error("400 Bad Request") is False
    assert is_retryable_error("401 Unauthorized") is False
    assert is_retryable_error("403 Forbidden") is False
    assert is_retryable_error("404 Not Found") is False
    assert is_retryable_error("Invalid recipient 'invalid_email'") is False
