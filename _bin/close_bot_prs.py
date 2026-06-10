#!python3
"""Close stale pull requests opened by bot accounts.

Closes open PRs older than a given age (default 1 hour) that were created by the
specified authors, unless the PR carries an excluded label. Intended to run on a
schedule to keep automated/bot PRs from piling up.
"""
import argparse
import http.client
import json
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta

GITHUB_API_BASE = "https://api.github.com"


def github_request(method, path, auth_token, body=None):
    url = f"{GITHUB_API_BASE}{path}"
    parsed_url = urlparse(url)
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "close-bot-prs-script",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"

    conn = http.client.HTTPSConnection(parsed_url.netloc)
    full_path = parsed_url.path + ("?" + parsed_url.query if parsed_url.query else "")
    conn.request(method, full_path, body=json.dumps(body) if body is not None else None, headers=headers)
    response = conn.getresponse()
    payload = response.read().decode()
    return response, payload


def get_open_pulls(repo, auth_token):
    pulls = []
    path = f"/repos/{repo}/pulls?state=open&per_page=100"

    while path:
        response, payload = github_request("GET", path, auth_token)
        if response.status != 200:
            raise Exception(f"Failed to fetch pull requests: {payload}")

        pulls.extend(json.loads(payload))

        # Handle pagination via the Link header.
        link_header = response.getheader("Link", "")
        next_path = None
        for link in link_header.split(","):
            parts = link.split(";")
            if len(parts) < 2:
                continue
            url_part = parts[0].strip()[1:-1]
            rel_part = parts[1].strip()
            if rel_part == 'rel="next"':
                parsed = urlparse(url_part)
                next_path = parsed.path + ("?" + parsed.query if parsed.query else "")
                break

        path = next_path

    return pulls


def close_pull(repo, number, auth_token, dry_run):
    if dry_run:
        print(f"[Dry Run] Would close PR #{number}")
        return

    response, payload = github_request(
        "PATCH", f"/repos/{repo}/pulls/{number}", auth_token, body={"state": "closed"}
    )
    if response.status == 200:
        print(f"Closed PR #{number}")
    else:
        print(f"Failed to close PR #{number}: {payload}")


def get_pull_age(created_at):
    created_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    return datetime.now(timezone.utc) - created_date


def main():
    parser = argparse.ArgumentParser(
        description="Close stale bot-authored pull requests, except those with an excluded label."
    )
    parser.add_argument("repo", help="Repository in 'owner/name' form, e.g. sentry-demos/empower")
    parser.add_argument("auth_token", help="GitHub API token with pull-requests write access")
    parser.add_argument(
        "--authors",
        nargs="+",
        default=["cursor[bot]", "sentry"],
        help="PR author logins to target (default: cursor[bot] sentry)",
    )
    parser.add_argument(
        "--exclude-label",
        default="example",
        help="PRs carrying this label are never closed (default: example)",
    )
    parser.add_argument(
        "--min-age-minutes",
        type=int,
        default=60,
        help="Only close PRs older than this many minutes (default: 60)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be closed without actually closing",
    )

    args = parser.parse_args()

    min_age = timedelta(minutes=args.min_age_minutes)
    authors = set(args.authors)

    print("=== close_bot_prs configuration ===")
    print(f"  repo:          {args.repo}")
    print(f"  authors:       {sorted(authors)}")
    print(f"  exclude-label: {args.exclude_label!r}")
    print(f"  min-age:       {args.min_age_minutes} min")
    print(f"  dry-run:       {args.dry_run}")
    print("===================================")

    pulls = get_open_pulls(args.repo, args.auth_token)
    print(f"Fetched {len(pulls)} open pull request(s)")

    count_closed = 0
    count_skipped = 0
    for pull in pulls:
        number = pull["number"]
        author = pull["user"]["login"]
        labels = {label["name"] for label in pull.get("labels", [])}
        age = get_pull_age(pull["created_at"])
        age_min = int(age.total_seconds() // 60)

        print(
            f"PR #{number}: author={author!r} created_at={pull['created_at']} "
            f"age={age_min}min labels={sorted(labels)}"
        )

        if author not in authors:
            count_skipped += 1
            print(f"  -> skip: author {author!r} not in target authors")
            continue

        if args.exclude_label in labels:
            count_skipped += 1
            print(f"  -> skip: has excluded label {args.exclude_label!r}")
            continue

        if age < min_age:
            count_skipped += 1
            print(f"  -> skip: only {age_min}min old (< {args.min_age_minutes}min)")
            continue

        print(f"  -> close: matches author, no excluded label, {age_min}min old")
        close_pull(args.repo, number, args.auth_token, args.dry_run)
        count_closed += 1

    print(f"{'Would have closed' if args.dry_run else 'Closed'} {count_closed} pull requests")
    print(f"Skipped {count_skipped} pull requests")


if __name__ == "__main__":
    main()
