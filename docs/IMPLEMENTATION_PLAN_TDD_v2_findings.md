# Validierungsbericht v1 → v2 — `IMPLEMENTATION_PLAN_TDD.md`

**Datum:** 2026-05-20
**Validierungs-Skill:** `ultrathink-craftsmanship` (Modus: voll)
**Quelle v1:** Git-History desselben Pfads.

Dieser Bericht dokumentiert, welche Findings aus der Validierung in v2
eingearbeitet wurden. Jedes Finding hat Severity, Fix-Status und Verweis
auf v2-Abschnitt.

---

## BLOCKER — vor erster Iter zwingend behoben

| ID  | Finding                                                                         | Status         | v2-Sektion                                |
| --- | ------------------------------------------------------------------------------- | -------------- | ----------------------------------------- |
| B1  | Coverage-Gate ≥ 80 % global selbst-blockierend                                  | FIXED          | §2.1 → Diff-Coverage per `diff-cover`     |
| B2  | Iter-2-Shadow-Phase widerspricht "jede Iter deploybar"                          | FIXED          | Iter 2 in 2a (Code) + 2b (Cutover) gesplittet |
| B3  | FileLock funktioniert nicht auf Railway-Multi-Host                              | FIXED          | D12 + ADR-015 + Iter 5: Postgres Advisory + Redis SET NX |
| B4  | Embedding-Determinismus zu stark behauptet ("byteidentisch")                    | FIXED          | Iter 7 Determinismus-Spec: Toleranz `atol=1e-4`, CI-Plattform pinned |
| B5  | Redis Pub/Sub kann kein Replay → Iter-9-Reconnect-Promise gebrochen             | FIXED          | D3 + Iter 9: Postgres = Source, Redis Streams Fan-Out, Pub/Sub nur Wake |
| B6  | Auth Iter 4 bricht Iter-0–3-Tests, Migration nicht budgetiert                   | FIXED          | Iter 4a Green: `authenticated_client`-Fixture + Test-Migration im selben PR |
| B7  | ADR-013 Idempotency-TTL undefiniert                                             | FIXED          | D10 + Iter 2a: 24 h UNIQUE, Cleanup-Job, eigener Test |

---

## HIGH — Iter überlauf-/scheiter-Risiko

| ID  | Finding                                                       | Status   | v2-Sektion                                                  |
| --- | ------------------------------------------------------------- | -------- | ----------------------------------------------------------- |
| H1  | CI-Laufzeit < 10 min unrealistisch                            | FIXED    | §2.4 ci-fast (< 5 min) / ci-deep (< 25 min) Split           |
| H2  | Iter 6 GBRAIN-Flag-Inkonsistenz (default false vs Acceptance) | FIXED    | Iter 6 Flag-Spec: Prod default false, Tests Override        |
| H3  | Magic-Link in 1 Sprint zu klein                               | FIXED    | Iter 4 in 4a (JWT+Seed) + 4b (Magic-Link) gesplittet        |
| H4  | MCP-Vertragstest in Iter 0 nicht haltbar                      | FIXED    | Iter 0 Test nur auf ENV-Lesen reduziert; Vertrag in Iter 1  |
| H5  | Projection-Rebuild-Strategie fehlt                            | FIXED    | Iter 2a + `projection_state`-Tabelle + Advisory-Lock-Rebuild |
| H6  | arq-Subscription auf Postgres-Events fehlt (Bridge)           | FIXED    | Iter 7 Event-Bridge-Worker via `LISTEN events_channel`       |
| H7  | Concurrency-Test sprengt DB-Pool                              | FIXED    | §2.6 Pool 60, Semaphore 20, Marker `serial`                 |
| H8  | Idempotency-UNIQUE nicht Multi-Tenant-sicher                  | FIXED    | Iter 2a Schema: `UNIQUE (workspace_id, idempotency_key)`     |
| H9  | Backup-Strategie erst Iter 10 statt Iter 2                    | FIXED    | §2.7 + Iter 2a Acceptance: Nightly-Backup ab Event-Store    |
| H10 | "Track"-Spalte in PR-Quality-Checklist existiert nicht        | FIXED    | §2.5 + Iter-Tabelle: "Sektion" statt "Track"                |

---

## MEDIUM — Rework-Vermeidung

