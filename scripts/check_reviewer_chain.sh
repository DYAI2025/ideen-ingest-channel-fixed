#!/usr/bin/env bash
# Verifies that the PR body, an issue comment, a review body, or a
# review-thread comment contains the Reviewer-Chain Findings-Disposition
# table required by plan §2.5 and ADR-016. Run from CI on pull_request
# events.
#
# Inputs (env, set by GitHub Actions):
#   GH_TOKEN          - read access to PRs in this repo
#   GITHUB_REPOSITORY - owner/repo
#   PR_NUMBER         - the PR number under review
#
# Exit codes:
#   0 - disposition table found
#   1 - disposition table missing; merge must be blocked
#   2 - infrastructure failure (gh network/auth/rate-limit); retry-able
#
# Local smoke test:
#   GH_TOKEN=$(gh auth token) \
#     GITHUB_REPOSITORY=DYAI2025/ideen-ingest-channel-fixed \
#     PR_NUMBER=7 ./scripts/check_reviewer_chain.sh

set -euo pipefail

: "${GH_TOKEN:?GH_TOKEN required}"
: "${GITHUB_REPOSITORY:?GITHUB_REPOSITORY required}"
: "${PR_NUMBER:?PR_NUMBER required}"

# Required heading text (exact form reviewers should paste). Matching is
# lenient: case-insensitive, and the dot-like separators are treated as
# any single non-word character, so "Reviewer Chain Findings Disposition",
# "reviewer-chain findings-disposition", "Reviewer/Chain Findings/Disposition"
# etc. all match. This avoids silent failures from minor formatting drift
# (different dash glyph, bolded heading, capitalisation).
required_heading="Reviewer-Chain Findings-Disposition"
needle_regex='Reviewer.Chain Findings.Disposition'

# C1: capture each gh call's stderr+stdout and on failure emit a distinct
# ::error:: annotation + exit 2, so observability can tell apart "infra
# broke" (auth/network/rate-limit) from "table missing".

if ! body=$(gh pr view "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" \
    --json body --jq .body 2>&1); then
  echo "::error::gh pr view body failed (network/auth/rate-limit). Output: $body" >&2
  exit 2
fi

if ! issue_comments=$(gh pr view "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" \
    --json comments --jq '.comments[].body' 2>&1); then
  echo "::error::gh pr view comments failed (network/auth/rate-limit). Output: $issue_comments" >&2
  exit 2
fi

# C2: gh pr view --json comments only returns issue comments (the
# bottom-of-page conversation). Reviewers using `gh pr review --body`
# or the web review composer produce top-level review bodies that the
# above query misses. Pull those explicitly.
if ! review_bodies=$(gh pr view "$PR_NUMBER" --repo "$GITHUB_REPOSITORY" \
    --json reviews --jq '.reviews[].body' 2>&1); then
  echo "::error::gh pr view reviews failed (network/auth/rate-limit). Output: $review_bodies" >&2
  exit 2
fi

# C2 (cont.): line-level review-thread comments live on a different
# REST endpoint and are also not returned by --json comments.
if ! review_thread_comments=$(gh api \
    "repos/${GITHUB_REPOSITORY}/pulls/${PR_NUMBER}/comments" \
    --jq '.[].body' 2>&1); then
  echo "::error::gh api review-thread comments failed (network/auth/rate-limit). Output: $review_thread_comments" >&2
  exit 2
fi

# Union of all four sources, grep'd once with the lenient regex.
union=$(printf '%s\n%s\n%s\n%s\n' \
  "$body" "$issue_comments" "$review_bodies" "$review_thread_comments")

if grep -qiE "$needle_regex" <<<"$union"; then
  echo "Disposition table found (searched body + issue comments + review bodies + review-thread comments)."
  exit 0
fi

cat >&2 <<MSG
::error::Reviewer-Chain Findings-Disposition table missing.

Plan §2.5 (docs/IMPLEMENTATION_PLAN_TDD.md) requires three reviewer
passes for every Iter PR. Their findings live in a table headed
"${required_heading}" inside the PR description, an issue comment,
a review body, or a review-thread comment. Matching is case-insensitive
and tolerates minor separator variation (different dash glyph, etc.),
but the heading text itself must be present.

To unblock this gate:
  1. Run /code-review-excellence (Subagent-Pass).
  2. Run /code-review-checklist (Bot-Pass).
  3. Post the disposition table with the heading "${required_heading}"
     covering both passes plus the human reviewer status.

  After posting the table, either push any commit (empty commit OK)
  or click 'Re-run jobs' in the Actions tab to re-evaluate.

See ADR-016 for governance context.
MSG
exit 1
