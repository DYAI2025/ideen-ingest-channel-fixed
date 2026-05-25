# Iterativer TDD-Implementationsplan — Ideen Ingest Channel × Vision

**Version:** v2 (nach `/ultrathink-craftsmanship`-Validierung)
**Datum:** 2026-05-20
**Vorgänger:** `PRJCT__save_2026-05-20_13-38-40.md` (Iterationsschnitt),
`ideen_architektur_deliverables (1)/ideen_backend_architektur_handoff.md` (Architektur, ADRs, Schema).
**Validierungsbericht v1→v2:** siehe `docs/IMPLEMENTATION_PLAN_TDD_v2_findings.md`.

Dieser Plan ersetzt nicht die Vorgängerdokumente, er macht sie ausführbar:
PRJCT liefert die Iterationsstruktur, Handoff liefert Schema und ADRs.
Dieser Plan fügt das Fehlende hinzu: konkrete Testdateien, Review-Gates,
CI-Anforderungen, Rollback-Pfade, Cross-Cutting-Reihenfolge.

---

## 0. Prämissen & Constraints

- Backend bleibt FastAPI (Python 3.12+).
- Frontend bleibt React 19 + Vite + TS.
- MCP-Server bleibt eigenständige Distribution.
- Kein vollständiger Rewrite. Selektive Integration.
- Jede Iteration endet mit gemergtem PR auf `main`, grünem CI, abgehaktem Review.
- Jede Iteration ist in sich deploybar **hinter Feature-Flag (Default OFF)**; Cutover-Phasen sind als eigene Sub-Iterationen (`Xa` Code, `Xb` Cutover) markiert.
- Keine direkten Agent-Writes in GBrain/Kanban (ADR-003 aus Handoff).
- **Sprint-Länge: 2 Kalenderwochen, 1 Engineer ≈ 60 % Fokuszeit.** Estimates sind Worst-Case-Median; Multi-Engineer-Parallelarbeit reduziert Wallclock proportional zur Iter-internen Parallelisierbarkeit.

---

## 1. Open Decisions — vor Iter 0 zu entscheiden

Diese Entscheidungen blockieren TDD-Disziplin. Ohne sie sind Tests nicht
schreibbar oder werden später invasiv umgeschrieben. Jede Entscheidung
bekommt eine eigenständige ADR-Datei (`docs/adr/ADR-XXX-<slug>.md`) mit
Template Kontext → Optionen → Entscheidung → Konsequenzen → **Alternatives
Rejected mit Grund**.

| #   | Entscheidung                  | Optionen                                                              | Empfehlung                                                                                   | Owner   | Blockiert      |
| --- | ----------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- | ------- | -------------- |
| D1  | Persistenzlayer               | raw SQL · SQLAlchemy Core · SQLModel · Tortoise                       | **SQLAlchemy 2.0 + Alembic** (reif, async, FastAPI-konform)                                  | Tech-Lead | Iter 2         |
| D2  | Worker-Queue                  | asyncio Task · arq · Celery · RQ · Dramatiq                           | **arq + Redis** (async-native, leicht, Railway-tauglich)                                     | Tech-Lead | Iter 6 / 7 / 8 |
| D3  | Realtime-Mechanismus          | WebSocket · SSE · Postgres LISTEN/NOTIFY                              | **WebSocket; Postgres als Event-Source; Redis Streams für Fan-Out; Pub/Sub nur als Wake-Signal** | Tech-Lead | Iter 9         |
| D4  | Auth-Modell                   | Token · OAuth · Slack Identity · Magic Link · Clerk/Auth.js           | **Iter 4a JWT + seeded Test-User; Iter 4b Magic-Link + Email-Provider; OAuth später**       | Product+Tech | Iter 4 |
| D5  | Embedding-Provider            | Ollama · OpenAI · Voyage · sentence-transformers offline              | **sentence-transformers `all-MiniLM-L6-v2` offline für Tests *und* Default Prod**; Ollama nur lokal Dev, OpenAI optional | Tech-Lead | Iter 7         |
| D6  | LLM-Provider für Agenten      | Ollama · OpenAI · Anthropic · keine                                   | **Anthropic + Provider-Interface; alle LLM-Calls in Tests via VCR-Recording**               | Tech-Lead | Iter 3         |
| D7  | Deploy-Host (Primär)          | Railway · Fly · Render · VPS · Vercel+Railway Hybrid                  | **Railway-zentriert** (siehe Handoff §6)                                                     | Product | Iter 10        |
| D8  | Obsidian-Vault-Betriebsmodell | lokales Volume · Git-Sync · WebDAV · Cloud-Sync                       | **Git-Sync mit Singleton-Vault-Writer-Worker** (auditierbar, mergebar, konfliktfrei)         | Product | Iter 6         |
| D9  | Test-Stil                     | London · Chicago · Hybrid                                              | **Hybrid**: London an Service-Boundaries, Chicago an Domänenkern                              | Tech-Lead | jede Iter      |
| D10 | Idempotency-Key               | Client-UUID · Server-Hash · Hybrid                                    | **Client-UUID, UNIQUE-Index mit 24h-TTL, Cleanup-Job**                                       | Tech-Lead | Iter 2         |
| D11 | Tenancy-Modell                | Row-per-Tenant (RLS) · Schema-per-Tenant · DB-per-Tenant              | **Row-per-Tenant + Postgres Row-Level-Security**; jede Tabelle `workspace_id NOT NULL`       | Tech-Lead | Iter 2         |
| D12 | Distributed Lock              | FileLock · Postgres Advisory Lock · Redis Lock                        | **Postgres Advisory Lock für DB-State, Redis Lock (`SET NX EX`) für externe File-Sync**     | Tech-Lead | Iter 5         |

**Vor Iter 0 abhaken.** ADRs aus Handoff um ADR-004…ADR-015 ergänzen
(1 ADR pro Decision, plus ADR-013 Idempotency-TTL, ADR-014 Tenancy/RLS,
ADR-015 LLM-Recording).

---

## 2. Preflight — Test- und Review-Infrastruktur

Vor Iter 0. Eigener PR, keine Produktlogik.

