# ADR-009: LLM-Provider Anthropic, Tests via VCR-Recording

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 3 (Proposal Pipeline)

## Context

Iter 3 erzeugt Proposals aus Agent-Runs. Sobald LLM-Calls im Pfad sind, ist Reproduzierbarkeit schwer — selbst bei `temperature=0` driften Modelle zwischen Versionen. Validierungsfund M11: Tests müssen LLM-Calls deterministisch replayen können, sonst flakt jede Pipeline.

## Options

1. **Anthropic Claude via Provider-Interface + VCR-Cassettes in Tests**
2. **OpenAI direkt** ohne Provider-Interface
3. **Ollama lokal** als einziger Provider
4. **Tests komplett ohne LLM** (Mock-Output, kein echtes Recording)

## Decision

**Anthropic Claude (`claude-sonnet-4-6` / `claude-opus-4-7`) hinter Provider-Interface `LLMProvider`.** Implementierungen: `AnthropicProvider`, `OpenAIProvider` (optional), `MockProvider` (für Unit-Tests ohne Cassette).

**Integration-Tests** verwenden `vcrpy`-Cassettes unter `backend/tests/fixtures/cassettes/llm/`. Cassettes werden einmal manuell mit echten API-Keys aufgenommen, dann ins Repo committed. CI hat keine API-Keys; Replay-Modus ist Pflicht.

## Consequences

- Neue Runtime-Dependency: `anthropic>=0.40`. Dev-Dependency: `vcrpy>=6`.
- `ANTHROPIC_API_KEY` als Env-Var; nicht im Repo.
- Cassettes versioniert; Re-Recording erfordert PR-Diff und bewusste Entscheidung.
- Anbieterwechsel = neue Provider-Klasse + neue Cassettes.
- Cost: nur bei Cassette-Aufnahme oder Prod-Betrieb.

## Alternatives Rejected

- **OpenAI direkt ohne Provider-Interface** — verworfen: Lock-in. Wechsel auf Anthropic oder lokales Modell würde alle Aufrufer anfassen müssen.
- **Ollama als einziger Provider** — verworfen: lokale LLMs sind für Proposal-Generierung qualitativ unterhalb Claude/GPT-Niveau (Stand 2026-05). Eingesetzt nur als Dev-Convenience.
- **Tests ohne LLM** — verworfen: Mock-Outputs entkoppeln Test von tatsächlicher Anbieter-API-Form, lassen Schema-Drift unbemerkt. VCR ist der Mittelweg: realer Wire-Verkehr, deterministisch replayed.
