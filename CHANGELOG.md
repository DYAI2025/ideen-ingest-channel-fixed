# Changelog

All notable changes to this project are documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versionierung erfolgt vorerst nicht — Datum-Sortierung reicht für die Pre-Iter-0-Phase.

## [Unreleased]

### Pre-Iter-0

- **ADR-Stack (ADR-004 … ADR-015):** 12 Architekturentscheidungen dokumentiert in `docs/adr/`. Jede ADR enthält Pflicht-Sektion `Alternatives Rejected`.
- **IMPLEMENTATION_PLAN_TDD.md v2:** iterativer Plan mit Test-Specs, Review-Gates, Rollback-Pfaden, CI-Split (`ci-fast` / `ci-deep`).
- **IMPLEMENTATION_PLAN_TDD_v2_findings.md:** Audit-Trail v1 → v2 (BLOCKER / HIGH / MEDIUM / LOW Findings + Fixes).
- **CLAUDE.md (Repo-Root):** projektspezifische Hinweise für Claude-Code-Sessions, mit Architektur-Map und Port-Hinweisen.
- **Preflight-Infra:**
  - `backend/pyproject.toml`: Dev-Dependencies erweitert um diff-cover, freezegun, mutmut, pytest-cov, pytest-randomly, pytest-xdist, respx, schemathesis, vcrpy (siehe Plan §2.1).
  - `backend/pytest.ini`: `asyncio_mode = auto`, Markers für `slow / serial / stress / fuzz / load / e2e`, **kein** globales `--cov-fail-under` (Diff-Coverage-Gate kommt via `diff-cover` in CI).
  - `backend/tests/_helpers/`: `race.py` (`run_race`) und `rls.py` (`as_workspace`, `assert_cross_workspace_query_empty`) als Stubs mit dokumentierter API für Iter 2 / Iter 5.
  - `backend/tests/test_agents_api.py`: Slug-Fix — Tests skippen sauber, wenn die `gbrain` CLI fehlt; kein `KeyError` mehr.
  - `frontend/package.json`: vitest, @testing-library/react, @playwright/test, msw, jsdom, @vitest/coverage-v8 als devDependencies.
  - `frontend/vitest.config.ts`, `frontend/tests/setup.ts`, leere `tests/{unit,integration,e2e}/`-Ordner.
  - `docker-compose.test.yml`: Postgres mit `max_connections=120` + Redis für Integration-Tests.
  - `.github/workflows/ci-fast.yml`: lint, unit, integration-fast, contract-snapshot, diff-coverage (< 5 min Budget).
  - `.github/workflows/ci-deep.yml`: schemathesis, mutation, e2e, migration-check, smoke-deploy (nightly + Label `release`, < 25 min Budget).
- **Preflight-Fix (chore/preflight-fix):**
  - `.github/workflows/ci-fast.yml`: alle `|| true`-Suppressions in `backend lint`, `frontend lint + typecheck`, `frontend unit`, `diff-coverage` entfernt; `astral-sh/setup-uv` von `@v3` auf `@v8` gepinnt (verifiziert via GitHub Releases API).
  - Backend-weiter Black-Format-Pass auf `src/` + `tests/` als separater Commit; `backend/pyproject.toml` Dev-Group um `black` erweitert.
  - `frontend/eslint.config.js`: eslint-plugin-react-hooks v7 Compiler-Rules (`set-state-in-effect`, `set-state-in-render`, `purity`, `refs`, `immutability`) und `@typescript-eslint/no-explicit-any` auf `warn` gesenkt mit dokumentierten Sunset-Klauseln; `no-unused-vars` honoriert `_`-Präfix.
  - `frontend/src/KanbanBoard.tsx`, `frontend/src/ObsidianGraph.tsx`: zwei scoped `// eslint-disable-next-line` mit Begründung.
  - `.gitignore`: ergänzt um `*.zip`, `ruvector.db`, `.claude/`, `.venv/`, `.pytest_cache/`, `.ruff_cache/`, `coverage.xml`, `PRJCT__save_*.md`, `ideen_architektur_deliverables*/`.
  - `docs/adr/ADR-016-governance-waiver-preflight-no-review.md`: dokumentiert den einmaligen Skip des Reviewer-Chain auf PR #5 und PR #6; Sunset ab Iter 0.
  - GitHub-Issue #8 verfolgt Sunset des temporären `diff-cover --exclude` für `src/api`/`src/services` (zu schließen vor dem ersten Iter-0-PR).
