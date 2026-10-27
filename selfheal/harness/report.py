"""Post self-heal results to Slack.

    python selfheal/harness/report.py review --pr-url URL --review FILE --variant V --results DIR
        Posted once per agent PR, after the reviewer agent has commented: the notification
        that tells a human a verified fix is waiting for them. DIR holds that variant's
        stats.json, verify.json and result.json.

    python selfheal/harness/report.py started --alert alert.json --variants '["without-seer"]'
        Posted when the run starts: the agents are on it, with a link to the run.

    python selfheal/harness/report.py run --alert alert.json --results DIR
        Posted when the run ends: the side-by-side scorecard. DIR holds one sub-directory
        per variant with the files above.

Slack: SELFHEAL_SLACK_BOT_TOKEN (an existing bot's xoxb- token with chat:write) plus
SELFHEAL_SLACK_CHANNEL (channel ID), or SELFHEAL_SLACK_WEBHOOK_URL (an incoming webhook).
With neither, prints the message.

Threading: with the bot token, messages are posted as replies to Sentry's own alert message in
the channel, when one is found: the most recent message from the Sentry app within
SELFHEAL_SLACK_THREAD_HOURS (default 6) that mentions SELFHEAL_SLACK_ALERT_MATCH (default
"revenue") or the alert's title or link. Needs channels:history (groups:history for a private
channel). With no match, e.g. runs started by trigger.sh, messages go to the channel itself.
"""
import argparse
import json
import os
import time

import requests

VARIANTS = ("without-seer", "with-seer")
SLACK_API = "https://slack.com/api"


def load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def is_from_sentry(message):
    profile = message.get("bot_profile") or {}
    return "sentry" in (profile.get("name") or message.get("username") or "").lower()


def find_alert_thread(token, channel, alert, attempts=1, wait_s=15):
    """ts of Sentry's alert message to reply under, or None. Never raises: threading is a
    nicety, so any problem (missing scope, no match) falls back to a channel post.

    attempts > 1 retries a missing match: the run can start a few seconds before Sentry's
    Slack message lands, so the first message of a run waits a little for it."""
    for attempt in range(attempts):
        ts, retry = lookup_alert_message(token, channel, alert)
        if ts or not retry:
            return ts
        if attempt < attempts - 1:
            print(f"No Sentry alert message yet; retrying in {wait_s}s")
            time.sleep(wait_s)
    print("No Sentry alert message found to reply under; posting to the channel")
    return None


def lookup_alert_message(token, channel, alert):
    """(ts, retryable): ts of the newest matching Sentry message, or None and whether a
    retry could help (no match yet) or not (Slack refused the lookup)."""
    hours = float(os.environ.get("SELFHEAL_SLACK_THREAD_HOURS") or 6)
    needles = [os.environ.get("SELFHEAL_SLACK_ALERT_MATCH") or "revenue",
               alert.get("title"), alert.get("url")]
    needles = [n.lower() for n in needles if n]
    try:
        response = requests.get(
            f"{SLACK_API}/conversations.history",
            headers={"Authorization": f"Bearer {token}"},
            params={"channel": channel, "oldest": f"{time.time() - hours * 3600:.0f}", "limit": 100},
            timeout=15,
        )
        body = response.json()
    except (requests.RequestException, ValueError) as err:
        print(f"Slack thread lookup failed ({err}); posting to the channel")
        return None, False
    if not body.get("ok"):
        print(f"Slack thread lookup failed: {body.get('error')} (needs channels:history, or"
              f" groups:history for a private channel); posting to the channel")
        return None, False
    # Newest first; the whole message (text, blocks, attachments) is searched, since Sentry
    # puts the alert name and link in blocks and attachments
    for message in body.get("messages", []):
        if is_from_sentry(message) and any(n in json.dumps(message).lower() for n in needles):
            return message["ts"], False
    return None, True


def post(text, blocks, alert=None, thread_attempts=1):
    """Post with an existing Slack bot's token if configured (in the thread of Sentry's alert
    message when there is one), else an incoming webhook, else print (the job log)."""
    token = os.environ.get("SELFHEAL_SLACK_BOT_TOKEN")
    channel = os.environ.get("SELFHEAL_SLACK_CHANNEL")
    url = os.environ.get("SELFHEAL_SLACK_WEBHOOK_URL")
    if token and channel:
        message = {"channel": channel, "text": text, "blocks": blocks, "unfurl_links": False}
        thread_ts = find_alert_thread(token, channel, alert or {}, attempts=thread_attempts)
        if thread_ts:
            message["thread_ts"] = thread_ts
        response = requests.post(
            f"{SLACK_API}/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json=message,
            timeout=15,
        )
        response.raise_for_status()
        body = response.json()
        # Slack answers 200 with ok: false on errors (bad channel, not in channel, missing scope)
        if not body.get("ok"):
            raise RuntimeError(f"Slack chat.postMessage failed: {body.get('error')}"
                               f" (needs chat:write, and the bot invited to {channel} unless it has chat:write.public)")
    elif url:
        requests.post(url, json={"text": text, "blocks": blocks}, timeout=15).raise_for_status()
    else:
        print(text)
        print(json.dumps(blocks, indent=2))


