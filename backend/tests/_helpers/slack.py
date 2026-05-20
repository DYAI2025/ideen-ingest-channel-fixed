"""
Slack-specific test helpers.

`_sign` computes a real Slack v0 HMAC-SHA256 signature so tests stop relying
on the C5 exploit (literal ``v0=test_signature`` strings that the old handler
accepted unconditionally).
"""

import hashlib
import hmac


def _sign(secret: str, timestamp: str, body: bytes) -> str:
    """Compute the canonical Slack v0 signature header value.

    Slack docs: https://api.slack.com/authentication/verifying-requests-from-slack
    basestring = b"v0:" + timestamp + b":" + body
    signature  = "v0=" + hex(hmac_sha256(secret, basestring))
    """
    basestring = b"v0:" + timestamp.encode() + b":" + body
    digest = hmac.new(secret.encode(), basestring, hashlib.sha256).hexdigest()
    return f"v0={digest}"
