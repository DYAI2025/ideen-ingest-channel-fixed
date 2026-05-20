# Architecture Decision Records

Decisions binden den Stack. Jede ADR ist eine eigene Datei, nummeriert und unveränderlich nach Annahme; Status-Wechsel (Proposed → Accepted → Superseded) erfolgt durch Edit des Status-Felds und Verlinkung der Nachfolger-ADR.

## Index

| ADR | Slug                                                                                    | Status   | Blockiert       |
| --- | --------------------------------------------------------------------------------------- | -------- | --------------- |
| 001 | (Handoff §7) postgres-as-source-of-truth                                                | Proposed | Iter 2          |
| 002 | (Handoff §7) event-sourcing-light                                                       | Proposed | Iter 2          |
| 003 | (Handoff §7) agent-proposals-not-writes                                                 | Proposed | Iter 3          |
| 004 | [sqlalchemy-2-alembic](./ADR-004-sqlalchemy-2-alembic.md)                               | Proposed | Iter 2          |
| 005 | [arq-redis-worker-queue](./ADR-005-arq-redis-worker-queue.md)                           | Proposed | Iter 6/7/8      |
| 006 | [ws-postgres-source-redis-streams-fanout](./ADR-006-ws-postgres-source-redis-streams-fanout.md) | Proposed | Iter 9          |
| 007 | [auth-jwt-then-magic-link](./ADR-007-auth-jwt-then-magic-link.md)                       | Proposed | Iter 4a/4b      |
| 008 | [embeddings-sentence-transformers-pinned](./ADR-008-embeddings-sentence-transformers-pinned.md) | Proposed | Iter 7          |
| 009 | [llm-anthropic-with-vcr](./ADR-009-llm-anthropic-with-vcr.md)                           | Proposed | Iter 3          |
| 010 | [deploy-railway-centric](./ADR-010-deploy-railway-centric.md)                           | Proposed | Iter 10         |
| 011 | [obsidian-git-sync-singleton-writer](./ADR-011-obsidian-git-sync-singleton-writer.md)   | Proposed | Iter 6          |
| 012 | [tdd-hybrid-style](./ADR-012-tdd-hybrid-style.md)                                       | Proposed | jede Iter       |
| 013 | [idempotency-client-uuid-24h-ttl](./ADR-013-idempotency-client-uuid-24h-ttl.md)         | Proposed | Iter 2          |
| 014 | [tenancy-row-with-rls](./ADR-014-tenancy-row-with-rls.md)                               | Proposed | Iter 2+         |
| 015 | [distributed-lock-postgres-advisory-redis-set-nx](./ADR-015-distributed-lock-postgres-advisory-redis-set-nx.md) | Proposed | Iter 5/6        |

ADR-001 bis ADR-003 sind im Handoff-Dokument (`ideen_architektur_deliverables (1)/ideen_backend_architektur_handoff.md`) dokumentiert; ADR-004 bis ADR-015 in diesem Verzeichnis. Migration der ersten drei in eigene Dateien optional, sobald sie aktiv revidiert werden.

## Template

```markdown
# ADR-NNN: <Titel>

- **Status:** Proposed | Accepted | Superseded by ADR-XXX
- **Date:** YYYY-MM-DD
- **Decision Owner:** <Rolle>
- **Blockiert:** <Iter oder Komponente>

## Context

<Problem, Constraints, Auslöser>

## Options

1. <Option A>
2. <Option B>
...

## Decision

<Was wir tun, konkret>

## Consequences

<Folgen: positiv und negativ>

## Alternatives Rejected

- **<Option B>** — verworfen: <Grund>
- ...
```

`Alternatives Rejected` ist Pflicht und braucht mindestens eine verworfene Option mit Begründung.