### 2.1 Backend

- `backend/pyproject.toml` Dev-Dependencies:
  - `pytest>=8`, `pytest-asyncio>=0.23`, `pytest-cov>=5`,
    `httpx>=0.27`, `respx>=0.21`, `freezegun>=1.5`,
    `schemathesis>=3.36`, `pytest-randomly>=3.15`,
    `pytest-xdist>=3.6`, `vcrpy>=6` (LLM-Recording),
    `diff-cover>=9` (Diff-Coverage-Gate), `mutmut>=2.5`.
- `backend/pytest.ini`: `asyncio_mode = auto`. **Kein globales `--cov-fail-under`** — Coverage-Gate läuft als CI-Job mit `diff-cover` über `coverage.xml`.
- Coverage-Gate (Diff-basiert):
  - Iter 1–3: ≥ 80 % auf geänderten Zeilen.
  - Iter 4–6: ≥ 85 % auf geänderten Zeilen.
  - Iter 7–10: ≥ 90 % auf geänderten Zeilen.
  - Pfad-Gates absolut: `src/core`, `src/services/events`, `src/services/proposals`, `src/services/kanban_sync`, `src/services/auth`, `src/services/gbrain_bridge` ≥ 85 % ab erster Berührung.
- Mutation-Testing-Pfade: `src/services/events`, `src/services/proposals`, `src/services/kanban_sync`, `src/services/auth`, `src/services/gbrain_bridge`. Mutmut nur auf geänderten Dateien (`mutmut run --paths-to-mutate=$CHANGED`).
- Test-Naming: **eine Datei pro Modul**, Funktionsname `test_<scenario>__<expected>`. Beispiel: `tests/unit/test_event_writer.py::test_append__assigns_revision`.
- Struktur:
  ```
  backend/tests/
    conftest.py
    fixtures/
      ideas.json
      kanban_seed.json
      slack_events/*.json
      embeddings/MODEL_HASH         # pinned sentence-transformers weights hash
      cassettes/llm/*.yaml          # VCR recordings (Iter 3+)
    _helpers/
      race.py                       # run_race(N, op) für Concurrency-Tests
      rls.py                        # Tenant-Test-Helfer
    unit/
    integration/
    contract/
    e2e/                            # Marker @slow
  ```

### 2.2 Frontend

- `frontend/package.json` Dev-Dependencies: `vitest`, `@testing-library/react`, `@playwright/test`, `msw`.
- `frontend/vitest.config.ts`: Diff-Coverage ≥ 70 % ab Iter 1.
- Struktur identisch (unit/integration/e2e).

### 2.3 MCP

- Tests bleiben, ergänzt durch Contract-Test gegen `docs/api/openapi.yaml` (Iter 1).
- Vendoring statt Code-Gen: `mcp/ideen-channel/ideen_channel/_openapi.json` als Snapshot, CI prüft Drift zwischen Backend-Export und MCP-Snapshot. Spätere Iter darf zu Code-Gen wechseln, sobald Vertrag stabil.

### 2.4 CI (`.github/workflows/`)

**`ci-fast.yml` — Pflicht auf jedem PR, Budget < 5 min:**

1. `lint` — ruff + black --check + mypy strict für `src/core` und `src/services`; eslint + `tsc --noEmit`.
2. `unit` — backend + frontend unit, parallel.
3. `integration-fast` — Postgres-Service via Docker, FastAPI TestClient, Migrations laufen pre-test. Marker `not slow`.
4. `contract-snapshot` — OpenAPI-Diff gegen `docs/api/openapi.yaml`. Diff verlangt Re-Approval per Label `api-change-approved`.
5. `diff-coverage` — `diff-cover coverage.xml --compare-branch=origin/main --fail-under=$THRESH`.

**`ci-deep.yml` — Nightly + Release-PR (Label `release`), Budget < 25 min:**

6. `schemathesis` — Property-Tests gegen TestClient. Bekannte Findings whitelisted in `tests/contract/schemathesis_ignore.yaml`; neue Findings = Fail.
7. `mutation` — Mutmut auf geänderten Pfaden (kritischer Pfad). Score-Gate ≥ 75 % auf geänderten Zeilen, ab Iter 4.
8. `e2e` — Playwright headless, voller Stack via `docker-compose.e2e.yml`.
9. `migration-check` — `alembic upgrade head && alembic downgrade -1 && alembic upgrade head` auf Snapshot-DB.
10. `smoke-deploy` — gegen Preview-Deployment (Railway PR-Environment).

Branch-Protection auf `main`: alle `ci-fast`-Jobs grün; `ci-deep` Pflicht bei Label `release`.

### 2.5 Review-Gate

- Jede Iter = 1 PR oder PR-Stack (≤ 5) unter einem Tracking-Issue.
- Pflichtreviewer:
  - 1× menschlich.
  - 1× `/code-review-excellence` Subagent-Pass.
  - 1× `/code-review-checklist` Bot-Pass.
- PR-Template gemäß `docs/PR-quality-checklist.md`. Iter-Tabelle (§4) nennt **Sektion** (`Protocol-grade` oder `Routine`), nicht "Track".
- Findings-Disposition-Tabelle (FIXED / SKIPPED+Grund / DEFERRED+Issue) Pflicht ab Iter 2.

### 2.6 DB-Pool & Test-Parallelität

- Test-Postgres-Pool: `POSTGRES_MAX_CONNECTIONS=60`, `docker-compose.test.yml` setzt `-c max_connections=120`.
- Test-Suite begrenzt parallele Sessions auf 50 via `asyncio.Semaphore` (in `conftest.py`).
- `pytest -n auto` für CPU-parallele Tests; DB-bindende Tests Marker `serial` (laufen sequentiell).

### 2.7 Backup-Spec (ab Iter 2 aktiv)

- Postgres Nightly-Dump nach Railway-Volume `/var/backups/`, 14-Tage-Retention.
- WAL-Archivierung ab Iter 4 (sobald PII via Auth-Tabellen reinkommt).
- Restore-Drill: erstmals Iter 2b, danach quartalsweise, dokumentiert in `docs/RUNBOOK-backup.md`.
- RPO-Ziel: ≤ 24 h ab Iter 2, ≤ 1 h ab Iter 10.

