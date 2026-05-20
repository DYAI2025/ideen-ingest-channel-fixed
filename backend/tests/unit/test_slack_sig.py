"""
Slack signature verification unit tests (C5, C6).
"""

from fastapi.testclient import TestClient

from src.main import app
from src.services.slack_service import init_slack_service


def test_missing_signature_header__rejected_401():
    """C5: event_callback without X-Slack-Signature header must be rejected with 401."""
    # Initialise the global verifier (current API takes no args; debug-mode
    # fallback supplies "test_secret"). A3 will introduce an explicit
    # signing_secret arg.
    init_slack_service()
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
    init_slack_service()
    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        json={"type": "url_verification", "challenge": "secret_challenge"},
        # NOTE: no signature headers
    )
    assert response.status_code == 401
    # Ensure the challenge value is NOT echoed back even partially.
    assert "secret_challenge" not in response.text
