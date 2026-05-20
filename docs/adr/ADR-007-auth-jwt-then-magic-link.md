# ADR-007: Auth — JWT zuerst, Magic-Link danach

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Product + Tech-Lead
- **Blockiert:** Iter 4a + 4b

## Context

Iter 4 braucht Multi-User-Auth, bevor Iter 5 Kanban-Collaboration startet. Validierungsfund H3 zeigte: Magic-Link mit Email-Provider, DNS, Bounce-Handling, Rate-Limits, Replay-Schutz passt nicht in einen Sprint. Iter 4 wurde gesplittet in 4a (Foundation) und 4b (Magic-Link).

## Options

1. **JWT + Seed-Test-User in 4a, Magic-Link + Email-Provider in 4b, OAuth später**
2. **OAuth direkt (Google/GitHub) als einzige Authentifizierung**
3. **Slack Identity** als primärer Auth-Provider
4. **Hosted Auth (Clerk, Auth.js, Supabase Auth)**

## Decision

**Iter 4a:** JWT (HS256) signiert mit `JWT_SECRET`, kurze Access-TTL (15 min), Refresh über `sessions`-Row (revozierbar). Dev/Staging hat `scripts/seed_test_user.py`, der deterministische User + Workspace + JWT erzeugt.

**Iter 4b:** Magic-Link-Flow mit Provider-Interface (`EmailProvider`). Konkreter Provider (Postmark / Resend / SES) wird in Iter-4b-PR ausgewählt. Token-Replay-Schutz: Single-Use, 15-min-TTL, Rate-Limit 5/15min pro Email.

**OAuth** und **Slack Identity** kommen nach MVP, wenn Workspaces auch echte Externe einladen.

## Consequences

- 4a-Tests laufen mit deterministischen Test-JWTs ohne Email-Infrastruktur.
- Bestehende Iter-0–3-Tests werden in 4a auf `authenticated_client` migriert (siehe Validierungsfund B6).
- Provider-Interface erlaubt Anbieterwechsel ohne Logikänderung.
- Magic-Link braucht DNS-Setup (SPF/DKIM/DMARC) als Runbook-Eintrag in `docs/RUNBOOK.md`.

## Alternatives Rejected

- **OAuth direkt** — verworfen: setzt voraus, dass jeder Nutzer ein Google/GitHub-Konto hat und bereit ist, das mit dem Workspace zu verknüpfen. Erhöht Onboarding-Friktion für Slack-Power-User. Außerdem bindet uns ein OAuth-Provider an dessen Identity-Modell, bevor wir wissen, was die Nutzer-Basis aussieht.
- **Slack Identity** — verworfen: koppelt Login zwingend an Slack-Verfügbarkeit, schließt Nicht-Slack-Nutzer aus, macht Tests fragil (Slack-Test-Workspace nötig in jedem CI-Job).
- **Hosted Auth (Clerk/Auth.js)** — verworfen: schneller Start, aber Lock-in, monatliche Kosten, weniger Kontrolle über Audit-Daten (jeder Login-Versuch ist relevant für unser Audit-Log). Zudem braucht Hosted Auth einen separaten Backend-Sync für Workspaces/Memberships, was die Komplexität nicht reduziert.
