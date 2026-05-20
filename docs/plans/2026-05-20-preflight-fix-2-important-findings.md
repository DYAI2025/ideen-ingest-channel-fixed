# Preflight-Fix-2: Resolve Important Findings I1–I4 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close the four Important findings raised by `/code-review-excellence` on the merged Pre-Iter-0 state (PRs #5/#6/#7): tighten the diff-cover exclusion, split the coupled CI unit job, add machine-enforced reviewer-chain attestation, and replace the test-file masking flag with a misplaced-test guard.

**Architecture:** All changes touch `.github/workflows/ci-fast.yml`, `docs/adr/ADR-016*.md`, and one new shell helper. No production code changes. No new runtime dependencies. The plan is one branch (`chore/preflight-fix-2`) with one PR (`#?`) against `main`, following the same reviewer-chain that Iter 0 will start using.

**Tech Stack:** GitHub Actions, bash, gh CLI, uv, npm, pytest, vitest.

**Reference:**
- Source of findings: code-review-excellence pass (this session, after PR #7 merge).
- Reviewer process: `docs/IMPLEMENTATION_PLAN_TDD.md` §2.5.
- Governance: `docs/adr/ADR-016-governance-waiver-preflight-no-review.md`.
- Sunset tracker: GitHub issue #8.

---

## Pre-flight checks

### Task 0: Verify clean main checkout

**Step 1: Pull main**

Run: `git checkout main && git pull origin main`
Expected: `Bereits aktuell.` or fast-forward to `7844f4a` (PR #7 merge commit).

**Step 2: Verify ci-fast.yml current state**

Run: `git log --oneline -1 .github/workflows/ci-fast.yml`
Expected: commit `cc77ca6` (the `--passWithNoTests` fix from PR #7).

**Step 3: Create work branch**

Run: `git checkout -b chore/preflight-fix-2`
Expected: `Zu neuem Branch 'chore/preflight-fix-2' gewechselt`.

**No commit yet.** Branch is empty.

---

## I1: Replace glob `--exclude` with explicit per-file list

Findings: glob `'*src/api*' '*src/services*'` matches future files, undermining the sunset clause.

### Task 1: List the files actually touched by the format-pass

**Files:**
- Read: result of `git log --format=%H format(backend)` to locate commit `8895e6b`.

**Step 1: Enumerate files reformatted by the black format-pass**

Run:
```
git diff --name-only 8895e6b^..8895e6b | grep -E '^backend/src/(api|services)/' | sort
```
Expected: 11 files (or however many the format-pass touched). Capture the list.

**Step 2: Sanity-check the count matches the commit message**

Run: `git show --stat 8895e6b -- 'backend/src/**' | tail -3`
Expected: 20 files (= src + tests). Grep narrows to src/api+src/services subset (~11).

**No commit yet.** This is a discovery step; the list goes into Task 2.

### Task 2: Replace glob with explicit file list

**Files:**
- Modify: `.github/workflows/ci-fast.yml:159-162` (the `diff-cover` invocation).

**Step 1: Update the workflow**

Replace the existing block:

```yaml
          uv tool run diff-cover coverage.xml \
            --compare-branch=origin/main \
            --fail-under=80 \
            --exclude '*src/api*' '*src/services*'
```

With:

```yaml
          uv tool run diff-cover coverage.xml \
            --compare-branch=origin/main \
            --fail-under=80 \
            --exclude \
              backend/src/api/agents.py \
              backend/src/api/graph.py \
              backend/src/api/ideas.py \
              backend/src/api/ingest.py \
              backend/src/api/kanban.py \
              backend/src/api/semantic.py \
              backend/src/api/status.py \
              backend/src/services/file_watcher.py \
              backend/src/services/gbrain_service.py \
              backend/src/services/kanban_sync.py \
              backend/src/services/semantic_analysis.py
```

(Adjust the list to whatever Task 1 enumerated.)

**Step 2: Update the surrounding comment block**

Replace the comment lines that describe the exclude rationale to match:

```yaml
          # `--exclude` lists the 11 files touched by the PR-#7 black
          # format-pass that ship without test coverage. Any other file
          # under src/api or src/services is intentionally NOT excluded,
          # so new files in Iter 0+ get the full 80% diff-cover gate.
          #
          # Sunset tracking: GitHub issue #8. The first Iter-0 PR closes
          # the issue by deleting these --exclude lines (or replacing
          # them with real coverage). No silent forgetting.
```

**Step 3: Local rehearsal**

Run (from `backend/`):
```
uv sync --dev
uv run pytest -m "not slow and not e2e and not stress and not fuzz and not load" --cov=src --cov-report=xml -p no:randomly tests/
uv tool install diff-cover
uv tool run diff-cover coverage.xml --compare-branch=origin/main --fail-under=80 \
  --exclude backend/src/api/agents.py backend/src/api/graph.py backend/src/api/ideas.py backend/src/api/ingest.py backend/src/api/kanban.py backend/src/api/semantic.py backend/src/api/status.py backend/src/services/file_watcher.py backend/src/services/gbrain_service.py backend/src/services/kanban_sync.py backend/src/services/semantic_analysis.py
```
Expected: diff-cover exits 0; no missing-lines report.

**Step 4: Negative test (manual, no commit yet)**

Add a deliberate untested line to `backend/src/services/file_watcher.py` (e.g., `print("trap")`). Re-run the pytest + diff-cover commands.
Expected: diff-cover STILL ignores it (file is on the exclude list — that's correct for this PR but Iter 0 will fail).

Revert the test edit: `git checkout backend/src/services/file_watcher.py`.

**Step 5: Add a fresh untested file and re-test (still no commit)**

Create `backend/src/services/_smoke_canary.py` with one new function:

```python
def canary():
    return "untested"
```

Run the same pytest + diff-cover commands.
Expected: diff-cover FAILS — the new file is NOT on the exclude list, so its lines must be covered. Confirms the glob change actually closes the loophole.

Delete the canary: `rm backend/src/services/_smoke_canary.py`.

**Step 6: Commit**

```
git add .github/workflows/ci-fast.yml
git commit -m "fix(ci): replace diff-cover glob exclude with explicit file list

Code-review finding I1: the glob '*src/api*' '*src/services*' would
silently swallow future files added under those directories
(Iter 2 ships backend/src/services/events/, etc.). Replace with a
literal list of the 11 files actually touched by the PR-#7 format-pass.

Verified: a fresh canary file under backend/src/services/ now fails
diff-cover until tested. Closes the loophole that issue #8 calls out."
```

---

## I2: Split CI `unit` job into parallel backend + frontend jobs

Finding: backend pytest failure short-circuits the frontend job; signals get coupled.

### Task 3: Read current `unit` job structure

**Files:**
- Read: `.github/workflows/ci-fast.yml:50-79` (the existing `unit` job).

**Step 1: Confirm what to split**

Run: `sed -n '50,80p' .github/workflows/ci-fast.yml`
Expected: one `unit` job containing both `uv sync + pytest` and `npm ci + npm test`.

**No commit yet.** Read-only.

### Task 4: Replace `unit` with two parallel jobs

**Files:**
- Modify: `.github/workflows/ci-fast.yml:50-79`.

**Step 1: Replace the `unit` job block with two independent jobs**

Replace:

```yaml
  unit:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
      - name: backend unit
        working-directory: backend
        run: |
          uv sync --dev
          uv run pytest -m "not slow and not e2e and not stress and not fuzz and not load" \
            --cov=src --cov-report=xml -p no:randomly tests/
      - uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: backend/coverage.xml
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: frontend unit
        working-directory: frontend
        run: |
          npm ci
          # `--passWithNoTests` accommodates the preflight state...
          npm test -- --passWithNoTests
```

With:

```yaml
  unit-backend:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v8.1.0
        with:
          enable-cache: true
      - name: backend unit
        working-directory: backend
        run: |
          uv sync --dev
          uv run pytest -m "not slow and not e2e and not stress and not fuzz and not load" \
            --cov=src --cov-report=xml -p no:randomly tests/
      - uses: actions/upload-artifact@v4
        with:
          name: backend-coverage
          path: backend/coverage.xml

  unit-frontend:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: misplaced-test guard
        working-directory: frontend
        run: |
          # I4 fix: vitest's --passWithNoTests would otherwise silently
          # accept misplaced specs. Fail explicitly if any *.test.ts(x)
          # lives outside tests/.
          stray=$(git ls-files 'src/**/*.test.ts' 'src/**/*.test.tsx' 'src/**/*.spec.ts' 'src/**/*.spec.tsx' || true)
          if [ -n "$stray" ]; then
            echo "::error::Test files found under frontend/src/ - move them to frontend/tests/{unit,integration}/:"
            echo "$stray"
            exit 1
          fi
      - name: frontend unit
        working-directory: frontend
        run: |
          npm ci
          npm test -- --passWithNoTests
```

**Step 2: Update the `needs` reference in `diff-coverage`**

Find:
```yaml
  diff-coverage:
    runs-on: ubuntu-22.04
    needs: [unit]
```

Replace with:
```yaml
  diff-coverage:
    runs-on: ubuntu-22.04
    needs: [unit-backend]
```

**Step 3: Local lint of YAML**

Run: `python3 -c 'import yaml; yaml.safe_load(open(".github/workflows/ci-fast.yml"))'`
Expected: no output (parse OK).

Note: per CLAUDE.md, prefer `uv run python3` if a hook blocks bare python3. If blocked, run: `uv --project backend run python -c 'import yaml; yaml.safe_load(open(".github/workflows/ci-fast.yml"))'`.

**Step 4: Commit**

```
git add .github/workflows/ci-fast.yml
git commit -m "fix(ci): split unit job into parallel unit-backend + unit-frontend

Code-review finding I2: the original single 'unit' job ran backend
pytest first; failure short-circuited the frontend step, so a broken
backend silently masked any frontend regression in the same PR.

Now: two independent jobs run in parallel. Backend coverage upload
moves with unit-backend; diff-coverage's needs list updates to
unit-backend. Total CI wallclock drops too, since the jobs no longer
serialize on the Node setup."
```

---

## I3: Reviewer-chain attestation as ci-fast gate

Finding: ADR-016 enforces reviewer-chain by social pressure only. Add machine check.

### Task 5: Write the attestation script

**Files:**
- Create: `scripts/check_reviewer_chain.sh`.

**Step 1: Create the script**

Write `scripts/check_reviewer_chain.sh`:

```bash
#!/usr/bin/env bash
# Verifies that the PR body or an explicit comment contains the
# Reviewer-Chain Findings-Disposition table required by plan §2.5
# and ADR-016. Run from CI on pull_request events.
#
# Inputs (env, set by GitHub Actions):
#   GH_TOKEN          - read access to PRs in this repo
#   GITHUB_REPOSITORY - owner/repo
#   PR_NUMBER         - the PR number under review
#
# Exit codes:
#   0 - disposition table found
#   1 - missing; merge must be blocked

set -euo pipefail

: "${GH_TOKEN:?GH_TOKEN required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY required}"
: "${PR_NUMBER:?PR_NUMBER required}"

needle="Reviewer-Chain Findings-Disposition"

body=$(gh pr view "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" --json body --jq .body)
if grep -q "$needle" <<<"$body"; then
  echo "Disposition table found in PR body."
  exit 0
fi

comments=$(gh pr view "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" --json comments --jq '.comments[].body')
if grep -q "$needle" <<<"$comments"; then
  echo "Disposition table found in PR comments."
  exit 0
fi

cat <<'MSG' >&2
::error::Reviewer-Chain Findings-Disposition table missing.

Plan §2.5 (docs/IMPLEMENTATION_PLAN_TDD.md) requires three reviewer
passes for every Iter PR. Their findings live in a table headed
"Reviewer-Chain Findings-Disposition" inside either the PR description
or an explicit comment.

To unblock this gate:
  1. Run /code-review-excellence (Subagent-Pass).
  2. Run /code-review-checklist (Bot-Pass).
  3. Post a comment with the disposition table covering both passes
     plus the human reviewer status.

See ADR-016 for governance context.
MSG
exit 1
```

**Step 2: Make executable**

Run: `chmod +x scripts/check_reviewer_chain.sh`

**Step 3: Smoke-test the script against an already-merged PR**

Run:
```
GH_TOKEN=$(gh auth token) GITHUB_REPOSITORY=DYAI2025/ideen-ingest-channel-fixed PR_NUMBER=7 \
  scripts/check_reviewer_chain.sh
```
Expected: `Disposition table found in PR comments.` exit 0. PR #7 has the table I posted earlier.

**Step 4: Negative test against a PR without the table**

Run:
```
GH_TOKEN=$(gh auth token) GITHUB_REPOSITORY=DYAI2025/ideen-ingest-channel-fixed PR_NUMBER=4 \
  scripts/check_reviewer_chain.sh
```
Expected: `::error::Reviewer-Chain Findings-Disposition table missing.` exit 1.

**Step 5: Commit**

```
git add scripts/check_reviewer_chain.sh
git commit -m "feat(ci): add reviewer-chain attestation script

Script reads the PR body + comments via gh CLI and exits non-zero if
no 'Reviewer-Chain Findings-Disposition' header is found. Turns plan
§2.5 from convention into machine-enforced gate.

Verified locally against PR #7 (passes - table in comments) and PR #4
(fails - no table). Next commit wires the script into ci-fast."
```

### Task 6: Wire script into ci-fast as new job

**Files:**
- Modify: `.github/workflows/ci-fast.yml` (append new job).

**Step 1: Add the job after `diff-coverage`**

Insert at end of the `jobs:` block:

```yaml
  reviewer-chain-attestation:
    runs-on: ubuntu-22.04
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - name: verify reviewer-chain disposition table present
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
        run: ./scripts/check_reviewer_chain.sh
```

**Step 2: YAML parse-check**

Run: `python3 -c 'import yaml; yaml.safe_load(open(".github/workflows/ci-fast.yml"))'` (or the uv variant).
Expected: no output.

**Step 3: Commit**

```
git add .github/workflows/ci-fast.yml
git commit -m "feat(ci): gate ci-fast on reviewer-chain attestation

Code-review finding I3: ADR-016 makes the reviewer-chain mandatory
from Iter 0 onward, but enforcement was 'convention'. Anyone could
skip the chain on Iter-0 PRs.

New job 'reviewer-chain-attestation' runs scripts/check_reviewer_chain.sh
on every pull_request event. Job fails if the PR body and comments
contain no 'Reviewer-Chain Findings-Disposition' header.

The check is intentionally lenient (matches header text anywhere) so
that the reviewer chooses where to place the table; only its presence
is enforced."
```

---

## I4: Replace `--passWithNoTests` with misplaced-test guard

Finding: vitest silence after misplaced spec.

### Task 7: Confirm Task 4 already added the guard

The guard step `misplaced-test guard` was introduced in the I2 fix (Task 4) as part of the new `unit-frontend` job. Confirm here that it covers the I4 concern.

**Files:**
- Read: `.github/workflows/ci-fast.yml` — find the `misplaced-test guard` step.

**Step 1: Verify the guard step exists**

Run: `grep -A 9 "misplaced-test guard" .github/workflows/ci-fast.yml`
Expected: the guard step listed in Task 4 is present.

**Step 2: Smoke-test locally**

From `frontend/`:
```
touch src/_smoke.test.ts
stray=$(git ls-files 'src/**/*.test.ts' 'src/**/*.test.tsx' 'src/**/*.spec.ts' 'src/**/*.spec.tsx' || true)
echo "stray=$stray"
```
Expected: the freshly-created file does NOT yet appear (git ls-files only shows tracked files).

**Step 3: Track the canary and re-test**

```
git add -N src/_smoke.test.ts
stray=$(git ls-files 'src/**/*.test.ts' 'src/**/*.test.tsx' 'src/**/*.spec.ts' 'src/**/*.spec.tsx' || true)
echo "stray=$stray"
```
Expected: now `stray=src/_smoke.test.ts`. The CI step would fail.

**Step 4: Clean up**

```
git reset HEAD frontend/src/_smoke.test.ts
rm frontend/src/_smoke.test.ts
```

**Step 5: No commit needed.** Guard already shipped in Task 4's commit.

---

## CHANGELOG + PR

### Task 8: Add CHANGELOG entry

**Files:**
- Modify: `CHANGELOG.md`.

**Step 1: Open the file and locate the existing Preflight-Fix block**

Run: `grep -n "Preflight-Fix" CHANGELOG.md`
Expected: one match around line 26.

**Step 2: Append a Preflight-Fix-2 sub-block**

Add immediately after the existing Preflight-Fix bullets:

```markdown
- **Preflight-Fix-2 (chore/preflight-fix-2):**
  - `.github/workflows/ci-fast.yml`: `unit` job aufgeteilt in `unit-backend` + `unit-frontend` (parallel statt seriell), neue `reviewer-chain-attestation`-Job blockt Merge ohne Disposition-Tabelle, `misplaced-test guard` fängt Test-Dateien unter `frontend/src/` ab, `diff-cover --exclude` ersetzt durch explizite 11-Datei-Liste statt Glob.
  - `scripts/check_reviewer_chain.sh`: macht Plan §2.5 von Konvention zu Gate.
```

**Step 3: Commit**

```
git add CHANGELOG.md
git commit -m "docs(changelog): add preflight-fix-2 entry"
```

### Task 9: Push branch

**Step 1: Push**

Run: `git push -u origin chore/preflight-fix-2`
Expected: branch created on origin, PR URL printed.

**No commit.** Networking only.

### Task 10: Open PR with disposition placeholder

**Step 1: Open PR**

Run:

```
gh pr create --base main --head chore/preflight-fix-2 \
  --title "chore: preflight-fix-2 - resolve code-review Important findings I1-I4" \
  --body "$(cat <<'EOF'
## Summary

Closes the four Important findings raised by /code-review-excellence on the merged Pre-Iter-0 state:

- **I1.** diff-cover glob exclude → explicit 11-file list. Future src files now caught by the gate.
- **I2.** unit job split into parallel unit-backend + unit-frontend. Coupled failure domains decoupled.
- **I3.** reviewer-chain-attestation job added. ADR-016 §2.5 now machine-enforced.
- **I4.** --passWithNoTests stays, but new misplaced-test guard fails if any *.test.ts(x) lives under frontend/src/.

## Reviewer-Chain Findings-Disposition

| Pass | Status | Notes |
|---|---|---|
| /code-review-excellence Subagent | TODO | will append after running |
| /code-review-checklist Bot | TODO | will append after running |
| Human review | TODO | requesting explicit approval |

## Test plan

- [ ] ci-fast green: lint, unit-backend, unit-frontend, integration-fast, contract-snapshot, diff-coverage, reviewer-chain-attestation all pass.
- [ ] Manual trigger: simulate a missing disposition (push commit without table) - reviewer-chain-attestation fails; revert.
- [ ] Manual trigger: simulate a misplaced test - misplaced-test guard fails; revert.

Reference: docs/IMPLEMENTATION_PLAN_TDD.md §2.4 §2.5; docs/adr/ADR-016*; issue #8 (independent tracker; still valid).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```
Expected: PR URL printed.

**No commit.**

### Task 11: Wait for ci-fast green

**Step 1: Watch the checks**

Run:
```
until s=$(gh pr checks <PR_NUMBER> --json name,bucket 2>/dev/null) && \
  jq -e 'length > 1 and all(.bucket != "pending")' <<<"$s" >/dev/null; do
    sleep 20
done
gh pr checks <PR_NUMBER>
```
Expected: all of `lint`, `unit-backend`, `unit-frontend`, `integration-fast`, `contract-snapshot`, `diff-coverage` show `pass`. `reviewer-chain-attestation` likely **fails** initially because the disposition table in the PR body is still `TODO`.

**No commit.**

### Task 12: Run reviewer-chain on this PR

**Step 1: Invoke /code-review-excellence (Subagent-Pass)**

Either via the `code-review-reviewer` or `caveman:cavecrew-reviewer` subagent (whichever responds — 529-overload fallback documented in PR #7 disposition).
Output: findings + dispositions for any new issues introduced by this PR.

**Step 2: Invoke /code-review-checklist (Bot-Pass)**

Run inline as a self-checklist using `docs/PR-quality-checklist.md` Protocol-grade track. Same approach as PR #7.

**Step 3: Update PR description with real disposition table**

Run: `gh pr edit <PR_NUMBER> --body "$(cat new_body.txt)"` with the real table.
Expected: `reviewer-chain-attestation` re-runs and passes on the next push or check re-run.

**Step 4: Trigger CI re-run if needed**

Run: `gh pr comment <PR_NUMBER> --body "/recheck"` or empty commit + push to re-trigger.

**No commit unless empty re-run commit needed.**

### Task 13: Await human OK + merge

**Step 1: Request human review explicitly**

Run: `gh pr ready <PR_NUMBER>` (if it was draft) and ping reviewer.

**Step 2: After human OK, merge**

Run: `gh pr merge <PR_NUMBER> --squash --delete-branch=false`
Expected: PR shows MERGED, main advances.

**No final commit — squash-merge is the artifact.**

---

## Final Sanity Pass

### Task 14: Verify main state

**Step 1: Sync and inspect**

Run: `git checkout main && git pull origin main`
Expected: `chore: preflight-fix-2 - resolve code-review Important findings I1-I4` is the latest commit.

**Step 2: Run the full local rehearsal one more time**

From `backend/`:
```
uv sync --dev
uv run pytest -m "not slow and not e2e and not stress and not fuzz and not load" --cov=src --cov-report=xml -p no:randomly tests/
```
Expected: 4 passed, 2 skipped (unchanged baseline).

From `frontend/`:
```
npm ci
npm run lint
npx tsc --noEmit
npm test -- --passWithNoTests
```
Expected: lint 0 errors (warnings tolerated), tsc clean, vitest "No test files found, exiting with code 0".

**Step 3: Run the attestation script against the freshly-merged PR**

Run: `scripts/check_reviewer_chain.sh` with the merged PR number.
Expected: `Disposition table found...`.

**No commit. Plan complete.**

---

## What this plan does NOT touch (explicit non-goals)

- The Minor findings (M1–M6) from the code review — defer to a separate PR if at all.
- Issue #8's underlying problem (the format-pass-without-coverage). This plan tightens the *enforcement* mechanism but does not add tests for `backend/src/api/*` or `backend/src/services/*` — that is Iter 0's work.
- ADR-016 itself does not change. Its convention-only enforcement language is now backed by `reviewer-chain-attestation`; updating the ADR text is optional and can wait for Iter 10's branch-protection pass.
- The plan does not introduce branch protection on `main`. That waits for Iter 10 per ADR-016.

---

## Definition of Done

- All 14 tasks completed with their commits or no-commit-needed markers checked.
- `chore/preflight-fix-2` merged on `main`.
- ci-fast on a fresh PR shows 7 jobs (lint, unit-backend, unit-frontend, integration-fast, contract-snapshot, diff-coverage, reviewer-chain-attestation) all green.
- `scripts/check_reviewer_chain.sh` exit-1 on a real PR without a disposition table (verified during Task 5).
- CHANGELOG.md mentions Preflight-Fix-2 alongside Preflight-Fix.
