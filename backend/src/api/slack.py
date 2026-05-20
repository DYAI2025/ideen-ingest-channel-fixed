"""
Slack API Router
Handles Slack webhook events and challenge responses
"""

from fastapi import APIRouter, HTTPException, Request, Header
from fastapi.responses import JSONResponse
from typing import Optional
import time
import logging

from ..services import slack_service
from ..services.slack_service import (
    process_slack_message,
    process_file_event,
    validate_timestamp,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/events")
async def slack_events_endpoint(
    request: Request,
    x_slack_signature: Optional[str] = Header(None, alias="X-Slack-Signature"),
    x_slack_request_timestamp: Optional[str] = Header(None, alias="X-Slack-Request-Timestamp"),
):
    """
    Handle Slack webhook events

    This endpoint receives:
    - URL verification challenges (during Slack app setup)
    - Event callbacks (messages, file shares, etc.)
    """
    try:
        # Read raw body for signature verification
        body_bytes = await request.body()
        body_str = body_bytes.decode("utf-8")

        # Parse JSON body
        import json

        body_data = json.loads(body_str)

        request_type = body_data.get("type")
        logger.info(f"Received Slack webhook request: {request_type}")

        # C5: Signature verification is unconditional for event_callback and
        # url_verification. Missing headers or an unconfigured verifier now
        # short-circuit to 401/503 (previously: deny-on-mismatch only — missing
        # headers fell through to the success path).
        if request_type in ("event_callback", "url_verification"):
            if slack_service.signature_verifier is None:
                logger.error("Slack signature verifier not configured")
                raise HTTPException(
                    status_code=503,
                    detail="Slack signature verifier not configured",
                )
            if not (x_slack_signature and x_slack_request_timestamp):
                logger.warning("Missing Slack signature headers")
                raise HTTPException(
                    status_code=401,
                    detail="Missing X-Slack-Signature or X-Slack-Request-Timestamp",
                )
            if not slack_service.signature_verifier.verify_signature(
                x_slack_signature, x_slack_request_timestamp, body_str
            ):
                logger.warning("Signature verification failed")
                raise HTTPException(status_code=401, detail="Invalid Slack signature")

        # Handle URL verification challenge
        if request_type == "url_verification":
            challenge = body_data.get("challenge")
            logger.info("Processing URL verification challenge")
            return JSONResponse(content={"challenge": challenge})

        # Handle event callbacks
        if request_type == "event_callback":
            event = body_data.get("event", {})
            event_type = event.get("type")
            logger.info(f"Processing event callback: {event_type}")

            # Process different event types
            if event_type == "message":
                result = process_slack_message(event)
                return JSONResponse(content={"status": "received", "result": result})

            elif event_type == "file_shared":
                result = process_file_event(event)
                return JSONResponse(content={"status": "received", "result": result})

            else:
                # Acknowledge other event types
                logger.info(f"Acknowledged event type: {event_type}")
                return JSONResponse(content={"status": "received", "event_type": event_type})

        # Unknown request type - return 400 as expected by test
        logger.warning(f"Unknown request type: {request_type}")
        return JSONResponse(
            content={"error": "Unknown request type", "status": "error"}, status_code=400
        )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in request body")
        return JSONResponse(content={"error": "Invalid JSON", "status": "error"}, status_code=400)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception:
        # C8: log full trace server-side, return an opaque message to the
        # caller. The previous implementation interpolated str(e) into the
        # response body which leaked internal details to unauthenticated
        # callers.
        logger.exception("Internal error processing Slack webhook")
        return JSONResponse(
            content={"error": "Internal error", "status": "error"}, status_code=500
        )
