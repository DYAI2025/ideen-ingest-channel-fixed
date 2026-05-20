"""
Slack service-level unit tests.

Ported from the legacy flat ``backend/tests/test_slack.py`` (B1) and renamed
to the ``test_<scenario>__<expected>`` convention. These exercise the
pure-Python helpers in ``src.services.slack_service`` — no HTTP, no FastAPI.
"""

import hashlib
import hmac
import json
import time

# ---------------------------------------------------------------------------
# SlackSignatureVerifier (service-level, no HTTP)
# ---------------------------------------------------------------------------


def test_verifier_with_valid_hmac__returns_true():
    """Verifier accepts a signature computed with the matching secret."""
    from src.services.slack_service import SlackSignatureVerifier

    secret = "test_signing_secret_12345"
    timestamp = str(int(time.time()))
    body = json.dumps({"test": "data"})

    sig_base = f"v0:{timestamp}:{body}".encode()
    valid_sig = "v0=" + hmac.new(secret.encode(), sig_base, hashlib.sha256).hexdigest()

    verifier = SlackSignatureVerifier(secret)
    assert verifier.verify_signature(valid_sig, timestamp, body) is True


def test_verifier_with_invalid_hmac__returns_false():
    """Verifier rejects a literal/garbage signature even if timestamp is fresh."""
    from src.services.slack_service import SlackSignatureVerifier

    secret = "test_signing_secret_12345"
    timestamp = str(int(time.time()))
    body = json.dumps({"test": "data"})

    verifier = SlackSignatureVerifier(secret)
    assert verifier.verify_signature("v0=invalid_signature", timestamp, body) is False


# ---------------------------------------------------------------------------
# process_slack_message
# ---------------------------------------------------------------------------


def test_process_slack_message_with_full_event_callback__extracts_fields():
    """Given the full event_callback envelope, the processor must unwrap
    ``event`` and return channel/text/user/files_count."""
    from src.services.slack_service import process_slack_message

    event = {
        "token": "verification_token",
        "team_id": "T123456",
        "api_app_id": "A123456",
        "event": {
            "type": "message",
            "channel": "C123456",
            "user": "U123456",
            "text": "Test message",
            "ts": "1234567890.123456",
            "thread_ts": "1234567890.123456",
            "files": [],
        },
        "type": "event_callback",
        "event_id": "Ev123456",
        "event_time": 1234567890,
    }

    result = process_slack_message(event)
    assert result["status"] == "success"
    assert result["channel"] == "C123456"
    assert result["text"] == "Test message"
    assert result["user"] == "U123456"
    assert result["files_count"] == 0


# ---------------------------------------------------------------------------
# process_file_event
# ---------------------------------------------------------------------------


def test_process_file_event_with_full_event_callback__extracts_fields():
    """File-shared events expose id/name/url_private; the processor returns
    a uniform success dict with those fields."""
    from src.services.slack_service import process_file_event

    file_event = {
        "token": "verification_token",
        "team_id": "T123456",
        "api_app_id": "A123456",
        "event": {
            "type": "file_shared",
            "channel": "C123456",
            "user": "U123456",
            "file_id": "F123456",
            "file": {
                "id": "F123456",
                "name": "test.txt",
                "url_private": "https://files.slack.com/files/test",
            },
        },
        "type": "event_callback",
        "event_id": "Ev123456",
        "event_time": 1234567890,
    }

    result = process_file_event(file_event)
    assert result["status"] == "success"
    assert result["file_id"] == "F123456"
    assert result["file_name"] == "test.txt"
    assert result["file_url"] == "https://files.slack.com/files/test"
