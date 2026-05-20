"""Row-Level-Security helpers for tenant-isolation tests.

ADR-014 (`docs/adr/ADR-014-tenancy-row-with-rls.md`) enforces tenancy via
Postgres RLS using a session variable `app.current_workspace_id`. The middleware
that sets the variable in production lives behind Iter 4a (Auth Foundation).
Tests from Iter 2 onwards must be able to switch workspaces explicitly.

Stub implementation: the real helpers ship with Iter 2 once the workspaces
table exists. Defining the API here gives Iter 2 a known signature to write
its Red-phase tests against.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator
from uuid import UUID


@asynccontextmanager
async def as_workspace(session, workspace_id: UUID) -> AsyncIterator[None]:
    """Pin the current async DB session to a given workspace for RLS.

    Usage (Iter 2+):

        async with as_workspace(session, workspace_a):
            await session.execute(text("SELECT * FROM events"))
        # back to no workspace; queries return 0 rows under RLS

    The real implementation issues `SET LOCAL app.current_workspace_id` inside
    a transaction so the variable is rolled back on exit. The stub raises
    until Iter 2 lands.
    """
    raise NotImplementedError(
        "as_workspace lands with Iter 2 (Event Store / RLS migration)."
    )


async def assert_cross_workspace_query_empty(session, workspace_a: UUID, workspace_b: UUID, query) -> None:
    """Run `query` under workspace A, then under B; assert isolation.

    Helper used by `test_rls__cross_workspace_query__returns_empty`.

    Iter 2 implements this once `workspaces` exists. Stub raises.
    """
    raise NotImplementedError(
        "assert_cross_workspace_query_empty lands with Iter 2 (RLS migration)."
    )
