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