---

## 3. Iteration-Schema (verbindlich pro Iter)

```
RED
  - Konkrete Testdatei(en) anlegen, Tests schreiben, alle FAIL.
  - Tests = Specs, keine Smoketests.
  - Datei pro Modul, Funktionsname test_<scenario>__<expected>.
  - PR „WIP: Iter X red phase" — kein Merge.
GREEN
  - Minimaler Code, Tests grün.
  - Keine Refactors, kein Polish.
  - PR-Update, ci-fast grün.
REFACTOR
  - Naming, Duplikate, Abstraktionen.
  - Tests bleiben grün.
  - Diff-Coverage-Schwelle gehalten.
REVIEW
  - PR-Sektion laut Iter-Tabelle.
  - Disposition-Table aktualisiert.
  - Reviewer-Findings adressiert.
ACCEPTANCE
  - Iter-spezifische Acceptance-Tests.
  - Manuelle UX-Probe bei UI-Iter.
  - Rollback-Pfad dokumentiert + verifiziert.
MERGE
  - Squash auf main.
  - Feature-Flag default OFF wenn nicht produktreif.
  - Iter-Outcome in CHANGELOG.md.
CUTOVER (falls Iter ein "b"-Suffix hat)
  - Flag ON in Staging, Beobachtungsfenster mit Metriken.
  - Cutover-Acceptance-Liste (siehe Iter 2b, 4b).
```

---

## 4. Iterationen

### Iter 0 — Baseline Freeze · 1 Sprint

**Sektion:** Routine. **CI-Gate:** ci-fast.

**Red — Testdateien:**

- `backend/tests/integration/test_status_api.py::test_health__returns_ok`
- `backend/tests/integration/test_ideas_api.py::test_list__returns_deterministic_shape`
- `backend/tests/integration/test_kanban_api.py::test_board__returns_seed`
- `backend/tests/integration/test_semantic_api.py::test_connections__returns_structure`
- `backend/tests/integration/test_agents_api.py::test_enrichment__includes_slug` (Fix für bekannten Fail aus Handoff §3)
- `mcp/ideen-channel/tests/test_client.py::test_base_url__from_env_only` (nur ENV-Lesetest; Vertragstest in Iter 1)

**Fixtures:** `tests/fixtures/ideas.json`, `tests/fixtures/kanban_seed.json` aus jetzigem `src/kanban_data.json` extrahiert.

**Green:** Endpoints konsolidieren, `slug`-Fix in `agents_api`, MCP-Client liest `IDEEN_CHANNEL_API_URL` (fail-fast wenn fehlt).

**Refactor:** Test-Fixtures + conftest konsolidieren.

**Acceptance:**

- `pytest -m "not slow"` grün auf frischer Checkout-Maschine.
- `scripts/smoke.sh` ruft `/health`, `/api/ideas`, `/api/kanban`, `/api/semantic/connections` gegen lokalen Stack.
- Coverage-Baseline-Report in PR-Beschreibung.

**Rollback:** Reine Test-Adds, keine Schema-Änderungen → Revert trivial.

---

### Iter 1 — Config & Contract Stabilisierung · 1 Sprint

**Sektion:** Protocol-grade (Wire-Contract). **CI-Gate:** ci-fast + contract-snapshot.

**Red:**

- `backend/tests/unit/test_settings.py::test_missing_required_env__raises`
- `backend/tests/integration/test_cors.py::test_only_allowed_origins__pass`
- `backend/tests/contract/test_openapi_export.py::test_snapshot_stable`
- `frontend/tests/unit/api_base_url.test.ts::test_from_env__required` *(verschoben aus Iter 0)*
- `frontend/tests/unit/api_base_url.test.ts::test_no_hardcoded_localhost_in_src` *(verschoben aus Iter 0)*
- `mcp/ideen-channel/tests/test_contract.py::test_client_calls_match_backend_openapi`

**Green:**

- `pydantic-settings`: required ohne Default → `DATABASE_URL`, `ALLOWED_ORIGINS`, `JWT_SECRET` (vorbereitet, in Iter 4 aktiv).
- CORS aus `ALLOWED_ORIGINS` (CSV); keine `*` + Credentials.
- `scripts/export_openapi.py` → `docs/api/openapi.yaml`; ci-fast prüft Diff.
- Frontend-Codemod: alle `http://localhost:PORT` → `import.meta.env.VITE_API_URL` / `VITE_WS_URL`.
- MCP-Client vendored `_openapi.json`, Drift-Check in CI.

**Acceptance:**

- `grep -rn 'localhost' frontend/src` → 0 Hits.
- Schemathesis-Lauf gegen TestClient: alle Findings entweder gefixt oder explizit in `schemathesis_ignore.yaml` mit Grund.
- Deploy gegen 3 verschiedene `API_BASE_URL`-Werte ohne Codeänderung.

**Rollback:** Nur Code/Config, kein Schema → Revert via Git.

**Bekannter Diff zum Handoff:** Handoff T3 (MCP-Vertrag) wird hier *strukturell* erfüllt; einzelne fehlende Endpoints werden in Iter 3 (Proposals) und Iter 5 (Kanban) ergänzt.

---

### Iter 2a — Event Store Code (hinter Flag) · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + migration-check; ci-deep mutation-Gate Pflicht ab dieser Iter für `src/services/events`.

**Red:**

- `backend/tests/unit/test_event_writer.py::test_append__assigns_revision`
- `backend/tests/unit/test_event_writer.py::test_same_idempotency_key_within_ttl__no_duplicate`
- `backend/tests/unit/test_event_writer.py::test_same_idempotency_key_after_ttl__accepted_as_new`
- `backend/tests/unit/test_event.py::test_payload_hash__deterministic`
- `backend/tests/unit/test_event.py::test_payload_hash__canonical_json`
- `backend/tests/integration/test_projections.py::test_idea_view__rebuild_from_events__matches_state`
- `backend/tests/integration/test_projections.py::test_kanban_view__rebuild_from_events__matches_state`
- `backend/tests/integration/test_projections.py::test_rebuild_after_schema_v2__catchup_correct`
- `backend/tests/integration/test_alembic.py::test_upgrade_then_downgrade__idempotent`
- `backend/tests/integration/test_rls.py::test_cross_workspace_query__returns_empty` *(via _helpers/rls)*

