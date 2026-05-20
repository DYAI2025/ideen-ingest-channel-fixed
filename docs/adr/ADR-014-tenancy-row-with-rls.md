# ADR-014: Tenancy — Row-per-Tenant + Postgres Row-Level-Security

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 2 (Event Store), alle späteren Iter

## Context

Mehrere Workspaces teilen sich denselben Stack. Validierungsfund M10: Tenancy-Modell war in v1 offen. Die Wahl beeinflusst jede Query, jede Migration und die Auth-Integration in Iter 4.

## Options

1. **Row-per-Tenant + RLS:** jede Tabelle `workspace_id NOT NULL`, Postgres-Policies erzwingen Isolation.
2. **Schema-per-Tenant:** ein Postgres-Schema pro Workspace.
3. **DB-per-Tenant:** separate Postgres-Datenbank pro Workspace.
4. **App-Level-Isolation:** Filter in jeder Query, keine DB-Policies.

## Decision

**Row-per-Tenant mit Postgres RLS.**

Jede Tabelle mit Mandanten-Daten hat `workspace_id UUID NOT NULL`. RLS-Policies (siehe Migration `0002_event_store.py` in Plan §4 Iter 2a) erzwingen `workspace_id = current_setting('app.current_workspace_id')::uuid`. Middleware (Iter 4a) setzt die Session-Variable aus dem JWT-Claim.

## Consequences

- Defense in Depth: selbst wenn ein App-Bug den Workspace-Filter vergisst, blockt die DB.
- Tests: `test_rls__cross_workspace_query__returns_empty` Pflicht ab Iter 2.
- Migrationen müssen RLS aktivieren und Policies anlegen.
- Performance: RLS hat geringen Overhead bei korrekt indizierten `workspace_id`-Spalten.
- Operationale Vorsicht: Admin-Tools müssen RLS bewusst umgehen (via `BYPASSRLS`-Rolle).

## Alternatives Rejected

- **Schema-per-Tenant** — verworfen: jede Migration muss N-mal laufen, Connection-Pooling pro Schema ist komplex, Cross-Workspace-Queries (für Admin/Analytics) brauchen Workaround.
- **DB-per-Tenant** — verworfen: erst bei sehr hoher Mandanten-Isolation-Anforderung gerechtfertigt; verteilt Migrationen, Backups, Monitoring auf N Datenbanken — Ops-Last unverhältnismäßig für MVP.
- **App-Level-Isolation** — verworfen: ein vergessener Filter in einer Query = Datenleck. Audit-Code-Reviews können das nicht zuverlässig fangen. RLS ist die robustere Verteidigung.
