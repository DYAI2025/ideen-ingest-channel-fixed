# Slack-PR Hardening (commit 1ae481f) Fix Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans / superpowers:subagent-driven-development to implement task-by-task.

**Goal:** Close 14 of the 21 actionable findings raised by `/code-review-excellence` against commit 1ae481f. Security-critical bypasses (C5–C9), test-theatre (I1–I3, I9), structural sloppiness (I4, I5, I7, I8, I12).

**Architecture:** All work scoped to `backend/src/api/slack.py`, `backend/src/services/slack_service.py`, `backend/tests/test_slack.py` (relocated + split). Optional minor touches in `backend/pyproject.toml`, `backend/src/main.py`, `backend/src/core/config.py`. No new runtime deps. No schema changes (those are Iter-2/4/6/8 work tracked in issues #24-#30).

**Tech Stack:** FastAPI, hmac/hashlib stdlib, pytest, hypothesis (already in dev-deps), TestClient.

**Reference:**
- Review source: chat log from `/code-review-excellence` on commit 1ae481f (2026-05-20).
- Plan: `docs/IMPLEMENTATION_PLAN_TDD.md` §2.5 reviewer-chain + §4 Iter 8 (target shape).
- Iter-blocked findings (NOT in this plan): tracker issues #24 (C1), #25 (C3), #30 (C2), #26 (C4), #27 (I6), #28 (I11), #29 (I10).

**Halt-on-defect rule:** Every Red test MUST fail on first run. If a Red test passes immediately, STOP and report — the assertion isn't reaching the code path under test. Do NOT proceed.

---

## Sub-Job A — Security-Critical (C5, C6, C7, C8, C9)

One commit per finding. Each finding gets a Red test before the fix where applicable.

### Task A1 — C5: signature verification unconditional

**Files:**
- Modify: `backend/src/api/slack.py` (the `if signature_verifier and x_slack_signature and x_slack_request_timestamp:` block)
- Test: `backend/tests/unit/test_slack_sig.py::test_missing_signature_header__rejected_401`

**Step 1: Red test**

```python
# backend/tests/unit/test_slack_sig.py
from fastapi.testclient import TestClient
from src.main import app
from src.services.slack_service import init_slack_service

def test_missing_signature_header__rejected_401():
    init_slack_service("test_secret")
    client = TestClient(app)
    # event_callback envelope without X-Slack-Signature header
    response = client.post(
        "/api/slack/events",
        json={"type": "event_callback", "event_id": "EvX1", "event": {"type": "message", "text": "hi"}},
        # NOTE: no X-Slack-Signature, no X-Slack-Request-Timestamp
    )
    assert response.status_code == 401, f"expected 401, got {response.status_code}: {response.text}"
```

**Step 2: Run test, verify it FAILS**

```
uv run pytest backend/tests/unit/test_slack_sig.py::test_missing_signature_header__rejected_401 -v
```
Expected: FAIL with status_code 200 (the current code lets it through).

**HALT-ON-DEFECT:** If this test passes on first run, the signature gate is *already* tighter than the review claims. Stop and surface — the review may have read stale code.

**Step 3: Apply fix**

Replace in `backend/src/api/slack.py`:
```python
if signature_verifier and x_slack_signature and x_slack_request_timestamp:
    if not signature_verifier.verify_signature(...):
        raise HTTPException(status_code=401, ...)
```
with:
```python
# Reject event_callback and url_verification without complete signature headers.
# C5/C6 fix: deny-on-omission (was deny-on-mismatch, allow-on-omission).
event_type = payload.get("type") if isinstance(payload, dict) else None
if event_type in ("event_callback", "url_verification"):
    if not signature_verifier:
        raise HTTPException(status_code=503, detail="Slack signature verifier not configured")
    if not (x_slack_signature and x_slack_request_timestamp):
        raise HTTPException(status_code=401, detail="Missing X-Slack-Signature or X-Slack-Request-Timestamp")
    if not signature_verifier.verify_signature(raw_body, x_slack_signature, x_slack_request_timestamp):
        raise HTTPException(status_code=401, detail="Invalid Slack signature")
```

**Step 4: Verify GREEN**

```
uv run pytest backend/tests/unit/test_slack_sig.py::test_missing_signature_header__rejected_401 -v
```
Expected: PASS.

**Step 5: Commit**

```
git add backend/src/api/slack.py backend/tests/unit/test_slack_sig.py
git commit -m "fix(slack): C5 reject event_callback without signature headers (was 200, now 401)

Red: test_missing_signature_header__rejected_401 failed before fix
     (assertion 401 got 200), passes after."
```

---

### Task A2 — C6: URL-verification signature-required

**Files:**
- Modify: `backend/src/api/slack.py` (move signature check ABOVE the URL-verification challenge response)
- Test: `backend/tests/unit/test_slack_sig.py::test_url_verification_without_signature__rejected_401`

**Step 1: Red test**

```python
def test_url_verification_without_signature__rejected_401():
    init_slack_service("test_secret")
    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        json={"type": "url_verification", "challenge": "secret_challenge"},
        # NOTE: no signature headers
    )
    assert response.status_code == 401
    assert "challenge" not in (response.json() if response.headers.get("content-type", "").startswith("application/json") else {})
```

**Step 2: Verify Red**

Expected: FAIL with status 200 + body `{"challenge": "secret_challenge"}` (current code returns challenge before any check).

**Step 3: Fix**

Move the signature-verification block (already strengthened in A1) so that for `url_verification` requests the same gating applies. Already implicitly covered by A1's `if event_type in ("event_callback", "url_verification")` clause, but ensure ordering: signature check must run BEFORE the `if payload.get("type") == "url_verification": return {"challenge": ...}` branch.

**Step 4–5: Verify GREEN + commit**

```
git commit -m "fix(slack): C6 verify signature before responding to url_verification

Red: test_url_verification_without_signature__rejected_401 failed
     before (200 + challenge leak), passes after (401)."
```

---

### Task A3 — C7: fail-closed boot when SLACK_SIGNING_SECRET is unset

**Files:**
- Modify: `backend/src/services/slack_service.py::init_slack_service`
- Modify: `backend/src/main.py` (startup behaviour)
- Test: `backend/tests/unit/test_slack_init.py::test_init_without_secret_in_prod_mode__raises`
- Test: `backend/tests/unit/test_slack_init.py::test_init_without_secret_with_test_override__allowed`

**Step 1: Red tests**

```python
import os
import pytest
from src.services.slack_service import init_slack_service

def test_init_without_secret_in_prod_mode__raises(monkeypatch):
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    monkeypatch.delenv("ALLOW_INSECURE_SLACK_FOR_TESTS", raising=False)
    with pytest.raises(RuntimeError, match="SLACK_SIGNING_SECRET"):
        init_slack_service(signing_secret=None)

def test_init_without_secret_with_test_override__allowed(monkeypatch):
    monkeypatch.delenv("SLACK_SIGNING_SECRET", raising=False)
    monkeypatch.setenv("ALLOW_INSECURE_SLACK_FOR_TESTS", "1")
    init_slack_service(signing_secret=None)  # should not raise
```

**Step 2: Verify Red**

Expected: First test FAILs (currently falls back to `"test_secret"` when debug=True default). Second passes vacuously or fails depending on current shape.

**Step 3: Fix**

Replace `init_slack_service` debug-gated fallback with explicit opt-in:
```python
def init_slack_service(signing_secret: str | None = None) -> "SlackSignatureVerifier":
    secret = signing_secret or os.environ.get("SLACK_SIGNING_SECRET")
    if not secret:
        if os.environ.get("ALLOW_INSECURE_SLACK_FOR_TESTS") == "1":
            secret = "test_secret"  # explicit opt-in for local dev
        else:
            raise RuntimeError("SLACK_SIGNING_SECRET not set; set ALLOW_INSECURE_SLACK_FOR_TESTS=1 for local-only test mode")
    global signature_verifier  # see A5 — DI replaces this
    signature_verifier = SlackSignatureVerifier(secret)
    return signature_verifier
```

**Step 4–5: GREEN + commit**

```
git commit -m "fix(slack): C7 fail-closed boot when SLACK_SIGNING_SECRET unset

Removes debug-mode fallback to literal 'test_secret'. Local-only opt-in
via ALLOW_INSECURE_SLACK_FOR_TESTS=1.

Red x2: prod-mode raises; test-override allowed. Both passing."
```

---

### Task A4 — C8: strip exception detail from 500 responses

**Files:**
- Modify: `backend/src/api/slack.py` (the `except Exception as e: ... JSONResponse({"error": f"Internal error: {str(e)}" ...})` block)
- Test: `backend/tests/unit/test_slack_sig.py::test_internal_error_response_does_not_leak_exception`

**Step 1: Red test**

Mock `process_slack_message` to raise `ValueError("SECRET INTERNAL DETAIL")`. Send a valid-signature event, assert 500 + body does NOT contain `"SECRET INTERNAL DETAIL"`.

**Step 2: Verify Red** — currently fails (body interpolates `str(e)`).

**Step 3: Fix**

```python
except Exception as e:
    logger.exception("Internal error processing Slack webhook")  # logs trace server-side
    return JSONResponse(content={"error": "Internal error"}, status_code=500)
```

**Step 4–5: GREEN + commit**

```
git commit -m "fix(slack): C8 do not return exception detail to caller (500 response)

Internal error string only logged server-side via logger.exception
(includes traceback). Response body is opaque 'Internal error'."
```

---

### Task A5 — C9: replace module-level mutable singleton with FastAPI Depends

**Files:**
- Modify: `backend/src/services/slack_service.py` (remove `signature_verifier = None` module global; add `get_signature_verifier()` factory)
- Modify: `backend/src/api/slack.py` (use `Depends(get_signature_verifier)`)
- Modify: `backend/src/main.py` (drop `init_slack_service()` from startup; verifier is built lazily on first request)
- Test: `backend/tests/integration/test_slack.py::test_no_init_call__handler_still_protected`

**Step 1: Red test**

Don't call `init_slack_service()` anywhere. POST to `/api/slack/events` with `event_callback`. Assert NOT 200 — should be 503 or boot failure.

**Step 2: Verify Red** — currently returns 200 because `signature_verifier` is `None` and the gate `if signature_verifier and ...` evaluates False, falling through to the `else` (which is the implicit success path in current code).

**Step 3: Fix**

Use `functools.lru_cache` factory:
```python
from functools import lru_cache

@lru_cache(maxsize=1)
def get_signature_verifier() -> SlackSignatureVerifier:
    secret = os.environ.get("SLACK_SIGNING_SECRET")
    if not secret:
        if os.environ.get("ALLOW_INSECURE_SLACK_FOR_TESTS") == "1":
            secret = "test_secret"
        else:
            raise RuntimeError("SLACK_SIGNING_SECRET required")
    return SlackSignatureVerifier(secret)
```

In `api/slack.py`:
```python
from fastapi import Depends
from src.services.slack_service import get_signature_verifier

@router.post("/events")
async def slack_events(
    request: Request,
    x_slack_signature: str | None = Header(None, alias="X-Slack-Signature"),
    x_slack_request_timestamp: str | None = Header(None, alias="X-Slack-Request-Timestamp"),
    verifier: SlackSignatureVerifier = Depends(get_signature_verifier),
):
    ...
```

**Step 4–5: GREEN + commit**

```
git commit -m "fix(slack): C9 replace module-singleton with FastAPI Depends

@lru_cache factory; verifier built lazily on first request. Eliminates
'verifier never initialized → bypass' failure mode caught by red test
test_no_init_call__handler_still_protected."
```

---

## Sub-Job B — Test-Theatre (I1, I2, I3, I4, I9)

### Task B1 — I4: relocate + split tests

**Files:**
- Move: `backend/tests/test_slack.py` → split into `backend/tests/unit/test_slack_sig.py` (already created in A1–A4) + `backend/tests/unit/test_slack_init.py` (from A3) + `backend/tests/integration/test_slack.py` (from A5)
- Delete: `backend/tests/test_slack.py` (after migration)

**Step 1: Confirm `tests/unit/` + `tests/integration/` dirs exist.** Create if absent: `mkdir -p backend/tests/unit backend/tests/integration`. Add `__init__.py` if other test dirs have them.

**Step 2: Migrate**

Move each test from `backend/tests/test_slack.py` to the appropriate file under unit/ or integration/, dropping the "_not_implemented" suffix per I-M10 (use `__valid__accepted`, `__invalid__rejected` form).

**Step 3: Delete the old flat file**

```
git rm backend/tests/test_slack.py
```

**Step 4: Run full suite from new locations**

```
cd backend && uv run pytest -m "not slow and not e2e and not stress and not fuzz and not load" tests/
```
Expected: same pass count as before migration (no regressions) + the new tests from A1–A5.

**Step 5: Commit**

```
git commit -m "test(slack): I4 split into tests/unit + tests/integration

backend/tests/test_slack.py → backend/tests/unit/test_slack_*.py +
backend/tests/integration/test_slack.py. Aligns with plan §2.1 layout
so pytest -m 'slow|fuzz' selectors work as intended."
```

---

### Task B2 — I1/I2/I3: add missing security tests + fix test-theatre

**Files:**
- `backend/tests/unit/test_slack_sig.py` — extend with:
  - `test_valid_signature__accepted`
  - `test_invalid_signature__rejected_401`
  - `test_malformed_signature_prefix__rejected_401`
  - `test_wrong_length_signature__rejected_401`
- `backend/tests/integration/test_slack.py` — replace `test_slack_event_endpoint_not_implemented` (which asserted 200 with a bogus signature, codifying the C5 exploit) with `test_event_callback_with_valid_signature__200_and_processes`.

**Step 1: Red — verify the new "valid signature accepted" test FAILS without a real signature**

The test must construct a real HMAC-SHA256 against `"test_secret"`, send the matching `v0=...` header. Helper:
```python
def _sign(secret: str, timestamp: str, body: bytes) -> str:
    import hmac, hashlib
    basestring = b"v0:" + timestamp.encode() + b":" + body
    digest = hmac.new(secret.encode(), basestring, hashlib.sha256).hexdigest()
    return f"v0={digest}"
```

**Step 2: Replace `test_slack_event_endpoint_not_implemented`**

The replacement test computes a real signature; assert 200 ONLY when signature is valid.

**Step 3: Run + verify**

The "test theatre" tests that previously asserted 200 with bogus sigs must be deleted or inverted to assert 401.

**Step 4: Commit**

```
git commit -m "test(slack): I1/I2/I3 replace test-theatre with real signature paths

Old: test_slack_event_endpoint_not_implemented asserted 200 with a
     bogus v0=test_signature header (codified the C5 exploit).
New: test_event_callback_with_valid_signature__200_and_processes
     constructs the real HMAC against the test secret; only that
     path returns 200. Invalid + missing variants assert 401."
```

---

### Task B3 — I9: timestamp window edge tests

**Files:**
- `backend/tests/unit/test_slack_sig.py` — add:
  - `test_timestamp_at_299s__accepted`
  - `test_timestamp_at_301s__rejected` 
  - `test_timestamp_future_skew_600s__rejected`
  - `test_timestamp_exactly_300s__rejected` (window is `< 300`, so 300 itself is out)

**Step 1: Red — set `time.time` via freezegun**

```python
from freezegun import freeze_time

@freeze_time("2026-05-20 12:00:00")
def test_timestamp_at_299s__accepted():
    ...
```

**Step 2: Run all four. Expected:** 299 PASSES (signature otherwise valid), 300/301 FAIL with 401, future-skew FAILs with 401.

If any one passes the wrong direction → halt-on-defect: window logic is broken in a way the original `test_timestamp_validation_not_implemented` missed.

**Step 3–4: GREEN + commit**

```
git commit -m "test(slack): I9 timestamp window edge cases

Adds 299/300/301 boundary tests + 600s future-skew. Window stays at
abs(diff) < 300 per Slack guidance. Tests use freezegun so clock
behavior is deterministic."
```

---

## Sub-Job C — Cleanup (I5, I7, I8, I12)

### Task C1 — I5: drop unused slack-sdk OR adopt SignatureVerifier

**Decision** (one commit either way):

**Option (a) — Drop:** `uv remove slack-sdk` + remove `slack-sdk>=3.27.0` from `pyproject.toml`. Justification: hand-rolled HMAC is fine and we have no other slack-sdk usage planned for Iter 8.

**Option (b) — Adopt:** Replace `SlackSignatureVerifier` hand-roll with `slack_sdk.signature.SignatureVerifier`. Smaller surface, well-tested upstream.

**Recommendation:** (b). Switching to upstream verifier removes A1/A2/A3/A4 worth of bespoke crypto code we have to maintain. Adopt it.

**Step 1: Refactor `backend/src/services/slack_service.py`**

```python
from slack_sdk.signature import SignatureVerifier as _SdkSignatureVerifier

class SlackSignatureVerifier:
    """Thin wrapper around slack_sdk.signature.SignatureVerifier so our type signature stays stable."""
    def __init__(self, signing_secret: str):
        self._inner = _SdkSignatureVerifier(signing_secret)

    def is_valid(self, body: bytes, timestamp: str, signature: str) -> bool:
        return self._inner.is_valid(body=body, timestamp=timestamp, signature=signature)
```

Update callers in `api/slack.py` accordingly.

**Step 2: Run full slack test suite**

All A1–A5 + B1–B3 tests must still pass with the new verifier under the hood (the wrapper API is identical from the handler's perspective).

**Step 3: Commit**

```
git commit -m "refactor(slack): I5 adopt slack_sdk.signature.SignatureVerifier

Replaces hand-rolled HMAC with upstream verifier. Wrapper preserves
our internal API surface so handler code unchanged. Drops ~30 lines
of bespoke crypto we don't need to maintain."
```

---

### Task C2 — I7: mypy strict annotations

**Files:**
- `backend/src/services/slack_service.py` — add return-type annotations to all public functions.
- Verify: `uv run mypy --strict backend/src/services/slack_service.py` exits 0.

**Step 1: Apply annotations.**

**Step 2: Run mypy strict.**

**Step 3: Commit**

```
git commit -m "fix(slack): I7 add return-type annotations for mypy --strict

mypy --strict backend/src/services/slack_service.py now exits 0.
Aligns with plan §2.4 'mypy strict für src/core und src/services'."
```

---

### Task C3 — I8: delete unused `validate_timestamp` export

**Files:**
- `backend/src/services/slack_service.py` — delete the free-function `validate_timestamp` (or fold it into the verifier's method if any caller needs it).
- `backend/src/api/slack.py` — drop the unused import.

**Step 1: Confirm no callers**

```
grep -rn "validate_timestamp" backend/
```
If any caller surfaces, switch to using the wrapper's `is_valid`.

**Step 2: Delete + run tests.**

**Step 3: Commit**

```
git commit -m "refactor(slack): I8 delete unused validate_timestamp export

Free function existed alongside verifier's internal _is_timestamp_valid
copy. Verifier method is the only path used. Removes dead code."
```

---

### Task C4 — I12: signature verify BEFORE JSON parse

**Files:**
- `backend/src/api/slack.py` — reorder `await request.body()` → signature verification → `json.loads(body)`.
- Test: `backend/tests/unit/test_slack_sig.py::test_malformed_json_with_invalid_signature__rejected_before_parse`

**Step 1: Red test**

```python
def test_malformed_json_with_invalid_signature__rejected_before_parse():
    init_slack_service("test_secret")
    client = TestClient(app)
    response = client.post(
        "/api/slack/events",
        content=b"this is not json",  # raw bytes
        headers={"X-Slack-Signature": "v0=bogus", "X-Slack-Request-Timestamp": "1234567890", "Content-Type": "application/json"},
    )
    assert response.status_code == 401  # NOT 400/500 from JSON parse failure
```

**Step 2: Verify Red** — currently fails with 500 or 400 from JSON parse, not 401.

**Step 3: Fix**

Move JSON parsing AFTER signature verification block.

**Step 4–5: GREEN + commit**

```
git commit -m "fix(slack): I12 verify signature before JSON parse

Unauthenticated malformed bodies now return 401 (not 400/500 from
json.loads). Removes a cheap DoS surface where the server did parse
work for forged callers."
```

---

## Final Tasks

### Task F1 — CHANGELOG entry

Append to `CHANGELOG.md` `Pre-Iter-0` block:

```markdown
- **Slack-PR Hardening (chore/2026-05-20-slack-hardening-fixes):**
  - C5: signature verification unconditional for event_callback + url_verification (was deny-on-mismatch only; missing headers now return 401).
  - C6: URL-verification challenge requires valid signature before responding.
  - C7: SLACK_SIGNING_SECRET fail-closed boot; debug-mode "test_secret" fallback removed. Local-only opt-in via ALLOW_INSECURE_SLACK_FOR_TESTS=1.
  - C8: 500 responses no longer leak exception detail; trace logged server-side via logger.exception.
  - C9: module-level signature_verifier singleton replaced with @lru_cache + FastAPI Depends.
  - I1/I2/I3: replaced test-theatre (tests that asserted 200 with bogus signatures, codifying the C5 exploit) with real HMAC-signed paths.
  - I4: tests/test_slack.py → tests/unit/test_slack_*.py + tests/integration/test_slack.py.
  - I5: adopted slack_sdk.signature.SignatureVerifier instead of hand-roll.
  - I7: mypy --strict annotations on src/services/slack_service.py.
  - I8: removed unused validate_timestamp free-function.
  - I9: timestamp window edge tests (299/300/301 + future-skew via freezegun).
  - I12: signature verification BEFORE JSON parse to remove cheap DoS surface.
  - Iter-deferred (#24-#30): C1 (audit), C2 (arq Iter 6), C3 (dedup Iter 2), C4 (OAuth Iter 4), I6 (OpenAPI Iter 1), I10 (= C3), I11 (CORS Iter 1).
```

Commit:
```
git commit -m "docs(changelog): Slack-PR hardening entry under Pre-Iter-0"
```

### Task F2 — Push + PR + reviewer chain + merge

- `git push -u origin chore/2026-05-20-slack-hardening-fixes`
- `gh pr create` with title `fix(slack): security + test hardening (commit 1ae481f follow-up)` and body containing the Reviewer-Chain Findings-Disposition table covering all 14 findings + the 7 Iter-deferred trackers.
- Watch ci-fast; merge once all 7 required checks pass.

---

## Definition of Done

- All 14 findings (C5–C9 + I1–I9 + I12) resolved with separate commits.
- 7 Iter-deferred findings tracked in issues #24-#30.
- PR `chore/2026-05-20-slack-hardening-fixes` merged on `main`.
- ci-fast green incl. `reviewer-chain-attestation`.
- `cd backend && uv run pytest -m "not slow..." tests/` returns ≥ 11 passed + new test additions; no flat `tests/test_slack.py` remaining.
- `grep -rn "validate_timestamp" backend/` returns 0 hits.
- `uv run mypy --strict backend/src/services/slack_service.py` exits 0.

---

## What this plan does NOT do

- Does not touch `chat_messages` or `slack_event_dedup` tables (Iter 2 via #25).
- Does not introduce arq queue (Iter 6 via #30).
- Does not add OAuth callback (Iter 4 via #26).
- Does not generate OpenAPI snapshot (Iter 1 via #27).
- Does not tighten CORS (Iter 1 via #28).
- Does not address M1–M12 (Minor findings; tracked in PR body only, not actioned).