LABELS = {"without-seer": "without Seer", "with-seer": "with Seer"}


def first_sentence(text, limit=160):
    """Shortest useful form of an agent's explanation, for a scannable Slack line."""
    text = " ".join(str(text or "").split())
    end = text.find(". ")
    text = text[: end + 1] if 0 < end < limit else text
    return text if len(text) <= limit else text[: limit - 1] + "…"


def impact_line(impact):
    """Business impact in one line, from the Sentry numbers the agent collected."""
    parts = []
    if impact.get("lost_revenue_usd"):
        parts.append(f"~${impact['lost_revenue_usd']:,.0f} in failed orders")
    if impact.get("failed_checkouts"):
        parts.append(f"{impact['failed_checkouts']:,} failed checkouts")
    # 0 usually means events carry no user identity, not that nobody was affected
    if impact.get("users_affected"):
        parts.append(f"{impact['users_affected']:,} customers")
    if impact.get("first_seen"):
        # 2026-10-26T19:17:56Z -> since 19:17 UTC
        parts.append(f"since {str(impact['first_seen'])[11:16]} UTC")
    return " · ".join(parts) or "Checkout revenue is dropping"


def run_url():
    return (f"{os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}"
            f"/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}")


def report_started(args):
    """First reply on the alert: the agents are on it, with a link to watch them work."""
    alert = load(args.alert)
    agents = " and ".join(LABELS.get(v, v) for v in args.variants)
    text = (f"*Self-heal started* · agents ({agents}) are investigating with Sentry telemetry"
            f" · <{run_url()}|watch the run>")
    # Alert-driven runs can start before Sentry's Slack message lands: wait up to ~1 min for it
    attempts = 1 if alert.get("kind") == "manual" else 5
    post(text, [{"type": "section", "text": {"type": "mrkdwn", "text": text}}], alert,
         thread_attempts=attempts)


def report_run(args):
    """End of run. Each opened PR already got its own "Fix ready for review" message, so this
    posts only for agents that didn't open one; otherwise the thread would just stop."""
    alert = load(args.alert)
    # Only variants that ran upload a scorecard (with-seer can be switched off)
    ran = [v for v in VARIANTS if os.path.isdir(os.path.join(args.results, v))] or list(VARIANTS)
    failed = [v for v in ran if not load(os.path.join(args.results, v, "verify.json")).get("pr_url")]
    if not failed:
        print("Every agent opened a PR and posted its own message; nothing to add.")
        return
    agents = " and ".join(LABELS.get(v, v) for v in failed)
    text = f"*No fix proposed* ({agents}) · see the <{run_url()}|run log> for why"
    post(text, [{"type": "section", "text": {"type": "mrkdwn", "text": text}}], alert)


def report_review(args):
    """The human-in-the-loop ping, kept scannable: impact, root cause, verification, PR link.
    Everything else (how the fix was found, the review) is in the PR."""
    with open(args.review) as f:
        review = [line.strip() for line in f.read().strip().splitlines() if line.strip()]
    verdict = review[0].replace("**", "").replace("Verdict:", "").strip() if review else "?"

    stats = load(os.path.join(args.results, "stats.json"))
    check = load(os.path.join(args.results, "verify.json"))
    agent = load(os.path.join(args.results, "result.json"))
    alert = load(os.path.join(args.results, "alert.json"))
    pr_number = args.pr_url.rstrip("/").rsplit("/", 1)[-1]

    verified = ("tests pass" if check.get("tests_passed") else "tests FAIL")
    if check.get("replay_status") == 200:
        verified += ", failing order now succeeds"
    footer = f"{verified} · reviewer: {verdict} · {LABELS.get(args.variant, args.variant)}"
    if stats:
        footer += f", {stats['duration_s']:.0f}s, ${stats['cost_usd']:.2f}"

    text = "\n".join([
        f"*Fix ready for review* · 🔧 <{args.pr_url}|PR #{pr_number}>",
        impact_line(agent.get("impact") or {}),
        f"Root cause: {agent.get('root_cause_short') or first_sentence(agent.get('root_cause') or 'see the PR', 120)}",
        footer,
    ])
    post(text, [{"type": "section", "text": {"type": "mrkdwn", "text": text}}], alert)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    run = sub.add_parser("run")
    run.add_argument("--alert", required=True)
    run.add_argument("--results", required=True)
    review = sub.add_parser("review")
    review.add_argument("--pr-url", required=True)
    review.add_argument("--review", required=True)
    review.add_argument("--variant", required=True)
    review.add_argument("--results", required=True, help="Dir with this variant's stats/verify/result.json")
    started = sub.add_parser("started")
    started.add_argument("--alert", required=True)
    started.add_argument("--variants", default='["without-seer"]', type=json.loads,
                         help='JSON list of the variants this run starts, e.g. ["without-seer"]')
    args = parser.parse_args()
    {"run": report_run, "review": report_review, "started": report_started}[args.mode](args)
