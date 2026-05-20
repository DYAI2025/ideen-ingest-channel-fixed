# ADR-008: Embeddings — sentence-transformers all-MiniLM-L6-v2, gepinnt

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 7 (Semantic Analysis)

## Context

Iter 7 muss reproduzierbare Embedding-Vektoren liefern, damit Tests deterministisch sind. Validierungsfund B4: jeder Cloud-Embedding-Provider ist eine externe Black-Box mit Versionsdrift; lokale Modelle haben Hardware-abhängige Float-Drifts in tieferen Dezimalstellen, sind aber auf einer fixen Plattform stabil.

## Options

1. **sentence-transformers `all-MiniLM-L6-v2` offline, Version gepinnt, CI-Plattform Linux/x86 fixiert**
2. **OpenAI `text-embedding-3-small`** als Cloud-Provider
3. **Voyage AI** als Cloud-Provider
4. **Ollama** mit lokalem Modell wie `nomic-embed-text`
5. **bge-small** statt MiniLM, sonst gleiche Strategie

## Decision

**sentence-transformers `all-MiniLM-L6-v2`** in der Version `==2.7.0`. Modellgewichte als Git-LFS-Artefakt in `backend/tests/fixtures/embeddings/`, Hash in `MODEL_HASH`. CI-Plattform pinned auf `ubuntu-22.04 x86_64` mit `openblas`. Determinismus-Assertion via `np.allclose(v1, v2, atol=1e-4)` statt Byte-Identität.

Default in Prod = dasselbe Modell. Ollama-Path nur als Dev-Convenience. OpenAI als optionaler Provider hinter Interface, deaktiviert in Tests.

## Consequences

- Keine externen API-Calls in Tests, kein Rate-Limit, keine Kosten.
- ~80 MB Modell-Artefakt im Repo (Git LFS).
- Apple-Silicon-Devs sehen abweichende Vektoren ab der 4. Dezimalstelle gegenüber CI; akzeptiert, weil CI die kanonische Quelle ist.
- Modell-Update = ADR-Update + Re-Hashing + bewusster Plan.

## Alternatives Rejected

- **OpenAI text-embedding-3-small** — verworfen für Tests: Modell-Versionsdrift (Anbieter rotiert intern), Rate-Limits brechen CI, Kosten skalieren mit Test-Suite-Größe. Bleibt als optionaler Prod-Provider hinter Interface.
- **Voyage AI** — verworfen: gleiche Drift- und Kostenprobleme wie OpenAI, kleinere Community, schlechtere Reproduzierbarkeit.
- **Ollama** — verworfen für Tests: lokale Installation in CI komplex (GPU-Erkennung, Modell-Pull, Disk-Space), Hardware-Drift stärker als bei reinen CPU-Inference-Modellen.
- **bge-small** — verworfen: marginal bessere Benchmark-Scores, aber MiniLM hat reifere Tooling-Integration in `sentence-transformers` und schnellere Inference auf CPU.