**Schema (Alembic `0002_event_store.py`):**

```sql
CREATE TABLE events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  actor_id UUID NULL,
  entity_type TEXT NOT NULL,
  entity_id UUID NOT NULL,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  payload_hash TEXT NOT NULL,
  idempotency_key UUID NULL,
  revision BIGSERIAL NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX events_entity_idx ON events (workspace_id, entity_id, revision);
CREATE UNIQUE INDEX events_idem_idx
  ON events (workspace_id, idempotency_key)
  WHERE idempotency_key IS NOT NULL;

CREATE TABLE projection_state (
  name TEXT PRIMARY KEY,
  last_event_id UUID NOT NULL,
  schema_version INT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RLS Pflicht ab dieser Migration
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
CREATE POLICY events_tenant_isolation ON events
  USING (workspace_id = current_setting('app.current_workspace_id')::uuid);
```

**Green:**

- `src/services/events/store.py` — `append(event, idempotency_key)` in einer Transaktion mit UNIQUE-Lookup.
- Canonical-JSON via `orjson` mit sortierten Keys; Hash = `sha256(canonical_json)`.
- `src/services/events/projections/` — `ideas_view`, `tasks_view`, `proposals_view`, `semantic_edges_view`.
- Projection-Rebuild = `TRUNCATE + replay FROM event_id=0`, Schreibsperre via Postgres Advisory Lock auf `('projection_rebuild', name_hash)`.
- Idempotency-Cleanup-Job (arq, einmal pro Stunde): `UPDATE events SET idempotency_key=NULL WHERE created_at < now() - interval '24 hours'`.
- API `/api/ideas/*`, `/api/kanban/*` lesen aus Views **wenn Flag `USE_EVENT_STORE=on`, sonst Legacy-JSON**. Flag default OFF.

**Acceptance Iter 2a:**

- Idee + Task per API erzeugt, Postgres-Dump zeigt Events.
- `pg_dump events` + Replay liefert identischen View-Zustand.
- `GET /api/audit?entity_id=...` liefert Historie.
- Legacy-JSON-Pfad unverändert grün bei Flag OFF.
- Mutation-Score ≥ 75 % auf `src/services/events`.
- Nightly-Backup-Job läuft, Restore-Test in Staging dokumentiert (siehe §2.7).

**Rollback:** Flag OFF; Migration `alembic downgrade -1` getestet in CI.

---

### Iter 2b — Event Store Cutover · ½ Sprint

**Sektion:** Routine (Cutover-Gate). **CI-Gate:** ci-fast + smoke-deploy.

**Pre-Cutover (Shadow-Phase, 7 Tage Staging):**

- Flag `USE_EVENT_STORE=shadow` → Reads gehen aus Legacy-JSON, **parallel** aus Views; Differenzen werden in `shadow_diff_log` geschrieben.
- Acceptance: 0 Differenzen über 7 Tage; Alarm in Slack bei jedem Diff.

**Cutover:**

- Flag auf `on`. Legacy-JSON read-only. Backup `backups/kanban_data_$(date).json`.
- Legacy-Read entfernt erst in Iter 5 (sobald Kanban-Sync stabil).

**Cutover-Acceptance:**

- `SELECT count(*) FROM shadow_diff_log WHERE created_at > now() - interval '7 days'` = 0.
- Restore-Drill aus Iter-2a-Backup erfolgreich.

**Rollback:** Flag zurück auf `off`, Reads laufen aus JSON; Events bleiben in DB (verlustfrei).

---

### Iter 3 — Agent Proposal Pipeline · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + contract.

**Red:**

- `backend/tests/unit/test_proposal.py::test_accept__emits_target_event`
- `backend/tests/unit/test_proposal.py::test_reject__leaves_target_unchanged`
- `backend/tests/unit/test_proposal.py::test_edit__stores_human_diff`
- `backend/tests/unit/test_proposal.py::test_schema__strict_unknown_rejected`
- `backend/tests/unit/test_proposal.py::test_expired__cannot_be_accepted`
- `backend/tests/integration/test_agents_enrichment.py::test_produces_proposal_not_mutation`
- `backend/tests/integration/test_agents_enrichment.py::test_llm_call__uses_vcr_cassette` *(deterministisch via VCR)*

**Schema:**

```sql
CREATE TYPE proposal_status AS ENUM ('pending','accepted','rejected','edited','expired');

CREATE TABLE proposals (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  target_entity_type TEXT NOT NULL,
  target_entity_id UUID NULL,           -- NULL = Proposal für neues Objekt
  proposed_change JSONB NOT NULL,
  rationale TEXT NOT NULL,
  sources JSONB NOT NULL DEFAULT '[]'::jsonb,
  confidence NUMERIC(4,3) NOT NULL CHECK (confidence BETWEEN 0 AND 1),
  risk TEXT NOT NULL,
  status proposal_status NOT NULL DEFAULT 'pending',
  expires_at TIMESTAMPTZ NOT NULL DEFAULT (now() + interval '30 days'),
  created_by UUID NULL,                 -- 'agent:<id>' oder user UUID
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  decided_by UUID NULL,
  decided_at TIMESTAMPTZ NULL
);
```

**Green:**

- `POST/GET/PATCH /api/proposals`, `POST /api/proposals/{id}/{accept|reject}`.
- Agent-Endpoints (`/api/agents/*`) intern auf Proposal-Erzeugung umgestellt.
- `/tmp/agent_enrichment_*.json` Codepfade entfernt.
- LLM-Aufrufe via Provider-Interface (ADR-009/D6); Tests nutzen VCR-Cassettes.
- Cleanup-Job (arq, täglich): `UPDATE proposals SET status='expired' WHERE expires_at < now() AND status='pending'`.

**Acceptance:**

