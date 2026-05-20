# ADR-012: TDD-Stil — Hybrid (London an Service-Grenzen, Chicago im Domänenkern)

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** jede Iteration (Review-Konvention)

## Context

TDD-Stile divergieren bei Test-Doubles: London-Schule mocked Kollaborateure und testet Interaktionen; Chicago-Schule baut State-Assertions auf echten Objekten. Plan §1 D9 / Validierungsfund: ohne festgelegte Konvention streiten Reviewer in jeder Iter über Mocks vs. echte Datenbank.

## Options

1. **Hybrid:** London an Service-Boundaries (HTTP, DB, Worker-Queue), Chicago im Domänenkern (Event-Logik, Proposal-Validierung).
2. **London-Schule durchgehend:** Mocks überall, schnellere Tests, riskiert Drift zwischen Mock und Realität.
3. **Chicago-Schule durchgehend:** echte Datenbank, echte HTTP-Mocks via `respx`, langsamer aber realistischer.
4. **Keine Konvention** — Engineer entscheidet pro PR.

## Decision

**Hybrid.**

- **Unit-Tests** (Domänenkern, Proposal-Logik, Event-Hashing, Reducer): keine Mocks, reine Objekte, State-Assertions (Chicago).
- **Integration-Tests** (FastAPI TestClient + echte Postgres): Chicago im Inneren, aber HTTP-Calls nach außen (LLM, Slack, Email) werden via `respx`/VCR gemockt (London-Element).
- **Boundary-Tests** (Worker-Jobs, Slack-Handler): klassisches London — Mock-Assertions, dass enqueue/dispatch passiert sind.

Reviewer-Findings, die Stil-Diskussion eröffnen wollen, werden auf diese ADR verwiesen.

## Consequences

- Klarheit in Code-Reviews.
- Test-Suite läuft schnell genug, weil Mocks an teuren Boundaries gesetzt werden.
- Mocked-Domänenlogik ist ein Code-Smell und Review-Blocker.

## Alternatives Rejected

- **London durchgehend** — verworfen: Mocks der Domänenlogik führen zu Test-Sklerose; Refactors brechen Tests ohne dass das Verhalten falsch ist.
- **Chicago durchgehend** — verworfen: Tests gegen echte LLM-/Slack-/Email-APIs sind unbezahlbar und nicht-deterministisch.
- **Keine Konvention** — verworfen: produziert genau die Diskussionen, die diese ADR vermeidet.
