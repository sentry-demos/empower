#!/bin/bash
# (Re)build selfheal/agent-base: the shopping-agent code from a PR (default: Kunal's #1692,
# kunalsentry:agent-order-stock-scenarios) plus the self-heal harness from selfheal/base.
#
# Agent PRs for the `agent-context` target (team-se) are opened against this branch, so the
# PR and its fork are never touched. Re-run this when the PR or the harness changes, then push:
#
#   selfheal/scripts/refresh-agent-base.sh
#   git push --force origin selfheal/agent-base
#
# Builds from the local selfheal/base, so unpushed harness changes are included.
set -euo pipefail

PR=${AGENT_PR:-1692}
REMOTE=${SELFHEAL_REMOTE:-origin}
HARNESS_BRANCH=${HARNESS_BRANCH:-selfheal/base}
TARGET=selfheal/agent-base
HARNESS_PATHS="selfheal .github/workflows/selfheal-runner.yml .github/actions/selfheal-claude AGENTS.md"

cd "$(git rev-parse --show-toplevel)"
git fetch -q "$REMOTE" "pull/$PR/head"
pr_sha=$(git rev-parse FETCH_HEAD)
harness_sha=$(git rev-parse --verify "$HARNESS_BRANCH")

tmp=$(mktemp -d)
trap 'git worktree remove --force "$tmp" 2>/dev/null || true' EXIT
git worktree add -q --detach "$tmp" "$pr_sha"
# shellcheck disable=SC2086
git -C "$tmp" checkout "$harness_sha" -- $HARNESS_PATHS
# Keep the PR's .gitignore; add what the harness needs ignored
if ! grep -qxF 'gha-creds-*.json' "$tmp/.gitignore"; then
  printf '\n# self-heal harness\ngha-creds-*.json\nselfheal/receiver/targets.json\n' >> "$tmp/.gitignore"
fi
git -C "$tmp" add -A
git -C "$tmp" commit -q -m "Self-heal harness on top of PR #$PR" \
  -m "Agent code: pull/$PR/head at ${pr_sha:0:12}. Harness: $HARNESS_BRANCH at ${harness_sha:0:12}."
git branch -f "$TARGET" "$(git -C "$tmp" rev-parse HEAD)"

echo "Built $TARGET locally: PR #$PR (${pr_sha:0:8}) + harness (${harness_sha:0:8})."
echo "Push it with:  git push --force $REMOTE $TARGET"
