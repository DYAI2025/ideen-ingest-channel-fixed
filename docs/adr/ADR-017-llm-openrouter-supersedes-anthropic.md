# ADR-017: LLM-Provider OpenRouter, ersetzt ADR-009 (Anthropic)

- **Status:** Accepted
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Supersedes:** ADR-009 (Anthropic + Provider-Interface mit VCR)
- **Blockiert:** Iter 3 (Proposal Pipeline)

## Context

ADR-009 wählte Anthropic Claude als primären LLM-Provider hinter einem austauschbaren `LLMProvider`-Interface. Die User-Direktive (2026-05-20) verlangt **OpenRouter** statt Anthropic als Default-Provider. OpenRouter bietet Modell-Aggregation über mehrere Anbieter (Anthropic, OpenAI, Google, Mistral, Meta, lokale Open-Source-Modelle) hinter einer einheitlichen API.

Diese ADR ersetzt ADR-009 als Quelle-der-Wahrheit für die LLM-Provider-Entscheidung. Das Provider-Interface (`LLMProvider`) selbst bleibt unverändert; ändert sich nur, welche Implementierung Default ist.

## Options

1. **OpenRouter als Default-Provider** (User-Direktive) — eine API-Key, Zugriff auf alle relevanten Modelle, einfache A/B-Modellwahl ohne Code-Änderung.
2. **Anthropic direkt** (ADR-009 Original) — direkter Anbieter, kein Routing-Overhead.
3. **OpenAI direkt** — alternative direkte Integration.
4. **Multi-Provider parallel** (OpenRouter + Anthropic + OpenAI als Peer-Implementierungen).

## Decision

**OpenRouter als Default-`LLMProvider`-Implementierung.**

- API-Endpoint: `https://openrouter.ai/api/v1/chat/completions` (OpenAI-kompatibel).
- API-Key: Env-Var `OPENROUTER_API_KEY`. Wert lebt lokal in `.env` (gitignored) und in CI-Repo-Secrets. Nie in Code, Logs, oder Commits.
- Default-Modell für Proposal-Generierung: konfigurierbar via `OPENROUTER_MODEL` (Standard: ein qualitätsstarkes Modell wie `anthropic/claude-opus-4` oder `openai/gpt-4o`; Iter 3 PR setzt den konkreten Default).
- VCR-Cassette-Strategie aus ADR-009 bleibt: alle LLM-Calls in Tests via `vcrpy` aufgenommen unter `backend/tests/fixtures/cassettes/llm/`. Cassettes werden einmal mit echtem Key generiert und dann ins Repo committed **erst nachdem** explizite Secret-Filterung aktiv ist (mindestens `Authorization`-Header via `filter_headers` konfigurieren, bevor irgendein Recording startet), damit kein `OPENROUTER_API_KEY` im Fixture landet.
- Provider-Interface (`LLMProvider`) unverändert: `OpenRouterProvider`, `MockProvider` (Unit-Tests), optional `AnthropicProvider` und `OpenAIProvider` als Fallbacks.

## Consequences

- Neue Runtime-Dependency: `openai>=1.0` (OpenRouter ist OpenAI-API-kompatibel) — kein separates OpenRouter-SDK nötig. Dev-Dep `vcrpy>=6` bleibt aus ADR-009.
- `ANTHROPIC_API_KEY` aus dem Variablen-Namespace entfernt. `OPENROUTER_API_KEY` ersetzt sie überall in Doku und Env-Beispielen.
- Modellwahl ist Runtime-Konfiguration, keine Code-Änderung — Iter 3 Tests können je Cassette unterschiedliche Modelle erzwingen.
- Anbieterwechsel weg von OpenRouter (zurück zu direktem Anthropic oder OpenAI) braucht nur eine neue Provider-Implementierung + neue Cassettes; das Interface trägt.
- VCR-Cassette-Recording-Workflow: vor Commit `vcrpy` so konfigurieren, dass `Authorization`-Header gestrippt wird. Iter-3-PR dokumentiert das Recording-Recipe in `docs/RUNBOOK-llm-recording.md`.
- Audit-Log: jede Proposal-Erzeugung notiert das tatsächlich verwendete Modell (aus OpenRouter-Response-Metadaten) in `events.payload`.

## Alternatives Rejected

- **Anthropic direkt (ADR-009)** — verworfen: User-Direktive. Auch ohne Direktive entfernt OpenRouter den Lock-in auf einen einzelnen Anbieter und reduziert die Anzahl der Provider-Keys, die wir verwalten.
- **OpenAI direkt** — verworfen: gleicher Lock-in wie Anthropic-direkt, Modellauswahl beschränkt auf OpenAI-Modelle.
- **Multi-Provider parallel** — verworfen für jetzt: doppelte Test-Cassetten je Provider, doppelte Quota-Verwaltung. OpenRouter macht Multi-Modell-Strategien implizit verfügbar ohne diesen Overhead. Wird re-evaluiert, wenn ein Anbieter ausfällt oder OpenRouter-Marge problematisch wird.
- **Lokale LLMs (Ollama) als Default** — verworfen: Qualität unter dem Niveau, das Iter 3 für Proposal-Generierung braucht (Stand 2026-05). Bleibt Dev-Convenience hinter dem Provider-Interface.
