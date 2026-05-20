# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Shape

Three-package monorepo:

- `backend/` — FastAPI service (Python 3.12+), entry point `src/main.py`, package `src/` (built via Hatchling, configured in `backend/pyproject.toml`). Mounts API routers under `/api/*` and serves a static frontend dir from `../frontend` at `/`.
- `frontend/` — React 19 + TypeScript + Vite SPA. UI for drag-and-drop ingest, idea search, Kanban board, and React Flow graph visualization.
- `mcp/ideen-channel/` — Standalone MCP (Model Context Protocol) server exposing the backend's idea/kanban APIs as MCP tools for WUPHF agent integration. Has its own `pyproject.toml`, `setup.py`, and `ideen_channel/` package.

Each package is deployed independently — there is no shared dependency graph. Railway treats backend and frontend as two separate services (see `railway.json`). The MCP server has its own `setup.py` because the bare `pyproject.toml` caused Railway build failures (see commit `bab5a71`).

## Common Commands

### Backend (run from `backend/`)

```bash
python3 -m venv venv && source venv/bin/activate
pip install -e .                                # editable install via pyproject
# or: pip install -r requirements.txt           # pinned versions (used by Railway)

uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload   # dev
python -m src.main                              # runs on port 8000 (main.py default)
```

Port mismatch is intentional and known: `src/main.py`'s `__main__` block uses **8000**, but `deploy.sh`, `RAILWAY` configs, the README, and the systemd unit all use **8001**. Use 8001 unless you have a reason not to.

### Frontend (run from `frontend/`)

```bash
npm install
npm run dev                # vite dev server on :5173
npm run build              # tsc -b && vite build → dist/
npm run preview            # serves built dist on $PORT (used in prod/Railway)
npm run lint               # eslint
```

### MCP Server (run from `mcp/ideen-channel/`)

```bash
pip install -e ".[dev]"
ideen-channel-server                  # via entry point
python -m ideen_channel.server        # direct
python run_server.py                  # script

pytest                                # all tests
pytest tests/test_cache.py -v         # single file
pytest --cov=ideen_channel            # with coverage
```

Tests live in `mcp/ideen-channel/tests/` (cache, client mock, config, rate limiter). The README claims `src/tests/` but the actual path is `tests/` at the package root.

### Full stack

```bash
./deploy.sh           # spawns backend (8001) + frontend (5173) together, traps SIGINT
./build-prod.sh       # production frontend build only
```

## Architecture Notes

### Backend service wiring (`backend/src/main.py`)

Routers are mounted under `/api/<area>`: `ingest`, `ideas`, `status`, `graph`, `kanban`, `semantic`, `agents`. Adding a new area means a new router module under `src/api/` plus an `app.include_router(...)` call. `/health` is the Railway healthcheck and lives directly on the app (not on a router).

Three long-lived services are instantiated at module scope: `GBrainService`, `FileWatcher`, `KanbanSyncService`. The file watcher's startup task is **deliberately commented out** to break an import loop — re-enabling it requires fixing that loop, not just uncommenting.

CORS is wide open (`allow_origins=["*"]`). The README flags this for SSH-tunnel adjustment, but it has not been narrowed.

The static mount at `/` serves the frontend dir and creates it if missing. This means the catch-all swallows anything not under `/api`, `/health`, `/docs`, `/redoc` — be careful adding new top-level routes.

### GBrain integration

The backend shells out to the `gbrain` CLI via subprocess (`backend/src/services/gbrain_service.py`). The CLI must be on `$PATH` of the process running uvicorn. Default upload directory is `~/ideen-growth-system/seeds` (configurable via `UPLOAD_DIR`). Allowed file extensions for ingest are hardcoded in `Settings`: `.md, .txt, .json, .yaml, .yml`.

### MCP server architecture

`FastMCP` server wraps an `IdeenClient` (httpx) → `IdeaCache` (TTL) → `RateLimiter` (token bucket) chain over the backend HTTP API. Set `IDEEN_CHANNEL_MOCK_CLIENT=true` to swap in `mocks.py` for offline testing. Default backend URL is `http://localhost:8002` (note: not 8001 — the MCP server expects backend on a different port than the dev default).

### Frontend

Single Vite app with multiple top-level views as siblings in `src/`: `App.tsx`, `KanbanBoard.tsx`, `GraphVisualization.tsx`, `ObsidianGraph.tsx`, `SimpleGraph.tsx`, `SSHGraph.tsx`. API base URL is hardcoded in `App.tsx` as `/api` — relies on Vite's proxy in dev and same-origin in prod.

## Deployment

### Railway (primary target)

`railway.json` declares two services (backend + frontend) under one project, each with its own nixpacks build. Backend uses pinned `requirements.txt`; frontend runs `npm ci && npm run build` then `npm run preview` on `$PORT`. Healthcheck paths: `/health` (backend), `/` (frontend).

Root `nixpacks.toml` is a no-op stub — it exists only so Railway doesn't try to build the monorepo root as a single app.

### Systemd

`ideen-ingest-backend.service` deploys the backend on a host with the GBrain CLI installed. Copy to `/etc/systemd/system/` and enable.

### Cloudflare / Caddy / SSH

The 5+ `Caddyfile-*` variants and `setup-cloudflare*.sh` / `setup-tailscale*.sh` scripts are deployment experiments — treat them as historical artifacts, not the canonical path. `RAILWAY-DEPLOYMENT.md` and `SSH-DEPLOYMENT.md` are the documents to trust.

## PR Quality

`docs/PR-quality-checklist.md` defines two tracks:

- **Protocol-grade PR** — for new packages, wire shapes, security boundaries, protocol/storage contracts. Requires CI in the same PR, `AGENTS.md`, demo script, cross-language oracle, file-size budgets, strict-unknown rejection, no `any`/`@ts-ignore`/`--no-verify`, and a per-finding disposition table.
- **Routine PR** — bug fixes, refactors, docs. Tests + lint + typecheck clean, no new suppressions, "why" in description.

Copy the matching track into the PR description.

## Gotchas

- Backend `__main__` port (8000) ≠ deploy port (8001). Pick deliberately.
- MCP server's expected backend port (8002) ≠ either backend port. Set `IDEEN_CHANNEL_API_URL` to match where the backend actually runs.
- The file watcher startup task is commented out because of an import loop — don't blindly re-enable.
- `frontend_path` static mount catches everything not under `/api`. New top-level FastAPI routes won't be reachable.
- `backend/requirements.txt` and `backend/pyproject.toml` both exist with different version semantics (pinned vs floor). Railway uses requirements.txt; local editable installs use pyproject.toml.
