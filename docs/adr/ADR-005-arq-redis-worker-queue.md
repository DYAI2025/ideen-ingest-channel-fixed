# ADR-005: arq + Redis als Worker-Queue

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 6 (GBrain), Iter 7 (Semantic), Iter 8 (Slack)

## Context

Mehrere Iterationen verlangen Hintergrundverarbeitung: Embedding-Recompute, Slack-Event-Verarbeitung, GBrain-Vault-Writes, Idempotency-Cleanup, Proposal-Expiry. FastAPI selbst ist async, aber Request-Handler dürfen nicht blockierende oder lang-laufende Arbeit synchron erledigen (Slack-Ack < 3 s, siehe Iter 8). Wir brauchen eine Queue, die im selben async-Ökosystem lebt und auf Railway lauffähig ist.

## Options

1. **arq + Redis** — async-native Worker-Queue von Samuel Colvin (Pydantic-Autor), schlank.
2. **Celery + Redis/RabbitMQ** — reifster Python-Queue, sync-first, async via `asgiref`/eventlet.
3. **RQ + Redis** — sync, einfach, kein async-Support.
4. **Dramatiq + Redis/RabbitMQ** — sync-first, gute Middleware-Story.
5. **FastAPI BackgroundTasks** — eingebaut, nur In-Process, kein Retry/Persistence.

## Decision

**arq + Redis.**

arq ist nativ asyncio, integriert sich nahtlos in FastAPI/AsyncSession, hat Dead-Letter, Retries, Cron-Jobs und ist klein genug, um auf Railways kleinem Worker-Plan zu laufen. Redis ist auf Railway als Managed-Service verfügbar und wird gleichzeitig in ADR-006 für Realtime-Fan-Out verwendet — eine Abhängigkeit deckt zwei Concerns.

## Consequences

- Neue Runtime-Dependencies: `arq>=0.26`, `redis>=5.0`.
- Eigener Worker-Service in Railway, Code unter `backend/src/workers/`.
- Jobs sind async-Funktionen, gleiche Programmiermodell wie API-Handler.
- Singleton-Worker-Pattern (ADR-011) trivial implementierbar via Queue-Concurrency=1.
- Operational Overhead: zusätzlicher Prozess zu monitoren, Redis-Verfügbarkeit kritisch.

## Alternatives Rejected

- **Celery** — verworfen: sync-Kern; async-Workarounds (`asgiref.sync_to_async`) sind brüchig, Doppelmodellierung der Aufrufkonventionen. Schwergewichtig (eigener Beat-Scheduler, Worker-Pool-Manager).
- **RQ** — verworfen: kein async-Support; Datenbankzugriffe in Workern würden Sync-SQLAlchemy parallel zu async-Stack im API erzwingen.
- **Dramatiq** — verworfen: solide, aber gleiches Sync-Modell-Problem wie Celery/RQ; geringere Verbreitung im FastAPI-Ökosystem.
- **FastAPI BackgroundTasks** — verworfen: keine Persistenz, kein Retry, geht beim Process-Restart verloren — unbrauchbar für Slack-Webhook-Verarbeitung und Embedding-Recompute.
