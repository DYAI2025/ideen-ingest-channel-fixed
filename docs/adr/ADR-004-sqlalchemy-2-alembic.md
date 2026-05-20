# ADR-004: SQLAlchemy 2.0 + Alembic als Persistenzlayer

- **Status:** Proposed
- **Date:** 2026-05-20
- **Decision Owner:** Tech-Lead
- **Blockiert:** Iter 2 (Event Store)

## Context

Der v2-Plan (`docs/IMPLEMENTATION_PLAN_TDD.md`, §1 D1) verlangt einen ORM/Migrationspfad für FastAPI. Postgres ist Source-of-Truth (Handoff ADR-001). Wir brauchen async-Support, weil der gesamte Stack auf `asyncio`/FastAPI läuft, und reversible Migrationen, weil jede Iter Schema-Änderungen einführt und die CI `alembic downgrade -1` als Gate fährt.

## Options

1. **SQLAlchemy 2.0 + Alembic** — etablierter ORM mit nativem async-Support, Alembic als kanonisches Migrations-Tool im SQLAlchemy-Ökosystem.
2. **SQLModel** — pydantic-basierter Wrapper über SQLAlchemy, kürzere Modelle.
3. **Tortoise ORM** — async-first ORM, Django-ähnliche API, Aerich für Migrationen.
4. **Raw SQL + Yoyo/Migra** — keine ORM, nur Migrations-Runner.

## Decision

**SQLAlchemy 2.0 (mit `AsyncSession`) + Alembic.**

SQLAlchemy 2.0 hat einen stabilen async-API, type-hint-freundlichen `Mapped[T]`-Stil und ist der Industriestandard in Python-Backends. Alembic ist Teil desselben Ökosystems, kennt Autogenerate für Migrations-Drafts und unterstützt sowohl Up- als auch Down-Migrationen sauber. Die CI-Gate-Sequenz `upgrade → downgrade -1 → upgrade` (siehe Plan §2.4) ist genau für Alembic gebaut.

## Consequences

- Neue Runtime-Dependency `sqlalchemy[asyncio]>=2.0`, `alembic>=1.13`, `asyncpg>=0.29`.
- Modelle in `backend/src/models/`, Migrationen in `backend/alembic/versions/`.
- Repository-Pattern in `src/services/*` kapselt Sessions.
- Lernkurve für Engineers, die nur den 1.x-Stil kennen.

## Alternatives Rejected

- **SQLModel** — verworfen: Pydantic + SQLAlchemy doppelt zu modellieren erzeugt Inkonsistenzen, sobald Validation und ORM auseinanderdriften. Außerdem hängt SQLModel hinter SQLAlchemy-Releases hinterher; wir würden bei async-Edge-Cases auf Workarounds angewiesen sein.
- **Tortoise ORM** — verworfen: kleinere Community, schwächere Type-Hints, Aerich-Migrationen unterstützen kein robustes Downgrade über mehrere Versionen hinweg — bricht das CI-Reversibilitäts-Gate.
- **Raw SQL + Yoyo** — verworfen: kein typsicheres Mapping zwischen Postgres-Rows und Python-Objekten, mehr Boilerplate in Services, kein Standard-Pfad für RLS-Session-Variablen-Injektion. Höhere Refactor-Kosten ab Iter 4 (Auth).
