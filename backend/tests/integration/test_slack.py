"""
Slack integration tests (C9).
Verifies the handler is protected even when no caller has explicitly
invoked init_slack_service(); the verifier must be built lazily on the
first request via the @lru_cache factory.
"""

import importlib

from fastapi.testclient import TestClient


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
