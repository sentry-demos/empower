#!/bin/bash
# Start a self-heal run by hand, the same way the receiver does on a Sentry alert:
# push a selfheal/run/<id> branch that adds .selfheal/alert.json on top of selfheal/base.
# The push starts selfheal-runner from that branch; the runner deletes the branch when done.
#
#   selfheal/scripts/trigger.sh ["Alert title"] [sentry-issue-id]
#
# Needs push access to the remote (SELFHEAL_REMOTE, default origin = sentry-demos/empower).
set -euo pipefail

TITLE=${1:-"Critical: Checkout revenue dropped"}
ISSUE_ID=${2:-}
REMOTE=${SELFHEAL_REMOTE:-origin}
BASE=selfheal/base
branch="selfheal/run/$(date -u +%Y%m%d-%H%M%S)"

cd "$(git rev-parse --show-toplevel)"
git fetch -q "$REMOTE" "$BASE"

tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp" 2>/dev/null || true' EXIT
git worktree add -q --detach "$tmp" "$REMOTE/$BASE"
mkdir -p "$tmp/.selfheal"
python3 - "$TITLE" "$ISSUE_ID" > "$tmp/.selfheal/alert.json" <<'EOF'
import json, sys
title, issue_id = sys.argv[1], sys.argv[2]
print(json.dumps({"kind": "manual", "title": title, "description": "Triggered with selfheal/scripts/trigger.sh",
                  "url": "", "issue_id": issue_id}, indent=2))
EOF
git -C "$tmp" add .selfheal/alert.json
git -C "$tmp" commit -q -m "Self-heal run: $TITLE"
git -C "$tmp" push -q "$REMOTE" "HEAD:refs/heads/$branch"

echo "Pushed $branch. Watch it with:"
echo "  gh run list --workflow selfheal-runner.yml --branch $branch"
