#!/bin/bash
# Make sure the /checkout bug is on selfheal/base and deployed.
#
# If a previous demo merged a fix, restore the buggy files from the `selfheal-armed` tag
# through a PR (selfheal/base is protected) and merge it with admin bypass. The merge
# triggers selfheal-deploy. With SELFHEAL_FLASK_URL set, waits until the deployed
# service returns 500 for a real checkout.
set -euo pipefail

REPO=${SELFHEAL_REPO:-sentry-demos/empower}
BASE=selfheal/base
TAG=selfheal-armed
BUGGY_FILES="flask/src/main.py flask/src/test/test_checkout.py"

top=$(git rev-parse --show-toplevel)
cd "$top"
git fetch -q origin "$BASE" "refs/tags/$TAG:refs/tags/$TAG"

bug_present() {
  # The bug: `quantities` is read (len check) before it's assigned
  git show "origin/$BASE:flask/src/main.py" | awk '
    /if len\(quantities\) == 0/ && !assigned { found = 1 }
    /quantities = \{int\(k\)/ { assigned = 1 }
    END { exit found ? 0 : 1 }'
}

if bug_present; then
  echo "✓ The bug is already on $BASE"
else
  branch="selfheal/rearm-$(date +%Y%m%d-%H%M%S)"
  tmp=$(mktemp -d)
  git worktree add -q -b "$branch" "$tmp" "origin/$BASE"
  # shellcheck disable=SC2086
  git -C "$tmp" checkout "$TAG" -- $BUGGY_FILES
  git -C "$tmp" commit -q -m "Re-arm self-heal demo: restore the /checkout bug"
  git -C "$tmp" push -q origin "$branch"
  git worktree remove --force "$tmp"

  url=$(gh pr create --repo "$REPO" --base "$BASE" --head "$branch" \
    --title "Re-arm self-heal demo" \
    --body "Restores \`$BUGGY_FILES\` from the \`$TAG\` tag so the next demo starts broken. Opened by selfheal/scripts/arm.sh.")
  echo "Opened $url"
  if gh pr merge "$url" --admin --squash --delete-branch; then
    echo "✓ Merged. selfheal-deploy is deploying the bug."
  else
    echo "✗ Couldn't merge with admin bypass. Approve and merge $url, then re-run this script."
    exit 1
  fi
fi

if [ -z "${SELFHEAL_FLASK_URL:-}" ]; then
  echo "Set SELFHEAL_FLASK_URL to wait for the deployed service to return the 500."
  exit 0
fi

echo "Waiting for $SELFHEAL_FLASK_URL to fail checkout (up to 15 min while the deploy runs)..."
order='{"cart":{"items":[{"id":3,"title":"Plant Mood","price":155}],"quantities":{"3":1},"total":155},"form":{"email":"arm@example.com"},"validate_inventory":"true"}'
for _ in $(seq 30); do
  status=$(curl -s -o /dev/null -w '%{http_code}' -X POST -H 'Content-Type: application/json' -H 'se: selfheal-arm' \
    --data "$order" "${SELFHEAL_FLASK_URL%/}/checkout")
  if [ "$status" = "500" ]; then
    echo "✓ Armed: /checkout returns 500"
    exit 0
  fi
  echo "  /checkout -> $status, retrying in 30s"
  sleep 30
done
echo "✗ Still not failing after 15 min. Check the selfheal-deploy run."
exit 1
