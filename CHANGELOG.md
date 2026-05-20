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
