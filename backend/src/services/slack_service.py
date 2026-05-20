"""
Slack Service
Handles Slack webhook events, signature verification, and message processing
"""

import time
import hmac
import hashlib
import logging
from typing import Dict, Any, Optional
from ..core.config import settings

logger = logging.getLogger(__name__)


class SlackSignatureVerifier:
    """Verifies Slack webhook signatures"""

    def __init__(self, signing_secret: str):
        self.signing_secret = signing_secret

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

        # Check timestamp freshness (prevent replay attacks)
        if not self._is_timestamp_valid(timestamp):
            logger.warning(f"Invalid timestamp in request: {timestamp}")
            return False

        # Create signature
        sig_basestring = f"v0:{timestamp}:{body}".encode("utf-8")
        my_signature = (
            "v0="
            + hmac.new(
                self.signing_secret.encode("utf-8"), sig_basestring, hashlib.sha256
            ).hexdigest()
        )

        # Compare signatures
        is_valid = hmac.compare_digest(my_signature, signature)
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


def validate_timestamp(timestamp: str) -> bool:
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


def init_slack_service():
    """Initialize Slack service with configuration"""
    global signature_verifier
    # Load signing secret from environment/config
    signing_secret = settings.slack_signing_secret
    if not signing_secret:
        if settings.debug:
            logger.warning("SLACK_SIGNING_SECRET not set - using test secret (not for production)")
            signing_secret = "test_secret"
        else:
            raise ValueError("SLACK_SIGNING_SECRET must be set in production mode")

    signature_verifier = SlackSignatureVerifier(signing_secret)
    logger.info("Slack service initialized successfully")
