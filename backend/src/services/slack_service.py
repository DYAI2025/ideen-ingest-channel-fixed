"""
Slack Service
Handles Slack webhook events, signature verification, and message processing
"""

import os
import time
import logging
from functools import lru_cache
from typing import Any, Dict, Optional, cast

from slack_sdk.signature import (  # type: ignore[import-not-found]
    SignatureVerifier as _UpstreamSignatureVerifier,
)

from ..core.config import settings

logger = logging.getLogger(__name__)


class SlackSignatureVerifier:
    """Verifies Slack webhook signatures.

    C1/I5: Thin wrapper around ``slack_sdk.signature.SignatureVerifier`` —
    delegates HMAC computation + constant-time comparison to the upstream
    library while preserving our handler-facing ``verify_signature`` API
    surface and our strict ``< 300`` timestamp window (upstream uses
    ``> 300`` which is one second more permissive at the boundary).
    """

    def __init__(self, signing_secret: str) -> None:
        self.signing_secret = signing_secret
        self._upstream = _UpstreamSignatureVerifier(signing_secret)

    def verify_signature(self, signature: str, timestamp: str, body: str) -> bool:
        """
        Verify Slack request signature

        Args:
            signature: X-Slack-Signature header value
            timestamp: X-Slack-Request-Timestamp header value
            body: Raw request body

        Returns:
            True if signature is valid, False otherwise
        """
        if not signature or not timestamp:
            logger.warning("Missing signature or timestamp in request")
            return False

        # Check timestamp freshness FIRST (prevent replay attacks). We keep
        # our own ``abs(diff) < 300`` strict-less-than window — upstream's
        # ``is_valid`` uses ``> 300`` (rejects > 5 minutes), so without this
        # explicit pre-check the boundary at exactly 300s would shift.
        if not self._is_timestamp_valid(timestamp):
            logger.warning(f"Invalid timestamp in request: {timestamp}")
            return False

        # Delegate HMAC computation + constant-time compare to slack-sdk.
        # ``cast`` keeps mypy --strict happy on environments where the
        # slack_sdk stubs aren't reachable from the type-checker's interpreter.
        is_valid = cast(
            bool,
            self._upstream.is_valid(
                body=body, timestamp=timestamp, signature=signature
            ),
        )
        if not is_valid:
            logger.warning("Signature verification failed")
        return is_valid

    def _is_timestamp_valid(self, timestamp: str) -> bool:
        """
        Validate timestamp is within acceptable range (5 minutes)

        Args:
            timestamp: Unix timestamp as string

        Returns:
            True if timestamp is valid, False otherwise
        """
        try:
            request_time = int(timestamp)
            current_time = int(time.time())
            # Accept requests within 5 minutes
            return abs(current_time - request_time) < 300
        except (ValueError, TypeError):
            return False


def process_slack_message(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Slack message event

    Args:
        event: Slack event dictionary (can be full event callback or just the inner event)

    Returns:
        Processing result
    """
    # Handle both full event callback and inner event formats
    if "event" in event:
        inner_event = event["event"]
    else:
        inner_event = event

    # Extract relevant information
    channel = inner_event.get("channel")
    text = inner_event.get("text")
    user = inner_event.get("user")
    thread_ts = inner_event.get("thread_ts")
    files = inner_event.get("files", [])

    logger.info(f"Processing message from user {user} in channel {channel}")

    # For now, just acknowledge receipt
    # TODO: Implement actual message processing logic
    return {
        "status": "success",
        "channel": channel,
        "text": text,
        "user": user,
        "thread_ts": thread_ts,
        "files_count": len(files),
    }


def process_file_event(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process Slack file event

    Args:
        event: Slack file event dictionary (can be full event callback or just the inner event)

    Returns:
        Processing result
    """
    # Handle both full event callback and inner event formats
    if "event" in event:
        inner_event = event["event"]
    else:
        inner_event = event

    # Extract file information
    file_data = inner_event.get("file", {})
    file_id = file_data.get("id")
    file_name = file_data.get("name")
    file_url = file_data.get("url_private")

    logger.info(f"Processing file event: {file_name} (ID: {file_id})")

    # For now, just acknowledge receipt
    # TODO: Implement actual file processing logic
    return {"status": "success", "file_id": file_id, "file_name": file_name, "file_url": file_url}


# Global signature verifier instance (will be initialized with proper secret)
signature_verifier: Optional[SlackSignatureVerifier] = None


def init_slack_service(signing_secret: Optional[str] = None) -> "SlackSignatureVerifier":
    """Initialize Slack service with configuration.

    Fail-closed boot (C7): if no signing secret can be resolved from the
    explicit argument, the configured settings value, or the process env,
    raise ``RuntimeError``. The only opt-out is the explicit env-var
    ``ALLOW_INSECURE_SLACK_FOR_TESTS=1`` which substitutes a literal
    ``"test_secret"`` — intended for local dev / pytest runs only.
    """
    global signature_verifier
    secret = (
        signing_secret
        or settings.slack_signing_secret
        or os.environ.get("SLACK_SIGNING_SECRET")
    )
    if not secret:
        if os.environ.get("ALLOW_INSECURE_SLACK_FOR_TESTS") == "1":
            logger.warning(
                "SLACK_SIGNING_SECRET not set - using test secret "
                "(ALLOW_INSECURE_SLACK_FOR_TESTS=1 opt-in; do NOT use in production)"
            )
            secret = "test_secret"
        else:
            raise RuntimeError(
                "SLACK_SIGNING_SECRET not set; set ALLOW_INSECURE_SLACK_FOR_TESTS=1 "
                "for local-only test mode"
            )

    signature_verifier = SlackSignatureVerifier(secret)
    # Keep the @lru_cache factory in sync with the explicit init call so the
    # FastAPI Depends path returns the same verifier instance.
    get_signature_verifier.cache_clear()
    get_signature_verifier.cache_set = signature_verifier  # type: ignore[attr-defined]
    logger.info("Slack service initialized successfully")
    return signature_verifier


@lru_cache(maxsize=1)
def get_signature_verifier() -> SlackSignatureVerifier:
    """C9: FastAPI dependency that lazily constructs the signature verifier
    on first request, replacing the previous mutable module-level singleton.

    The @lru_cache(maxsize=1) means subsequent requests reuse the same
    verifier instance until ``get_signature_verifier.cache_clear()`` is
    called (used by tests to swap secrets).

    If ``init_slack_service()`` has already populated the module-global
    ``signature_verifier``, prefer that — it lets the explicit init path
    (e.g. test fixtures passing ``"test_secret"``) override the env-driven
    construction.
    """
    if signature_verifier is not None:
        return signature_verifier
    secret = settings.slack_signing_secret or os.environ.get("SLACK_SIGNING_SECRET")
    if not secret:
        if os.environ.get("ALLOW_INSECURE_SLACK_FOR_TESTS") == "1":
            secret = "test_secret"
        else:
            raise RuntimeError(
                "SLACK_SIGNING_SECRET not set; set ALLOW_INSECURE_SLACK_FOR_TESTS=1 "
                "for local-only test mode"
            )
    return SlackSignatureVerifier(secret)
