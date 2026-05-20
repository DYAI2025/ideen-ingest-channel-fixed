# ADR-006: Realtime via WebSocket — Postgres als Source, Redis Streams als Fan-Out

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 9 (Realtime Collaboration)

## Context

Iter 9 verlangt: mehrere Browser sehen Board-Änderungen < 1 s ohne Reload, Reconnect liefert verpasste Events seit Last-Event-ID. Validierungsfund B5: Redis Pub/Sub allein liefert kein Replay, weil es fire-and-forget ist und nach Redis-Restart Daten weg sind. Wir brauchen einen Mechanismus, der gleichzeitig (a) niedrige Latenz für Live-Updates, (b) garantierten Replay nach Disconnect und (c) horizontale Skalierung über mehrere WebSocket-Server bietet.

## Options

1. **WebSocket + Postgres als Replay-Source + Redis Streams als Fan-Out + Pub/Sub als Wake-Signal**
2. **Server-Sent Events (SSE) + Postgres LISTEN/NOTIFY**
3. **WebSocket + nur Redis Pub/Sub**
4. **WebSocket + nur Postgres LISTEN/NOTIFY**
5. **Hosted Realtime (Supabase Realtime, Ably, Pusher)**

## Decision

**WebSocket-Transport. Postgres `events`-Tabelle ist Single Source of Truth für Replay. Redis Streams (`XADD`/`XREADGROUP`) verteilen Events an WebSocket-Server-Replikas. Redis Pub/Sub wird nur als Wake-Signal genutzt, damit WS-Server bei neuem Event aus Postgres nachlädt.**

Reconnect-Flow: Client sendet `Last-Event-ID`-Header → Server `SELECT … FROM events WHERE revision > :last_id ORDER BY revision` → Streamt nachträglich. Live-Pfad: Postgres-Trigger → `LISTEN events_channel` → Bridge-Worker → Redis Stream → WS-Server consumes → broadcast an Subscribers.

## Consequences

- WS-Endpunkt `/ws/workspaces/{id}` mit `Last-Event-ID`-Header-Konvention.
- Bridge-Worker (siehe ADR-005) übersetzt Postgres-Notifications zu Redis-Streams-Records.
- Replay-Test (`test_after_redis_restart__replay_from_postgres`) Pflicht in Iter 9.
- Höherer Implementierungsaufwand als reine Pub/Sub-Lösung, aber Replay-Korrektheit ist nicht verhandelbar (Iter 9 Acceptance).
- Skalierung: WS-Server stateless; Streams als persistente Queue erlauben mehrere Consumer-Groups.

## Alternatives Rejected

- **SSE + Postgres LISTEN/NOTIFY** — verworfen: SSE ist halbduplex, Client→Server-Signale brauchen separaten HTTP-Pfad; mehr Code. LISTEN/NOTIFY skaliert bei vielen Subscriber-Verbindungen schlechter als Stream-basierte Fan-Out.
- **WebSocket + nur Pub/Sub** — verworfen: Validierungsfund B5; kein Replay nach Disconnect oder Redis-Restart.
- **WebSocket + nur LISTEN/NOTIFY** — verworfen: jede WS-Server-Replika öffnet eigene PG-Verbindung mit LISTEN, das skaliert nicht über ~50 Connections; horizontal teurer als Streams.
- **Hosted Realtime** — verworfen: zusätzlicher Anbieter, Schema-Lock-in (Supabase erwartet eigene Tabellen-Konventionen), Kostenkontrolle schwerer, weniger Auditierbarkeit als unsere Event-Tabelle.
