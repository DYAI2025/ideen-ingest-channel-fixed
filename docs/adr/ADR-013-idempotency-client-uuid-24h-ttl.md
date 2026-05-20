# ADR-013: Idempotency — Client-UUID + 24h TTL + Cleanup-Job

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 2 (Event Store)

## Context

Iter 2 Event-Store-Writes müssen idempotent sein, damit Client-Retries (Netzwerk, mobile Reconnects, Slack-Replays) kein Doppel-Event erzeugen. Validierungsfund B7: TTL war in v1 undefiniert — die Spec `same_idempotency_key__no_duplicate` ist nur sinnvoll mit klarer Lebensdauer.

## Options

1. **Client-generierte UUID, UNIQUE-Index `(workspace_id, idempotency_key)`, 24h TTL, Cleanup-Job**
2. **Server-Hash über Payload** als Key
3. **Hybrid:** Client-UUID bevorzugt, Server-Hash als Fallback
4. **Keine Idempotenz** — Client-Verantwortung

## Decision

**Client generiert UUID v4 als `Idempotency-Key`-Header.** Server validiert: `UNIQUE (workspace_id, idempotency_key) WHERE idempotency_key IS NOT NULL` im `events`-Index (Validierungsfund H8: workspace-scoped, nicht global).

**TTL:** 24 Stunden. Ein arq-Cron-Job (`idempotency_cleanup`, stündlich) setzt `idempotency_key = NULL` auf Events älter als 24 Stunden. Danach darf derselbe Key wieder akzeptiert werden — pragmatischer Kompromiss zwischen Speicher und Replay-Resilienz.

## Consequences

- Test `test_idempotency_key__after_ttl__accepted_as_new` in Iter 2 (siehe Plan Iter 2a Red).
- Storage-Wachstum begrenzt; Index bleibt klein, weil Cleanup NULL-setzt.
- Clients müssen `Idempotency-Key` bei kritischen Mutations setzen (POST `/api/proposals`, POST `/api/ideas`, etc.). Optional für GETs.
- Doku-Pflicht in OpenAPI-Spec.

## Alternatives Rejected

- **Server-Hash über Payload** — verworfen: zwei semantisch unterschiedliche Operationen mit identischem Payload würden als Duplikate behandelt; Hash-Kollisionen bei JSON-Reordering ohne canonical-JSON-Diskussion.
- **Hybrid Client-UUID + Server-Hash-Fallback** — verworfen: doppelte Logik, doppelter Failure-Mode. Wenn Client zuverlässig UUID generiert (alle modernen HTTP-Libraries können das), reicht der Single Path.
- **Keine Idempotenz** — verworfen: Slack-Retry-Verhalten allein würde unsere Event-Tabelle mit Duplikaten füllen.
