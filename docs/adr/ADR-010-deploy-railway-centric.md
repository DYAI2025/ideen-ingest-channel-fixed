# ADR-010: Deployment Railway-zentriert

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Product + Tech-Lead
- **Blockiert:** Iter 10 (Deployment Hardening)

## Context

Der Stack braucht: dauerhaften FastAPI-Prozess (WebSockets), Worker (arq, ADR-005), Postgres, Redis. Handoff §6 priorisiert Railway-Variante, weil der Code bereits Nixpacks/Railway-nah ist und Railway dauerhafte Backend-Prozesse + Datenbanken + Workers als Managed-Services anbietet.

## Options

1. **Railway-zentriert:** Backend + Worker + Postgres + Redis alle auf Railway.
2. **Vercel + Railway Hybrid:** Frontend auf Vercel, Rest auf Railway.
3. **Fly.io** für alles.
4. **VPS (Hetzner/Hostinger) mit Docker Compose.**
5. **Supabase + Vercel:** Supabase Postgres + Auth + Realtime, FastAPI nur für Worker/Slack.

## Decision

**Railway-zentriert.** Konkret: vier Railway-Services im selben Projekt: `backend-web`, `backend-worker`, `postgres`, `redis`. Frontend optional auf Railway-Static oder Vercel — Wahl in Iter 10 nach Performance-Messung.

## Consequences

- `railway.json` existiert bereits, muss um Worker-Service erweitert werden.
- Healthchecks pro Service in `railway.json`.
- Postgres-Backup via Railway-Volume + nightly `pg_dump` (siehe Plan §2.7).
- Vendor-Lock-Risiko mittel: Railway-Spezifika beschränken sich auf `railway.json` und Env-Var-Konventionen.
- Skalierungsgrenze: Railway Plus-Plan reicht für MVP; Wechsel auf Pro/Enterprise oder Migration zu Fly/VPS bei höherer Last.

## Alternatives Rejected

- **Vercel + Railway Hybrid** — Option, nicht abgelehnt; offen als Iter-10-Sub-Entscheidung. Vercel-Frontend liefert bessere DX, kostet aber zusätzliche Vendor-Beziehung. Wird gegen Railway-Static abgewogen, sobald Performance-Daten vorliegen.
- **Fly.io** — verworfen: gute Alternative, aber Railway hat reifere PR-Preview-Environments und schlankere `railway.json`-Config als Fly's `fly.toml`-Vielfalt. Auf Fly würden wir mehr CI-Skripte schreiben.
- **VPS mit Docker Compose** — verworfen: höherer Ops-Overhead (Updates, Backups, Monitoring, TLS), kein Managed-Postgres, kein PR-Preview. Für MVP zu viel undifferenzierte Arbeit.
- **Supabase + Vercel** — verworfen für jetzt: Supabase Realtime ersetzt unsere eigene WS-Schicht teilweise, aber wir verlieren Kontrolle über Audit-Log-Granularität und können Postgres-Erweiterungen wie RLS-Custom-Policies oder LISTEN/NOTIFY-Triggers nicht so direkt steuern. Erneut prüfen, wenn Datenmodell stabil ist.