| ID  | Finding                                                  | Status   | v2-Sektion                                                 |
| --- | -------------------------------------------------------- | -------- | ---------------------------------------------------------- |
| M1  | Frontend-localhost-Test in Iter 0 statt Iter 1           | FIXED    | nach Iter 1 verschoben                                     |
| M2  | Test-Naming-Convention (Datei pro Test = Bloat)          | FIXED    | §2.1: Datei pro Modul, Funktion `test_<scenario>__<expected>` |
| M3  | ADRs ohne "Alternatives Rejected"                        | FIXED    | §6: Pflicht-Template, eigene Dateien `docs/adr/ADR-XXX-*.md` |
| M4  | Polling-Fallback ohne Sunset                             | FIXED    | Iter 9 Sunset-Kriterium + Iter 10 Acceptance               |
| M5  | Slack-Timing-Test flaky                                  | FIXED    | Iter 8: Design-Test (`returns_200_before_processing`) statt Wallclock |
| M6  | Workspace-Onboarding-Flow fehlt                          | FIXED    | Iter 4a Green: `POST /api/workspaces`, Invites, Rollen     |
| M7  | Sprint-Länge undefiniert                                 | FIXED    | §0: 2 Wochen, 60 % Fokuszeit, Worst-Case-Median            |
| M8  | Mutation-Pfade zu eng (auth, gbrain fehlten)             | FIXED    | §2.1: Pfade erweitert auf 5 Module                         |
| M9  | Proposal-Expiry fehlt                                    | FIXED    | Iter 3 Schema: `expires_at` + Cleanup-Job                  |
| M10 | Tenancy-Modell offen                                     | FIXED    | D11 + ADR-014 + Iter 2a RLS-Migration                      |
| M11 | LLM-Recording fehlt                                      | FIXED    | D6/ADR-009 + §5: VCR-Cassettes Pflicht                     |
| M12 | Git-Sync-Konflikte für Vault                             | FIXED    | D8 + ADR-011 + Iter 6 Singleton-Worker                     |

---

## LOW — Polish

| ID  | Finding                                | Status     | v2-Sektion                          |
| --- | -------------------------------------- | ---------- | ----------------------------------- |
| L1  | PR-Stack-Strategie nicht spezifiziert  | DEFERRED   | bewusst offen, Team-Wahl            |
| L2  | Double-Underscore in Test-Namen        | ACCEPTED   | bleibt; Pep-8-konform               |
| L3  | Decision-Owner-Spalte fehlt            | FIXED      | §1: Spalte `Owner` ergänzt          |
| L4  | Mermaid-Diagramm Iter-Abhängigkeiten   | DEFERRED   | Anhang B Tabelle als Ersatz         |
| L5  | Glossar fehlt                          | FIXED      | Anhang A                            |

---

## Konfabulations-Audit (aus Validierung)

| Claim                                                          | Status v1                | Behandlung v2                                                 |
| -------------------------------------------------------------- | ------------------------ | ------------------------------------------------------------- |
| `sentence-transformers all-MiniLM-L6-v2` offline-deterministisch | ableitbar, Vorbehalt   | Plattform pinned + Toleranz spec'd                            |
| `arq` async-native, leicht                                     | belegt                   | unverändert                                                   |
| Schemathesis "0 Findings" als Acceptance                       | ungeprüft                | "alle gefixt **oder explizit whitelisted**"                   |
| Mutation-Score 75 % erreichbar                                 | ungeprüft                | R9: Pilotlauf Iter 2 misst echten Score; Gate ggf. gesenkt   |
| CI < 10 min für vollen Run                                     | nicht behauptbar         | Split ci-fast / ci-deep; jeweils eigene Budgets               |
| Magic-Link in 1 Sprint                                         | nicht behauptbar         | 1 Sprint → 2 Sub-Iter                                         |
| MCP-Drift                                                      | belegt aus Handoff       | Iter 1 contract-snapshot + Iter 3/5 endpoint fixes            |

---

## Verbleibende offene Punkte (nicht plan-blockierend)

- Email-Provider-Wahl für Iter 4b (Postmark / Resend / SES).
- Obsidian-Vault-Identität für Iter 6 (existierend vs greenfield).
- Slack-Org für Iter 8.
- Realtime-SLO-Verschärfung für Cursor/Presence post-MVP.

---

## Nächste Aktion

1. ADR-Stack (ADR-004…015) als Routine-PR.
2. Preflight-PR mit Test-Infra + CI-Split.
3. Iter 0 starten.

Validator-Hinweis: v2 ist hinreichend für Start. Weitere Validierungsrunden
nicht nötig vor Iter 0. Re-Validierung empfohlen vor Iter 4a (Auth ist
sicherheitsrelevant) und Iter 7 (Embedding-Determinismus empirisch belegen).
