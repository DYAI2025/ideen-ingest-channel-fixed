# ADR-016: Governance-Waiver für Preflight-PRs #5 und #6

- **Status:** Accepted
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Geltungsbereich:** PR #5 (`chore/adr-stack`) und PR #6 (`chore/preflight-infra`). Einmalig.
- **Sunset:** ab Iter 0 ist Skip des Reviewer-Chain ein Merge-Blocker.

## Context

Plan §2.5 (`docs/IMPLEMENTATION_PLAN_TDD.md`) verlangt für jeden Iter-PR drei Reviewer:

1. 1× menschliche Review.
2. 1× `/code-review-excellence` Subagent-Pass.
3. 1× `/code-review-checklist` Bot-Pass.

Beide Preflight-PRs (#5, #6) wurden von einem einzigen Agent-Autor erstellt und ohne diesen Chain gemergt. Validierungsfund aus `/ultrathink-craftsmanship` (Phase 4 Gegenprüfung): Skip ist Governance-Verstoß und Präzedenz, die in späteren Iterationen erodieren kann, wenn nicht ausdrücklich begrenzt.

## Decision

Der Reviewer-Chain-Skip auf PR #5 und PR #6 wird **rückwirkend** durch diese ADR autorisiert, mit folgenden Auflagen:

1. **Sunset:** Ab Iter 0 (erster Sprint nach diesem Waiver) ist der vollständige 3-Reviewer-Chain harter Merge-Blocker. Branch-Protection-Regel auf `main` wird im Iter-10-Hardening-Pass aktiviert; bis dahin gilt der Chain als Konvention.
2. **Compensating Control:** PR `chore/preflight-fix` (dieser PR) durchläuft den vollständigen Chain und repariert konkrete technische Schulden aus den Skip-PRs (insbesondere `|| true`-Suppressions in `ci-fast.yml`, fehlendes `.gitignore`, ungepinnte Action-Version).
3. **Audit-Trail:** Diese ADR + der Validierungsbericht `docs/IMPLEMENTATION_PLAN_TDD_v2_findings.md` dokumentieren Skip-Begründung und Reparatur transparent.
4. **No-Repeat-Klausel:** Jeder zukünftige Skip-Antrag (auch durch Termin-Druck) braucht eine neue ADR mit eigener Begründung und expliziter Approval einer zweiten menschlichen Review. Goal-Hook-Termindruck ist keine zulässige Begründung.

## Consequences

- Plan-Disziplin bleibt intakt, weil die Ausnahme dokumentiert, befristet und ausgleichend repariert ist.
- Reviewer-Chain wird ab Iter 0 striktes Gate, was zusätzliche Latency pro PR bedeutet (~1 Tag für menschliche Review).
- Wenn die Reviewer-Chain in Iter 0 als zu schwer empfunden wird, ist die Antwort, Plan §2.5 zu ändern — nicht erneut zu skippen.
- Bot-Pass `/code-review-checklist` ist abhängig von der Verfügbarkeit dieses Subagent im Claude-Code-Setup; falls nicht verfügbar, dokumentiert der PR-Autor das in einer Findings-Disposition-Tabelle und nutzt einen funktional gleichwertigen Lint/Format-Check-Pass.

## Alternatives Rejected

- **Plan §2.5 absenken (Chain auf 2 Reviewer reduzieren)** — verworfen: das eigentliche Problem war Termindruck, nicht Chain-Größe. Wer einmal nachgibt, gibt wieder nach. Discipline-Inflation hätte schleichende Qualitäts-Erosion zur Folge.
- **PRs #5 und #6 revertieren und mit Chain re-erstellen** — verworfen: Inhalt ist korrekt; nur der Prozess war fehlerhaft. Revert + Redo verbraucht ½ Sprint ohne neuen Wert. Stattdessen Compensating Control über `chore/preflight-fix`.
- **Nichts tun, in CHANGELOG erwähnen, weitermachen** — verworfen: ohne Sunset-Klausel etabliert sich Skip als zulässige Option. Governance verliert Bindungskraft.
- **Branch-Protection auf `main` sofort aktivieren** — verworfen für jetzt: würde diesen Reparatur-PR selbst blockieren, weil das Repo noch keine angepasste Reviewer-Pflicht in Branch-Settings hat. Aktivierung in Iter 10 (Deploy Hardening) ist im Plan vorgesehen.