- **Preflight-Fix-2 (chore/preflight-fix-2):**
  - I1: `diff-cover --exclude` Glob ersetzt durch explizite 11-Datei-Liste mit `*`-Wildcard-Prefix (fnmatch-Anforderung). Future-Files unter `src/api`/`src/services` durchlaufen jetzt den 80%-Gate.
  - I2: `unit`-Job aufgeteilt in parallele `unit-backend` + `unit-frontend`. Backend-Pytest-Fail koppelt nicht mehr Frontend-Signale ab. `diff-coverage.needs` auf `unit-backend` aktualisiert.
  - I3: `scripts/check_reviewer_chain.sh` + `reviewer-chain-attestation`-Job in `ci-fast.yml`. Verlangt `Reviewer-Chain Findings-Disposition`-Tabelle in PR-Body, Issue-Kommentaren, Review-Bodies oder Review-Thread-Kommentaren. Distinct exit codes 0/1/2 für found/missing/infra. Lenient regex-Matching (case-insensitive, flexible separator). Explizite `permissions: pull-requests: read, contents: read`.
  - I4: Misplaced-Test-Guard-Step in `unit-frontend` blockt Test-Dateien unter `frontend/src/` (Top-Level + Nested). `set -euo pipefail` + `--`-anchored pathspec.
  - ADR-016 referenziert + Sunset-Issue #8 mit fnmatch-Pitfall-Kommentar dokumentiert.
- **Iter-0 Launchpad (chore/iter-0-launchpad):**
  - GitHub-Admin: 11 Iter-Milestones (`iter-0` … `iter-10`) angelegt; Labels `sunset`, `blocker`, `iter-0` … `iter-10` angelegt; Issue #8 erhält `blocker` + `sunset` + `iter-0`-Label + Milestone + Assignee.
  - 12 Sunset-Tracker-Issues (#11–#22) eröffnet, je verlinkt mit zugehörigem Iter-Milestone.
  - ADR-017 (`docs/adr/ADR-017-llm-openrouter-supersedes-anthropic.md`): OpenRouter ersetzt Anthropic als Default-LLM-Provider hinter `LLMProvider`-Interface (User-Direktive). VCR-Cassette-Disziplin aus ADR-009 bleibt; nur Provider-Implementierung ändert sich. Modellwahl via `OPENROUTER_MODEL` Runtime-Config.
  - ADR-009 Status auf `Superseded by ADR-017`. ADR-README aktualisiert.
  - `docs/IMPLEMENTATION_PLAN_TDD.md` D6-Tabelle + ADR-Tabelle auf OpenRouter umgestellt.
  - Branch-Protection auf `main` aktiviert mit 7 required Checks (`lint`, `unit-backend`, `unit-frontend`, `integration-fast`, `contract-snapshot`, `diff-coverage`, `reviewer-chain-attestation`) + `enforce_admins: true`. Bypass für Owner-Merges deaktiviert. ADR-016 §2 vorgezogen aus Iter 10.
  - `.env` bleibt lokal-only (gitignored). CI-Secret-Name dokumentiert als `OPENROUTER_API_KEY`.
- **Slack-PR Hardening (chore/2026-05-20-slack-hardening-fixes):**
  - C5: signature verification unconditional for `event_callback` + `url_verification` (missing headers → 401, war 200 mit deny-on-mismatch).
  - C6: URL-verification challenge requires valid signature BEFORE responding (war: 200 + challenge ohne jeden Check).
  - C7: `init_slack_service` fail-closed boot when `SLACK_SIGNING_SECRET` unset; debug-mode `"test_secret"` fallback removed. Opt-in via `ALLOW_INSECURE_SLACK_FOR_TESTS=1`.
  - C8: 500 responses no longer leak exception detail; full trace logged server-side via `logger.exception`.
  - C9: module-level `signature_verifier` singleton replaced with `@lru_cache get_signature_verifier()` factory + FastAPI `Depends`. Handler protected lazily even without explicit init call.
  - C4/I12: signature verification BEFORE `json.loads`. Always-verify (not type-gated). Unauthenticated callers cannot probe JSON parser.
  - I1/I2/I3: test-theatre (`test_slack_event_endpoint_not_implemented`, `test_challenge_response_not_implemented` — die `v0=test_signature` bogus headers benutzten und 200 erwarteten) durch real-HMAC-Tests ersetzt.
  - I4: `backend/tests/test_slack.py` flat → `tests/unit/test_slack_sig.py` + `test_slack_init.py` + `test_slack_service.py` + `tests/integration/test_slack.py`. Plus `tests/_helpers/slack.py::_sign`.
  - I5: hand-rolled HMAC durch `slack_sdk.signature.SignatureVerifier`-Wrapper ersetzt. Eigene strict-less-than-300s Timestamp-Window-Behavior bleibt.
  - I7: `mypy --strict` Annotations auf `backend/src/services/slack_service.py`.
  - I8: unused `validate_timestamp` free-function entfernt.
  - I9: Timestamp-Window-Edge-Tests (299/300/301 + 600s future-skew) via `freezegun`.
  - Iter-deferred Findings (Tracker-Issues #24–#30): C1 (Audit), C2 (arq Iter 6), C3 (dedup Iter 2), C4-tracker (OAuth Iter 4), I6 (OpenAPI Iter 1), I10 (= C3), I11 (CORS Iter 1).
  - Pre-existing Slack-PR (commit `1ae481f`) Schwarmcommits dokumentiert als Beispiel des `1ae481f → branch-protection`-Failure-Modes, den PR #23 nachträglich verhindert.
