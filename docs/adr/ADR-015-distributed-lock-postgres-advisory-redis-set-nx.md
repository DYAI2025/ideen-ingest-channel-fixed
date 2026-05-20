# ADR-015: Distributed Locks — Postgres Advisory + Redis SET NX

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 5 (Kanban Concurrency), Iter 6 (GBrain Singleton)

## Context

Validierungsfund B3: v1 nutzte `filelock` für Concurrency-Schutz. Funktioniert nicht über Railway-Multi-Host (kein gemeinsames Filesystem). Wir brauchen einen Distributed-Lock-Mechanismus, der bei mehreren Web-/Worker-Prozessen korrekt serialisiert.

## Options

1. **Hybrid:** Postgres Advisory Lock für DB-State, Redis `SET NX EX` für externe File-Sync.
2. **Postgres Advisory Lock allein.**
3. **Redis-Lock allein** (`SET NX EX` oder Redlock).
4. **Zookeeper / etcd** für Locks.

## Decision

**Hybrid.**

- **Postgres Advisory Lock (`pg_try_advisory_xact_lock`)** für jede Operation, die innerhalb einer DB-Transaktion läuft — z. B. Projection-Rebuild (Iter 2), Task-Move-Konfliktauflösung (Iter 5). Lock lebt mit der Transaktion, automatische Freigabe bei Commit/Rollback.
- **Redis `SET NX EX 30`** für externe-Resource-Locks — z. B. Vault-Schreiben (Iter 6 Singleton-Writer), Slack-Event-Dedup-Lock. TTL verhindert Deadlocks bei Crash.

## Consequences

- Tests `test_advisory_lock__serialises_writers` und `test_redis_lock__cross_worker_serialisation` Pflicht in Iter 5.
- Zwei Lock-Mechanismen erfordern Engineer-Bewusstsein. Konvention: DB-State → Advisory; alles andere → Redis.
- Kein neuer Ops-Service (Postgres + Redis sind ohnehin da).

## Alternatives Rejected

- **Postgres Advisory Lock allein** — verworfen: Vault-File-Writes laufen außerhalb der DB-Transaktion; Advisory-Lock hat dort keinen sinnvollen Scope.
- **Redis-Lock allein** — verworfen: Redis-Lock hat im Edge-Case (Network-Partition, Redis-Failover) Korrektheits-Risiko (Redlock-Debatte von Martin Kleppmann). Für DB-State ist Advisory-Lock atomarer und billiger.
- **Zookeeper / etcd** — verworfen: zusätzlicher Cluster zu betreiben, für MVP klar overkill.
