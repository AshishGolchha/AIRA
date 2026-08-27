import hashlib
import hmac
import ipaddress
import json
import socket
from datetime import datetime, timezone
from typing import Any, Callable
from urllib.parse import urlparse
from flask import current_app, has_app_context

from app.services.notifications.base import BaseNotificationProvider


class WebhookNotificationProvider(BaseNotificationProvider):
    """External webhook alert notification provider with strict SSRF protection and HMAC signing."""

    def __init__(
        self,
        timeout: float = 5.0,
        dispatch_fn: Callable[..., bool] | None = None,
        allow_http_in_tests: bool = False,
    ):
        self.timeout = timeout
        self._dispatch_fn = dispatch_fn
        self._allow_http_in_tests = allow_http_in_tests
        self.sent_webhooks: list[dict[str, Any]] = []

    @staticmethod
    def is_safe_url(url: str, allow_http: bool = False) -> tuple[bool, str | None]:
        """Validates that destination URL is safe against SSRF attacks and dangerous protocols."""
        if not url or not isinstance(url, str):
            return False, "URL is required and must be a string."

        url = url.strip()
        parsed = urlparse(url)

        valid_schemes = ("https", "http") if allow_http else ("https",)
        if parsed.scheme.lower() not in valid_schemes:
            return False, f"URL scheme must be HTTPS{' or HTTP' if allow_http else ''}."

        hostname = parsed.hostname
        if not hostname:
            return False, "URL must contain a valid hostname."

        # Check for banned keywords
        if hostname.lower() in ("localhost", "0.0.0.0", "127.0.0.1", "::1", "metadata.google.internal"):
            return False, "Localhost and cloud internal hostnames are blocked."

        # Resolve IP addresses and verify they are globally routable / public
        try:
            # Check if hostname is already an IP address
            try:
                ip = ipaddress.ip_address(hostname)
                if (
                    ip.is_private
                    or ip.is_loopback
                    or ip.is_link_local
                    or ip.is_multicast
                    or ip.is_reserved
                    or ip.is_unspecified
                ):
                    return False, f"Private/loopback IP address {ip} is blocked."
            except ValueError:
                # Hostname is a domain name - resolve IPs
                addr_info = socket.getaddrinfo(hostname, None)
                for item in addr_info:
                    sockaddr = item[4]
                    ip_str = sockaddr[0]
                    ip = ipaddress.ip_address(ip_str)
                    if (
                        ip.is_private
                        or ip.is_loopback
                        or ip.is_link_local
                        or ip.is_multicast
                        or ip.is_reserved
                        or ip.is_unspecified
                    ):
                        return False, f"Resolved IP address {ip} for host {hostname} is in a blocked network range."
        except (socket.gaierror, socket.herror, Exception) as e:
            if not allow_http:
                return False, f"Could not safely resolve hostname {hostname}: {e}"

        return True, None

    def build_payload(self, alert: dict[str, Any]) -> dict[str, Any]:
        """Constructs standardized webhook event JSON payload."""
        return {
            "event": "investment_alert",
            "alert": {
                "id": alert.get("id"),
                "symbol": alert.get("symbol"),
                "company_name": alert.get("company_name"),
                "alert_type": alert.get("alert_type"),
                "severity": alert.get("severity"),
                "title": alert.get("title"),
                "message": alert.get("message"),
                "facts": alert.get("facts") or {},
                "sources": alert.get("sources") or [],
                "created_at": alert.get("created_at"),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def compute_signature(self, payload_bytes: bytes, secret_key: str) -> str:
        """Computes HMAC-SHA256 signature for payload verification."""
        sig = hmac.new(secret_key.encode("utf-8"), payload_bytes, hashlib.sha256).hexdigest()
        return f"sha256={sig}"

    def send_alert_notification(
        self,
        user_id: int,
        alert: dict[str, Any],
        endpoint_url: str | None = None,
        secret_key: str | None = None,
        **kwargs,
    ) -> bool:
        """Dispatches alert webhook to the specified endpoint with signature and failure isolation."""
        if not user_id or not alert or not alert.get("id"):
            return False

        if not endpoint_url:
            if has_app_context():
                current_app.logger.warning(f"Webhook delivery skipped: missing endpoint URL for user {user_id}")
            return False

        allow_http = self._allow_http_in_tests or (
            has_app_context() and current_app.config.get("TESTING", False)
        )
        is_safe, error_msg = self.is_safe_url(endpoint_url, allow_http=allow_http)
        if not is_safe:
            if has_app_context():
                current_app.logger.warning(f"Webhook SSRF validation failed for URL '{endpoint_url}': {error_msg}")
            return False

        payload = self.build_payload(alert)
        payload_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "AIRA-Alert-Webhook/1.0",
        }
        if secret_key:
            headers["X-AIRA-Signature"] = self.compute_signature(payload_bytes, secret_key)

        record = {
            "user_id": user_id,
            "endpoint_url": endpoint_url,
            "payload": payload,
            "headers": headers,
        }
        self.sent_webhooks.append(record)

        if self._dispatch_fn:
            return bool(self._dispatch_fn(record))

        # Standard HTTP dispatch using urllib.request with timeout
        import urllib.request
        req = urllib.request.Request(
            endpoint_url,
            data=payload_bytes,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return 200 <= resp.status < 300
        except Exception as e:
            if has_app_context():
                current_app.logger.warning(f"Webhook HTTP delivery failed for {endpoint_url}: {e}")
            return False
