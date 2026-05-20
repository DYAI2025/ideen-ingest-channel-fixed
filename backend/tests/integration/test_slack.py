"""
Slack integration tests.

Covers:
- C9 lazy-init protection (handler is protected before init_slack_service is
  ever called, via the @lru_cache(get_signature_verifier) factory).
- B2 positive path: a fully-signed event_callback is accepted and dispatched
  to process_slack_message.
- B1-ported error-handling path: an unrecognised request type still returns
  400 ``status:error`` (no signature required, because the type-gated
  signature check only runs for ``event_callback`` / ``url_verification``).
"""

import importlib
import json
import time

from fastapi.testclient import TestClient

from tests._helpers.slack import _sign


def test_no_init_call__handler_still_protected(monkeypatch):
    """C9: an unauthenticated POST against /api/slack/events must NOT
    succeed when nobody has called init_slack_service. The lazy factory
    @lru_cache get_signature_verifier() must be wired so the handler is
    protected by default.

    We force a clean state by clearing the @lru_cache and the module-
    level singleton, then send an unsigned event_callback. Expected:
    401 (missing headers) — NOT 200.
    """
    monkeypatch.setenv("ALLOW_INSECURE_SLACK_FOR_TESTS", "1")

    # Reload slack_service to ensure no stale module-level state. The
    # @lru_cache must be cleared too — see C9 fix.
    import src.services.slack_service as slack_service_module

    importlib.reload(slack_service_module)
    # Clear any cached verifier so the factory rebuilds on first request.
    if hasattr(slack_service_module, "get_signature_verifier"):
        slack_service_module.get_signature_verifier.cache_clear()
    # Also defeat any lingering module global from earlier tests.
    if hasattr(slack_service_module, "signature_verifier"):
        slack_service_module.signature_verifier = None

    # IMPORTANT: do NOT call init_slack_service() — the handler must be
    # protected even without an explicit init call.
    from src.main import app

    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        json={
            "type": "event_callback",
            "event_id": "EvX1",
            "event": {"type": "message", "text": "hi"},
        },
        # NOTE: no signature headers
    )

    assert response.status_code != 200, (
        f"handler returned 200 without init+signature — bypass! body={response.text}"
    )
    assert response.status_code == 401, (
        f"expected 401 (missing headers), got {response.status_code}: {response.text}"
    )


def test_event_callback_with_valid_signature__200_and_processes():
    """B2 positive path (replaces the C5 ``test_slack_event_endpoint_not_implemented``
    theatre test): a fully-signed event_callback must be accepted (200) and
    the response body must include the processed result from
    ``process_slack_message``."""
    from src.main import app
    from src.services.slack_service import init_slack_service

    init_slack_service("test_secret")

    body_obj = {
        "token": "verification_token",
        "team_id": "T123456",
        "api_app_id": "A123456",
        "event": {
            "type": "message",
            "channel": "C123456",
            "user": "U123456",
            "text": "Test message",
            "ts": "1234567890.123456",
            "files": [],
        },
        "type": "event_callback",
        "event_id": "Ev123456",
        "event_time": 1234567890,
    }
    body = json.dumps(body_obj).encode()
    timestamp = str(int(time.time()))
    sig = _sign("test_secret", timestamp, body)

    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        content=body,
        headers={
            "X-Slack-Signature": sig,
            "X-Slack-Request-Timestamp": timestamp,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "received"
    assert "result" in data
    assert data["result"]["channel"] == "C123456"
    assert data["result"]["text"] == "Test message"
    assert data["result"]["user"] == "U123456"


def test_unknown_request_type__400_error_envelope():
    """Ported from legacy ``test_error_handling_not_implemented``: an
    unrecognised request type (no ``type`` or unknown value) must produce
    a 400 with ``{"status": "error", "error": ...}``.

    C4/I12 update: the handler now verifies the signature on the raw body
    BEFORE parsing JSON or dispatching by type. This test therefore must
    send a valid signature; the meaning of the assertion is still ``a
    well-formed but unknown-typed payload returns 400``, just from inside
    the authenticated path.
    """
    from src.main import app
    from src.services.slack_service import init_slack_service

    init_slack_service("test_secret")

    body_obj = {"invalid": "data"}
    body = json.dumps(body_obj).encode()
    timestamp = str(int(time.time()))
    sig = _sign("test_secret", timestamp, body)

    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        content=body,
        headers={
            "X-Slack-Signature": sig,
            "X-Slack-Request-Timestamp": timestamp,
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 400, response.text
    body_json = response.json()
    assert body_json["status"] == "error"
    assert "error" in body_json
