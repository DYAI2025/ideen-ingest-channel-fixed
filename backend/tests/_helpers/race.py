"""Concurrency-stress helper for race-condition tests.

Used by Iter 5 (Kanban concurrent moves) and any later iteration that needs to
prove a write path serialises correctly under N parallel callers.

Stub implementation: the real `run_race` arrives with Iter 5. Defining the API
contract here lets Iter 5 author tests against a known signature without
inventing it during Red phase.

Example (Iter 5):

    from tests._helpers.race import run_race

    async def move(client, task_id, target_column, revision):
        return await client.post(
            f"/api/kanban/tasks/{task_id}/move",
            json={"column": target_column, "revision": revision},
        )

    results = await run_race(N=50, max_parallel=20, op=lambda: move(...))
    successes = [r for r in results if r.status_code == 200]
    conflicts = [r for r in results if r.status_code == 409]
    assert len(successes) == 1
    assert len(conflicts) == 49
"""
from __future__ import annotations

import asyncio
from typing import Awaitable, Callable, Sequence, TypeVar

T = TypeVar("T")


async def run_race(
    N: int,
    op: Callable[[], Awaitable[T]],
    *,
    max_parallel: int = 20,
) -> Sequence[T]:
    """Execute `op` N times concurrently, bounded by `max_parallel`.

    The bound prevents tests from exhausting the Postgres connection pool.
    Plan §2.6 sets pool size to 60; default 20 leaves headroom for the
    framework and other fixtures.

    Returns results in the order they completed; callers asserting
    `exactly one winner` should look at status codes, not order.
    """
    semaphore = asyncio.Semaphore(max_parallel)

    async def _guarded() -> T:
        async with semaphore:
            return await op()

    return await asyncio.gather(*(_guarded() for _ in range(N)))