- Agent-Run erzeugt Proposal mit Evidence + Confidence.
- Accept → Event in `events`, View aktualisiert.
- Keine direkte Mutation durch Agenten in Test-Run.

**Rollback:** Feature-Flag `AGENT_PROPOSALS_ONLY=true`; alte Pfade bleiben deaktiviert im Code für 1 Iter, dann gelöscht.

---

### Iter 4a — Auth-Foundation (JWT + Test-User-Seed) · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + ci-deep mutation Pflicht für `src/services/auth`.

**Red:**

- `backend/tests/unit/test_jwt.py::test_expired_token__rejected`
- `backend/tests/unit/test_jwt.py::test_wrong_signature__rejected`
- `backend/tests/integration/test_auth_dep.py::test_unauth_request__401`
- `backend/tests/integration/test_workspace_middleware.py::test_no_membership__403`
- `backend/tests/integration/test_audit.py::test_event_carries_actor_id`
- `backend/tests/integration/test_rls.py::test_workspace_scope_enforced_at_db_level`

**Schema:**

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TYPE workspace_role AS ENUM ('owner','editor','viewer');

CREATE TABLE memberships (
  workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role workspace_role NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  expires_at TIMESTAMPTZ NOT NULL,
  revoked_at TIMESTAMPTZ NULL
);
```

**Green:**

- JWT-Signierung (HS256 für MVP, Key in `JWT_SECRET`).
- FastAPI-Dependencies `current_user`, `current_workspace`.
- Events bekommen `actor_id` (NULL nur für System-/Migration-Aktoren).
- POST `/api/workspaces`, POST `/api/workspaces/{id}/invites`, Rollen `owner|editor|viewer`.
- `scripts/seed_test_user.py` für Dev/Staging: erzeugt deterministische Test-User + Workspace + JWT.
- Existierende Iter-0–3-Tests bekommen Fixture `authenticated_client`; Migration aller Tests im selben PR (Aufwand-Estimate: ~30 Test-Dateien × 5 min = 2.5 h).
- RLS-Policies aus Iter 2 nutzen `app.current_workspace_id`, gesetzt per Middleware aus JWT-Claim.

**Acceptance:**

- Unauth-Request → 401.
- Cross-Workspace-Read → 403 (App-Layer) + Leerergebnis (DB-Layer via RLS).
- Audit-Eintrag enthält Nutzer-ID.
- Mutation-Score ≥ 75 % auf `src/services/auth`.

**Rollback:** Feature-Flag `AUTH_ENFORCED=false` für 1 Deploy-Zyklus zum Smoke-Testen, dann ON.

---

### Iter 4b — Magic-Link & Email-Provider · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + security-test.

**Red:**

- `backend/tests/integration/test_magic_link.py::test_valid__creates_session`
- `backend/tests/integration/test_magic_link.py::test_replay_attack__rejected`
- `backend/tests/integration/test_magic_link.py::test_rate_limit__per_email`
- `backend/tests/integration/test_email_provider.py::test_send__uses_mock_in_test`

**Green:**

- Provider-Interface `EmailProvider` (Postmark / Resend / SES — Wahl in ADR).
- DNS-Setup (SPF/DKIM/DMARC) als Runbook-Eintrag.
- Bounce-Handling via Webhook.
- Rate-Limit per Email (5 Magic-Links / 15 min).
- Token-Replay-Schutz: Single-Use, kurze TTL (15 min).

**Acceptance:**

- E2E-Lauf: Email-Request → Mock-Provider liefert Token → Login → Session aktiv.
- Manuelle Lieferung an Test-Inbox in Staging dokumentiert.

**Rollback:** Magic-Link-Endpoints feature-flagged; JWT + Seed-Endpoint aus 4a bleiben funktional.

---

### Iter 5 — Kanban-Governance & Sync · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + ci-deep concurrency-stress (`@stress`-Marker, nightly Pflicht).

**Red:**

- `backend/tests/unit/test_task_move.py::test_emits_task_moved_event`
- `backend/tests/integration/test_concurrent_move.py::test_cas_conflict__second_rejected` (`run_race(N=50)` mit `Semaphore(20)`)
- `backend/tests/integration/test_concurrent_move.py::test_advisory_lock__serialises_writers`
- `backend/tests/integration/test_kanban_sync.py::test_obsidian_md_roundtrip__preserves_user_frontmatter` (ruamel.yaml round-trip)
- `backend/tests/integration/test_kanban_sync.py::test_redis_lock__cross_worker_serialisation` (mehrere arq-Worker-Pids)

**Green:**

- `kanban-sync` Boundary-Service.
- Optimistic Concurrency: `tasks.revision`, CAS via `UPDATE … WHERE revision = :rev`.
- Distributed Lock: Postgres Advisory Lock (`pg_try_advisory_xact_lock`) für DB-State; Redis-Lock (`SET NX EX 30`) für Vault-Datei-Sync.
- Markdown-Round-Trip via `ruamel.yaml` (preserve order, comments, quoting).

**Acceptance:**

- 50 parallele Moves: genau 1 wins, 49 erhalten 409 Conflict.
- Obsidian-MD: User-`tags:` byte-identisch nach Round-Trip.
- Zweite Worker-Instanz wartet auf Lock, kein Datenverlust.
- Legacy-`kanban_data.json` Read-Pfad entfernt.

**Rollback:** Shadow-Phase aus Iter 2b weiterhin abrufbar; bei Issue rollback via Flag.

---

### Iter 6 — GBrain Bridge · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast.

**Red:**

- `backend/tests/unit/test_gbrain_bridge.py::test_write_to_kanban_subtree__rejected`
- `backend/tests/unit/test_gbrain_bridge.py::test_write_without_accepted_proposal_or_human_actor__rejected`
- `backend/tests/integration/test_gbrain_bridge.py::test_bidirectional_links__validated`
- `backend/tests/contract/test_gbrain_bridge.py::test_invalid_frontmatter__400`
- `backend/tests/integration/test_gbrain_bridge.py::test_singleton_writer__serialises_concurrent_writes`

**Green:**

- Singleton-Vault-Writer als dedizierter arq-Worker (Queue `vault_writes`, Concurrency=1).
- Git-Sync nach jedem Write (commit + push); Conflict-Resolution = "letzter gewinnt, Audit-Log-Eintrag".
- Schema für Ideen-, Chat-, Task-, Semantic-Edge-Pages.

**Test-Fixture-Pattern:** `vault_per_test` Fixture (tempdir + `git init` pro Test, Cleanup im teardown). Tests parallel-sicher.

**Acceptance:**

- Schreibtests grün gegen Test-Vault.
- Git-Diff nach jedem Write deterministisch (commit-Message-Template).
- Read-Tests laufen auch bei `GBRAIN_WRITE_ENABLED=false`.

**Flag-Spec:**

- Code-Flag: `GBRAIN_WRITE_ENABLED` (Default `false` in Prod, `true` in Staging/Tests).
- Test-Override: `pytest`-Fixture setzt Flag explizit auf `true` für Schreibtests.

**Rollback:** Flag `false` → Read-only.

---

### Iter 7 — Semantische Analyse · 2 Sprints

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + ci-deep determinism-suite.

**Determinismus-Spec:**

- sentence-transformers `all-MiniLM-L6-v2`, Version pinned in `requirements.txt` (`==2.7.0`).
- Modellgewichte als Git-LFS-Artefakt unter `tests/fixtures/embeddings/`; CI cached via Actions-Cache.
- CI-Plattform pinned: `ubuntu-22.04 x86_64`, BLAS-Lib `openblas`.
- Test-Assertion: Vektor-Vergleich mit Toleranz `np.allclose(v1, v2, atol=1e-4)`; Edge-Set-Vergleich nach Threshold-Round.
- Hardware-Drift dokumentiert: Apple-Silicon-Devs sehen abweichende 4.+ Dezimale; akzeptiert, weil CI-Linux-x86 die kanonische Quelle ist.

**Red:**

- `backend/tests/unit/test_semantic.py::test_similar_ideas__edge_proposed`
- `backend/tests/unit/test_semantic.py::test_duplicates__detected`
- `backend/tests/unit/test_semantic.py::test_contradicts__manual_flag_only`
- `backend/tests/integration/test_graph.py::test_hubs__deterministic_on_canonical_ci`
- `backend/tests/integration/test_graph.py::test_orphans__deterministic_on_canonical_ci`
- `backend/tests/integration/test_event_bridge.py::test_pg_notify__enqueues_arq_job`

**Schema:**

```sql
CREATE TYPE relation_type AS ENUM (
  'supports','extends','duplicates','depends_on',
  'contradicts','same_cluster','question_for'
);

