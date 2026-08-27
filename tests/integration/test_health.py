def test_health_endpoint(client):
    """Verify /api/v1/health returns 200 OK with expected payload."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "service": "AIRA",
        "version": "0.1.0",
    }


def test_request_id_generated_when_missing(client):
    """Verify X-Request-ID header is generated when omitted by client."""
    response = client.get("/api/v1/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_request_id_preserved_when_supplied(client):
    """Verify client-supplied X-Request-ID is preserved in response."""
    custom_id = "aira-client-trace-12345"
    response = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response.headers.get("X-Request-ID") == custom_id


def test_404_not_found(client):
    """Verify 404 responses return structured JSON error with request ID."""
    response = client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "NOT_FOUND"
    assert "Resource not found" in data["error"]["message"] or "not found" in data["error"]["message"].lower()
    assert data["request_id"] == response.headers.get("X-Request-ID")


def test_405_method_not_allowed(client):
    """Verify 405 responses return structured JSON error with request ID."""
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "METHOD_NOT_ALLOWED"
    assert data["request_id"] == response.headers.get("X-Request-ID")


def test_500_internal_server_error(app, client):
    """Verify 500 responses return safe structured JSON without leaking trace details."""
    @app.get("/api/v1/test-error")
    def trigger_error():
        raise RuntimeError("Secret internal failure details")

    response = client.get("/api/v1/test-error")
    assert response.status_code == 500
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert data["error"]["message"] == "An internal server error occurred."
    assert "Secret internal failure details" not in response.get_data(as_text=True)
    assert data["request_id"] == response.headers.get("X-Request-ID")
