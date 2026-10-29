#!/bin/bash
# Start a self-heal run by hand, the same way the receiver does on a Sentry alert:
# push a selfheal/run/<id> branch that adds .selfheal/alert.json on top of the target's base
# branch. The push starts selfheal-runner from that branch; the runner deletes it when done.
#
#   selfheal/scripts/trigger.sh ["Alert title"] [sentry-issue-id] [with-seer|without-seer]
#   SELFHEAL_TARGET=agent-context selfheal/scripts/trigger.sh "Kunal LLM Context Snowball" 7813412119
#
# With no version, the run uses SELFHEAL_VARIANTS (both side by side, or the repo's choice).
#
# SELFHEAL_TARGET picks a target from selfheal/targets.json (default: checkout, the demo org).
# Needs push access to the remote (SELFHEAL_REMOTE, default origin = sentry-demos/empower).
set -euo pipefail

TARGET=${SELFHEAL_TARGET:-checkout}
TITLE=${1:-"Critical: Checkout revenue dropped"}
ISSUE_ID=${2:-}
VARIANT=${3:-}
case "$VARIANT" in ""|with-seer|without-seer) ;; *) echo "version must be with-seer or without-seer" >&2; exit 2 ;; esac
REMOTE=${SELFHEAL_REMOTE:-origin}
branch="selfheal/run/${VARIANT:+$VARIANT/}$(date -u +%Y%m%d-%H%M%S)"

cd "$(git rev-parse --show-toplevel)"
read -r BASE ORG < <(python3 -c "
import json, sys
t = json.load(open('selfheal/targets.json')).get(sys.argv[1])
if not t:
    sys.exit(f'Unknown target {sys.argv[1]!r}; see selfheal/targets.json')
print(t['base'], t['org'])" "$TARGET")
git fetch -q "$REMOTE" "$BASE"

tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp" 2>/dev/null || true' EXIT
git worktree add -q --detach "$tmp" "$REMOTE/$BASE"
mkdir -p "$tmp/.selfheal"
python3 - "$TITLE" "$ISSUE_ID" "$VARIANT" "$ORG" "$TARGET" > "$tmp/.selfheal/alert.json" <<'EOF'
import json, sys
title, issue_id, variant, org, target = sys.argv[1:6]
print(json.dumps({"kind": "manual", "title": title, "description": "Triggered with selfheal/scripts/trigger.sh",
                  "url": "", "issue_id": issue_id, "variant": variant, "org": org, "target": target}, indent=2))
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