CREATE TABLE semantic_edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL,
  source_id UUID NOT NULL,
  target_id UUID NOT NULL,
  relation_type relation_type NOT NULL,
  weight NUMERIC(4,3) NOT NULL,
  evidence JSONB NOT NULL,
  method TEXT NOT NULL,
  confidence NUMERIC(4,3) NOT NULL,
  accepted BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (source_id <> target_id)
);
```

**Green:**

- Event-Bridge-Worker: Postgres `LISTEN events_channel` → `arq.enqueue('semantic.recompute', event_id)`.
- arq-Worker `semantic.recompute` lädt Idee, embedded, baut Edge-Kandidaten, schreibt mit `accepted=false`.
- Graph-API liefert aus `semantic_edges_view`; UI trennt accepted vs proposed.

**Acceptance:**

- 2× Lauf auf gleicher Input-Menge auf CI-Plattform: identisches Edge-Set unter Toleranz.
- UI-Smoke: Cluster, Hubs, Orphans sichtbar.

**Rollback:** `SEMANTIC_AUTO_PROPOSE=false` lässt Modul installiert, inaktiv.

---

### Iter 8 — Slack Integration · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + ci-deep signature-fuzz.

**Red:**

- `backend/tests/unit/test_slack_sig.py::test_valid__accepted`
- `backend/tests/unit/test_slack_sig.py::test_invalid__rejected`
- `backend/tests/unit/test_slack_sig.py::test_timestamp_outside_5min__rejected` (Replay-Schutz)
- `backend/tests/unit/test_slack_sig.py::test_fuzz_signature__never_accepts_random` (`@pytest.mark.fuzz`, hypothesis)
- `backend/tests/unit/test_slack.py::test_duplicate_event_id__deduped`
- `backend/tests/integration/test_slack.py::test_slash_idea__creates_chat_message_event`
- `backend/tests/integration/test_slack.py::test_handler_enqueues_before_returning_200` *(Design-Test: durable handoff before ack)*

**Schema-Add:** `chat_messages` aus Handoff §7; `slack_event_dedup(event_id PK, seen_at)` für Idempotenz.

**Green:**

- `slack-ingest` Service mit Signature-Verify und 3s-Ack-Pattern: Event zuerst dedupe+persist/enqueue (durable handoff), danach `return JSONResponse(200)`.
- arq-Job verarbeitet, schreibt `chat.message.received`-Event.
- Slack-Thread-TS → Idea-ID-Mapping in `chat_messages.linked_entity_id`.
- OAuth-Install-Flow als separater Endpoint `/api/slack/oauth/callback`.

**Acceptance:**

- Manueller E2E-Lauf mit Slack-Test-Workspace.
- Mapping persistiert, Replay-Test grün.
- Signature-Fuzz: 0 False-Positives über 10k random inputs.

**Rollback:** Slack-App-Tokens revozierbar; Mapping-Tabelle bleibt für Replay.

---

### Iter 9 — Realtime Collaboration · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + ci-deep e2e Pflicht.

**Red:**

- `backend/tests/integration/test_ws.py::test_connect__sends_snapshot`
- `backend/tests/integration/test_ws.py::test_after_event__broadcasts_to_subscribers`
- `backend/tests/integration/test_ws.py::test_stale_revision__conflict_response`
- `backend/tests/integration/test_ws.py::test_reconnect_with_last_event_id__replays_missed`
- `backend/tests/integration/test_ws.py::test_after_redis_restart__replay_from_postgres`
- `frontend/tests/unit/event_reducer.test.ts::test_task_moved__updates_board`
- `frontend/tests/e2e/two_browsers.spec.ts::test_two_browsers_see_change_under_1s`

**Architektur (ADR-006 final):**

- WebSocket-Transport (`/ws/workspaces/{id}`).
- Postgres `events`-Tabelle = Source-of-Truth für Replay.
- Redis Streams (`XADD`/`XREADGROUP`) für Fan-Out an Worker-Replikas.
- Redis Pub/Sub nur als Wake-Signal an WebSocket-Server, der dann aus Postgres nachlädt.
- Client schickt `Last-Event-ID`-Header beim Reconnect; Server replayed aus Postgres.

**Acceptance:**

- 2 Browser-Kontexte sehen Board-Change < 1 s ohne Reload.
- Reconnect nach 30 s Disconnect → alle Events nachgeliefert.
- Redis-Kill in Staging: Reconnect lädt aus Postgres weiter; max. 5 s Verzögerung.

**Polling-Fallback-Sunset:**

- Frontend behält Polling-Pfad in Iter 9 als Fallback.
- Sunset-Kriterium: ≥ 14 Tage WS-Reconnect-Rate < 1 % in Staging-Metriken; Entfernung als Acceptance von Iter 10.

**Rollback:** WS-Endpoint disabled → Frontend nutzt Polling weiter.

---

### Iter 10 — Deployment Hardening & SLO · 1 Sprint

**Sektion:** Protocol-grade. **CI-Gate:** ci-fast + ci-deep komplett Pflicht.

**Red:**

- `backend/tests/e2e/test_healthcheck_all_services.py`
- `backend/tests/integration/test_settings.py::test_missing_env__app_fails_fast`
- `backend/tests/integration/test_db_backup_restore.py::test_data_preserved`
- `backend/tests/integration/test_cors.py::test_foreign_origin__rejected`
- `backend/tests/integration/test_rate_limit.py::test_burst__throttled`
- `backend/tests/e2e/test_load.py::test_p95_under_300ms_at_50rps` (`@load`-Marker; Locust-Run)

**Green:**

- Railway-Profile finalisiert (web + worker getrennt).
- Strukturierte Logs (`structlog`).
- Secrets nur aus Env; Pre-Push-Hook scanned via `trufflehog`.
- Rate-Limit per User+IP (Redis-basiert).
- Runbook `docs/RUNBOOK.md` (Deploy, Restore, Incident, On-Call).
- Polling-Fallback aus Iter 9 entfernt.

**Acceptance:**

- Frische Railway-Umgebung per Runbook in < 30 min hochgezogen.
- SLO erreicht: `/api/*` p95 < 300 ms bei 50 rps; Error-Rate < 1 %.
- Backup-Restore-Drill durchgeführt + dokumentiert (RPO ≤ 1 h).
- Disaster-Recovery-Drill: vollständiger Wiederaufbau aus Backup in < 2 h.

**Rollback:** Blue-green über Railway Environments.

---

## 5. Cross-Cutting Anforderungen (jede Iter)

- **Definition of Done:**
  - PR-Quality-Sektion abgehakt
  - `ci-fast` grün; `ci-deep` grün bei Release-PR
  - Diff-Coverage-Schwelle gehalten
  - Reviewer-Findings dispositioniert
  - Acceptance-Tests grün
  - Rollback-Pfad verifiziert
  - CHANGELOG.md aktualisiert
- **Feature-Flags:** Default OFF; Default ON erst nach ≥ 7 Tagen Staging-Stabilität.
- **Migrationen:** Reversibel; `alembic downgrade -1` im CI getestet.
- **Test-Pyramide-Ziel:** ~60 % Unit, ~35 % Integration, ~5 % E2E. (Korrigiert vs v1: I/O-Lastigkeit drückt Unit-Anteil.)
- **Determinismus:** Tests reproduzierbar bei `pytest-randomly --randomly-seed=last`. Anti-Flake-Budget: max. 3 Retries; mehr = Issue + Fix vor Merge.
- **Mutation-Testing:** Ab Iter 2 für `src/services/{events,proposals,kanban_sync,auth,gbrain_bridge}` auf geänderten Pfaden, Score ≥ 75 %.
- **Observability:** Prometheus-Metriken ab Iter 2, Pflicht in Iter-10-Acceptance.
- **LLM-Recording:** Alle LLM-Calls in Tests via VCR-Cassettes (`tests/fixtures/cassettes/llm/`). Cassettes versioniert.
- **Glossar:** siehe Anhang A.

---

## 6. ADR-Stack (vor Iter 0)

| ADR | Slug                       | Decision   |
| --- | -------------------------- | ---------- |
| 001 | postgres-as-source-of-truth | Handoff    |
| 002 | event-sourcing-light       | Handoff    |
| 003 | agent-proposals-not-writes | Handoff    |
| 004 | sqlalchemy-2-alembic       | D1         |
| 005 | arq-redis-worker-queue     | D2         |
| 006 | ws-postgres-source-redis-streams-fanout | D3 (verschärft) |
| 007 | auth-jwt-then-magic-link   | D4         |
| 008 | embeddings-sentence-transformers-pinned | D5     |
| 009 | llm-anthropic-with-vcr     | D6         |
| 010 | deploy-railway-centric     | D7         |
| 011 | obsidian-git-sync-singleton-writer | D8 (verschärft) |
| 012 | tdd-hybrid-style           | D9         |
| 013 | idempotency-client-uuid-24h-ttl | D10 (TTL präzisiert) |
| 014 | tenancy-row-with-rls       | D11        |
| 015 | distributed-lock-postgres-advisory-redis-set-nx | D12 |

ADRs in **eigenständigem Routine-PR** vor Iter 0. Jede ADR mit "Alternatives Rejected" Pflicht.

---

## 7. Akzeptanzkriterien Gesamt

Plan gilt als erfolgreich umgesetzt, wenn:

- Nutzer kann in Slack Idee erfassen → System erzeugt Proposal → Mensch akzeptiert → Idee/Task/Kante entsteht → GBrain wird kontrolliert aktualisiert → zweiter Remote-Nutzer sieht Änderung < 1 s → Audit-Log zeigt Actor/Zeit/Payload.
- `ci-fast` < 5 min auf jedem PR; `ci-deep` < 25 min nightly.
- Mutation-Score ≥ 75 % auf geänderten Zeilen kritischer Pfade.
- Diff-Coverage ≥ 90 % ab Iter 7 auf geänderten Zeilen.
- Frische Umgebung per `docs/RUNBOOK.md` in < 30 min deploybar.
- Disaster-Recovery-Drill durchgeführt + RPO ≤ 1 h dokumentiert.
- 0 hardcodierte Hosts/Ports im Frontend-Build.

---

## 8. Bekannte Risiken & Mitigationen

| #   | Risiko                                        | Auftritt   | Mitigation                                                                     |
| --- | --------------------------------------------- | ---------- | ------------------------------------------------------------------------------ |
| R1  | Embedding-Modell-Drift                        | Iter 7     | Modellgewicht-Hash pinned, CI-Plattform pinned, Toleranz `atol=1e-4`           |
| R2  | Slack Rate Limits                             | Iter 8     | Worker-Backoff + Queue, Dev-Workspace getrennt                                 |
| R3  | Postgres-Lock-Kontention bei Idempotency      | Iter 2+    | UNIQUE-Constraint statt expliziter Lock; Cleanup-Job entfernt alte Keys       |
| R4  | WebSocket-Fan-out-Cost auf Railway            | Iter 9     | Redis Streams horizontal, Pub/Sub nur Wake-Signal                              |
| R5  | Magic-Link-Email-Provider-Ausfall             | Iter 4b    | Provider-Interface, Fallback auf Console-Log in Dev/Staging                    |
| R6  | Mutation-Test-Laufzeit blockiert CI           | Iter 2+    | Mutmut nur auf geänderten Dateien; in `ci-deep`, nicht `ci-fast`               |
| R7  | Iter-2b Shadow-Phase findet stille Datendrift | Iter 2b    | Diff-Logging, Alarm bei > 0 Differenzen, kein Cutover ohne 7 Tage 0-Diff      |
| R8  | DB-Pool-Erschöpfung in Concurrency-Tests      | Iter 5+    | Pool 60, Semaphore 20, Marker `serial` für DB-bindende Tests                   |
| R9  | Mutation-Score 75 % nicht erreichbar          | Iter 4+    | Pilotlauf in Iter 2 misst echten Score; Gate ggf. auf 60 % gesenkt mit ADR     |
| R10 | Schemathesis flood von False-Positives        | Iter 1+    | `schemathesis_ignore.yaml` whitelistet; neue Findings Review-pflichtig         |
| R11 | Git-Sync-Konflikte im Vault                   | Iter 6     | Singleton-Writer-Queue, sequentielle Verarbeitung, Conflict-Audit              |

**Offene Fragen vor jeweiliger Iter:**

- Iter 4b: Welcher Email-Provider in Prod? (Postmark, Resend, SES)
- Iter 6: Welcher Obsidian-Vault? Existierender DYAI-Vault oder Greenfield?
- Iter 8: Slack-Org? Bot-User-Name?
- Iter 9: Realtime-SLO p99? 1 s reicht MVP; Cursor/Presence später < 100 ms.

---

## 9. Nächste Schritte

1. ADR-Stack (ADR-004…015) als 1 Routine-PR (siehe §6).
2. Preflight-PR (§2): Test-Infra, CI-Split, Review-Gates, DB-Pool-Config.
3. Iter 0 starten.

---

## Anhang A — Glossar

- **Event**: Append-only Datensatz in `events`-Tabelle; Source-of-Truth für State.
- **Projection (View)**: Aus Events abgeleiteter Lesezustand (`ideas_view`, `tasks_view` …).
- **Proposal**: Vorschlag (von Agent oder Mensch) zur Änderung; muss akzeptiert werden, bevor Event entsteht.
- **Workspace**: Mandanten-Container; alle Daten haben `workspace_id`.
- **Cutover (Xb-Suffix)**: Sub-Iter, in der Feature-Flag von OFF/Shadow auf ON dreht; eigene Acceptance.
- **Singleton-Worker**: arq-Queue mit Concurrency=1, garantiert Serialisierung (z.B. Vault-Writes).
- **CAS**: Compare-and-Swap via `revision`-Spalte, Basis für optimistische Concurrency.
- **RLS**: Postgres Row-Level-Security, durchgesetzt per Policy + Session-Variable.
- **VCR-Cassette**: Aufgezeichneter HTTP-Verkehr (LLM-Call), in Tests replayed.

---

## Anhang B — Iter-Übersicht

| Iter | Name                    | Sprint | Sektion       | CI-Gate                   |
| ---- | ----------------------- | ------ | ------------- | ------------------------- |
| 0    | Baseline Freeze         | 1      | Routine       | ci-fast                   |
| 1    | Config & Contract       | 1      | Protocol      | ci-fast + contract        |
| 2a   | Event Store Code        | 1      | Protocol      | ci-fast + migration       |
| 2b   | Event Store Cutover     | 0.5    | Routine       | ci-fast + smoke           |
| 3    | Proposal Pipeline       | 1      | Protocol      | ci-fast + contract        |
| 4a   | Auth Foundation         | 1      | Protocol      | ci-fast + mutation        |
| 4b   | Magic-Link              | 1      | Protocol      | ci-fast + security        |
| 5    | Kanban Governance       | 1      | Protocol      | ci-fast + concurrency     |
| 6    | GBrain Bridge           | 1      | Protocol      | ci-fast                   |
| 7    | Semantic Analysis       | 2      | Protocol      | ci-fast + determinism     |
| 8    | Slack Integration       | 1      | Protocol      | ci-fast + signature-fuzz  |
| 9    | Realtime                | 1      | Protocol      | ci-fast + e2e             |
| 10   | Deploy Hardening        | 1      | Protocol      | ci-fast + ci-deep voll    |

Gesamt: 12.5 Sprints × 2 Wochen ≈ 6 Monate für 1 Engineer @ 60 %. Multi-Engineer-Parallelisierung möglich für Iter 4b/5/6/7 (geringe gegenseitige Abhängigkeit).
