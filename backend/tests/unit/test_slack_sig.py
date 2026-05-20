"""
Slack signature verification unit tests (C5, C6, C8 + B2 real-HMAC gate).
"""

import time

from fastapi.testclient import TestClient

from src.main import app
from src.services.slack_service import init_slack_service
from tests._helpers.slack import _sign


def test_missing_signature_header__rejected_401():
    """C5: event_callback without X-Slack-Signature header must be rejected with 401."""
    # Initialise the global verifier (current API takes no args; debug-mode
    # fallback supplies "test_secret"). A3 will introduce an explicit
    # signing_secret arg.
    init_slack_service("test_secret")
    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        json={
            "type": "event_callback",
            "event_id": "EvX1",
            "event": {"type": "message", "text": "hi"},
        },
        # NOTE: no X-Slack-Signature, no X-Slack-Request-Timestamp
    )
    assert response.status_code == 401, (
        f"expected 401, got {response.status_code}: {response.text}"
    )


def test_url_verification_without_signature__rejected_401():
    """C6: url_verification without signature headers must be rejected with 401
    BEFORE the challenge response is returned. Previously the challenge was
    echoed back unconditionally — leaking confirmation that the endpoint
    exists and letting an unauthenticated caller complete Slack's URL
    verification ritual.
    """
    init_slack_service("test_secret")
    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        json={"type": "url_verification", "challenge": "secret_challenge"},
        # NOTE: no signature headers
    )
    assert response.status_code == 401
    # Ensure the challenge value is NOT echoed back even partially.
    assert "secret_challenge" not in response.text


def test_internal_error_response_does_not_leak_exception(monkeypatch):
    """C8: a raised ValueError must be logged server-side but the response
    body must not contain the exception's message text."""
    import hashlib
    import hmac

    init_slack_service("test_secret")
    # Compute a valid signature so the request reaches process_slack_message.
    timestamp = str(int(__import__("time").time()))
    body = '{"type":"event_callback","event":{"type":"message","text":"hi"}}'
    sig_base = f"v0:{timestamp}:{body}".encode()
    sig = "v0=" + hmac.new(b"test_secret", sig_base, hashlib.sha256).hexdigest()

    def _boom(_event):
        raise ValueError("SECRET INTERNAL DETAIL")

    monkeypatch.setattr("src.api.slack.process_slack_message", _boom)

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

    assert response.status_code == 500, (
        f"expected 500, got {response.status_code}: {response.text}"
    )
    assert "SECRET INTERNAL DETAIL" not in response.text, (
        f"response leaked exception detail: {response.text}"
    )


# ---------------------------------------------------------------------------
# B2 / I1+I2+I3 — real-HMAC signature gate tests.
# The old test_slack.py used the literal "v0=test_signature" and asserted
# the handler returned 200. That was test-theatre that codified the C5
# bypass. These tests compute REAL HMAC signatures against the configured
# secret so they actually exercise the gate.
# ---------------------------------------------------------------------------


def _build_signed_request(secret: str = "test_secret", *, timestamp: str | None = None):
    """Build the (body, headers) pair for a fully-signed event_callback."""
    body = (
        b'{"type":"event_callback","event_id":"EvB2",'
        b'"event":{"type":"message","channel":"C1","user":"U1","text":"hi"}}'
    )
    if timestamp is None:
        timestamp = str(int(time.time()))
    sig = _sign(secret, timestamp, body)
    headers = {
        "X-Slack-Signature": sig,
        "X-Slack-Request-Timestamp": timestamp,
        "Content-Type": "application/json",
    }
    return body, headers


def test_valid_signature__accepted():
    """B2 positive: a request signed with the correct secret + fresh
    timestamp must pass the signature gate (200). This is a positive
    smoke that complements the negative tests below; landing GREEN on
    first run is expected because Sub-Job A's hardening preserved the
    happy path."""
    init_slack_service("test_secret")
    body, headers = _build_signed_request("test_secret")

    client = TestClient(app)
    response = client.post("/api/slack/events", content=body, headers=headers)

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "received"


def test_invalid_signature__rejected_401():
    """B2 I1: a request whose HMAC was computed with the WRONG secret
    must be rejected with 401 — not silently accepted."""
    init_slack_service("test_secret")
    body, _ = _build_signed_request("test_secret")
    timestamp = str(int(time.time()))
    # Sign with a different secret — the gate must catch the mismatch.
    bad_sig = _sign("wrong_secret", timestamp, body)
    headers = {
        "X-Slack-Signature": bad_sig,
        "X-Slack-Request-Timestamp": timestamp,
        "Content-Type": "application/json",
    }

    client = TestClient(app)
    response = client.post("/api/slack/events", content=body, headers=headers)

    assert response.status_code == 401, (
        f"expected 401, got {response.status_code}: {response.text}"
    )


def test_malformed_signature_prefix__rejected_401():
    """B2 I2: a signature header that lacks the ``v0=`` prefix (or uses a
    different version like ``v1=``) must be rejected. ``hmac.compare_digest``
    is constant-time but only returns True for byte-identical strings, so a
    ``v1=...`` prefix cannot match the verifier's ``v0=...`` recomputation."""
    init_slack_service("test_secret")
    body, _ = _build_signed_request("test_secret")
    timestamp = str(int(time.time()))
    # Compute the correct v0 digest but flip the version prefix to v1.
    correct_sig = _sign("test_secret", timestamp, body)
    assert correct_sig.startswith("v0=")
    malformed = "v1=" + correct_sig[3:]
    headers = {
        "X-Slack-Signature": malformed,
        "X-Slack-Request-Timestamp": timestamp,
        "Content-Type": "application/json",
    }

    client = TestClient(app)
    response = client.post("/api/slack/events", content=body, headers=headers)

    assert response.status_code == 401, (
        f"expected 401, got {response.status_code}: {response.text}"
    )


def test_wrong_length_signature__rejected_401():
    """B2 I3: a signature with the right ``v0=`` prefix but a truncated /
    elongated digest must be rejected. ``hmac.compare_digest`` should be
    constant-time and length-aware; we don't want a length-mismatch to
    leak through (or, worse, raise and 500)."""
    init_slack_service("test_secret")
    body, _ = _build_signed_request("test_secret")
    timestamp = str(int(time.time()))
    # Truncate the hex digest to 10 chars — wrong length, wrong content.
    correct = _sign("test_secret", timestamp, body)
    truncated = correct[: len("v0=") + 10]
    headers = {
        "X-Slack-Signature": truncated,
        "X-Slack-Request-Timestamp": timestamp,
        "Content-Type": "application/json",
    }

    client = TestClient(app)
    response = client.post("/api/slack/events", content=body, headers=headers)

    assert response.status_code == 401, (
        f"expected 401, got {response.status_code}: {response.text}"
    )
