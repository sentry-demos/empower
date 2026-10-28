#!/bin/bash
# Start a self-heal run by hand, the same way the receiver does on a Sentry alert:
# push a selfheal/run/<id> branch that adds .selfheal/alert.json on top of selfheal/base.
# The push starts selfheal-runner from that branch; the runner deletes the branch when done.
#
#   selfheal/scripts/trigger.sh ["Alert title"] [sentry-issue-id] [with-seer|without-seer]
#
# With no version, the run uses SELFHEAL_VARIANTS (both side by side, or the repo's choice).
#
# Needs push access to the remote (SELFHEAL_REMOTE, default origin = sentry-demos/empower).
set -euo pipefail

TITLE=${1:-"Critical: Checkout revenue dropped"}
ISSUE_ID=${2:-}
VARIANT=${3:-}
case "$VARIANT" in ""|with-seer|without-seer) ;; *) echo "version must be with-seer or without-seer" >&2; exit 2 ;; esac
REMOTE=${SELFHEAL_REMOTE:-origin}
BASE=selfheal/base
branch="selfheal/run/${VARIANT:+$VARIANT/}$(date -u +%Y%m%d-%H%M%S)"

cd "$(git rev-parse --show-toplevel)"
git fetch -q "$REMOTE" "$BASE"

tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp" 2>/dev/null || true' EXIT
git worktree add -q --detach "$tmp" "$REMOTE/$BASE"
mkdir -p "$tmp/.selfheal"
python3 - "$TITLE" "$ISSUE_ID" "$VARIANT" > "$tmp/.selfheal/alert.json" <<'EOF'
import json, sys
title, issue_id, variant = sys.argv[1], sys.argv[2], sys.argv[3]
print(json.dumps({"kind": "manual", "title": title, "description": "Triggered with selfheal/scripts/trigger.sh",
                  "url": "", "issue_id": issue_id, "variant": variant}, indent=2))
EOF
git -C "$tmp" add .selfheal/alert.json
git -C "$tmp" commit -q -m "Self-heal run: $TITLE"
git -C "$tmp" push -q "$REMOTE" "HEAD:refs/heads/$branch"

echo "Pushed $branch. Waiting for the run to start..."
# Look the run up by branch through the API: plain `gh run list` 404s in this repo
repo=$(gh repo view "$(git remote get-url "$REMOTE")" --json nameWithOwner --jq .nameWithOwner)
for _ in $(seq 20); do
  run=$(gh api "repos/$repo/actions/runs?branch=$branch" --jq '.workflow_runs[0].id // empty')
  if [ -n "$run" ]; then
    echo "Run $run started:"
    echo "  gh run watch $run --repo $repo              # step status"
    echo "  gh run view $run --repo $repo --web         # live agent output: fix job -> \"Agent diagnoses and fixes\""
    exit 0
  fi
  sleep 3
done
echo "No run yet for $branch. Check Actions: https://github.com/$repo/actions/workflows/selfheal-runner.yml"
