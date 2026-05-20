"""
Slack service initialisation tests (C7).
Verifies fail-closed boot when SLACK_SIGNING_SECRET is unset, with an
explicit local-only opt-in via ALLOW_INSECURE_SLACK_FOR_TESTS=1.
"""

import pytest

from src.services.slack_service import init_slack_service


def test_init_without_secret_in_prod_mode__raises(monkeypatch):
    """C7: missing SLACK_SIGNING_SECRET must raise unless test override set."""
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    monkeypatch.delenv("ALLOW_INSECURE_SLACK_FOR_TESTS", raising=False)
    # Also patch the settings instance so the function does not see a
    # cached secret from .env / process env at import time.
    from src.core import config as _cfg

    monkeypatch.setattr(_cfg.settings, "slack_signing_secret", None, raising=True)

    with pytest.raises(RuntimeError, match="SLACK_SIGNING_SECRET"):
        init_slack_service(signing_secret=None)


def test_init_without_secret_with_test_override__allowed(monkeypatch):
    """C7: ALLOW_INSECURE_SLACK_FOR_TESTS=1 is the explicit opt-in for local
    test mode; init_slack_service must succeed and return a verifier."""
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    monkeypatch.setenv("ALLOW_INSECURE_SLACK_FOR_TESTS", "1")
    from src.core import config as _cfg

    monkeypatch.setattr(_cfg.settings, "slack_signing_secret", None, raising=True)

    # Should not raise.
    init_slack_service(signing_secret=None)
