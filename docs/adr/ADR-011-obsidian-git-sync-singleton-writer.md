# ADR-011: Obsidian Vault via Git-Sync, Singleton-Writer-Worker

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Product + Tech-Lead
- **Blockiert:** Iter 6 (GBrain Bridge)

## Context

Iter 6 schreibt strukturiert in den Obsidian-Vault. Validierungsfund M12: Mehrere Agenten + Workers schreiben in dasselbe Git-Repo → Merge-Konflikte. Wir brauchen eine Strategie, die Auditierbarkeit (Git-History) bewahrt, aber Konflikte vermeidet.

## Options

1. **Git-Sync + Singleton-Vault-Writer-Worker (Concurrency=1)**
2. **Lokales Volume ohne Git** (Railway-Volume mit Filesystem-Lock)
3. **WebDAV** auf gemeinsamen Vault
4. **Obsidian-Sync** (kommerzieller Cloud-Sync)
5. **Object-Storage (S3/R2)** mit Markdown-Datei-Schreiben

## Decision

**Git-Sync mit Singleton-Vault-Writer.** Konkret: ein arq-Worker namens `vault_writer` mit Queue `vault_writes` und `WORKER_CONCURRENCY=1`. Jeder Write durchläuft diesen einen Worker, der sequentiell `git pull --rebase`, schreiben, `git commit`, `git push` ausführt. Conflict-Resolution: letzter Write gewinnt, Konflikt wird in `events`-Tabelle als `vault.conflict.detected` geloggt.

## Consequences

- Volle Audit-Historie via Git-Log.
- Mergebare Markdown-Dateien.
- Single-Point-of-Failure: wenn Vault-Writer steht, queueen Writes. Monitoring zwingend.
- Schreib-Latenz höher als direktes Filesystem-Write (Git-Round-Trip).
- Konflikt-Audit-Pfad gibt Reviewern Gelegenheit zu manuellem Eingriff.

## Alternatives Rejected

- **Lokales Volume + FileLock** — verworfen: siehe Validierungsfund B3. FileLock funktioniert nicht über Railway-Multi-Host. Außerdem keine Audit-Historie ohne separate Pipeline.
- **WebDAV** — verworfen: schwächere Locking-Semantik als Git, schlechtere Tooling-Integration mit Obsidian (Obsidian erwartet lokale Filesystem-Semantik), unklare TLS-/Auth-Story.
- **Obsidian-Sync** — verworfen: kommerzieller Vendor-Lock, kein API zum programmatischen Schreiben, Konflikt-Resolution opaque.
- **S3/R2 mit Markdown-Schreiben** — verworfen: Obsidian erwartet Filesystem, nicht Object-Storage. Workaround via `rclone-mount` ist fragil. Audit nur über S3-Versioning, weniger expressiv als Git.
