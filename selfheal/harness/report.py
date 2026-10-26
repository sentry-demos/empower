"""Post self-heal results to Slack.

    python selfheal/harness/report.py review --pr-url URL --review FILE --variant V --results DIR
        Posted once per agent PR, after the reviewer agent has commented: the notification
        that tells a human a verified fix is waiting for them. DIR holds that variant's
        stats.json, verify.json and result.json.

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


def find_alert_thread(token, channel, alert):
    """ts of Sentry's alert message to reply under, or None. Never raises: threading is a
    nicety, so any problem (missing scope, no match) falls back to a channel post."""
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
        return None
    if not body.get("ok"):
        print(f"Slack thread lookup failed: {body.get('error')} (needs channels:history, or"
              f" groups:history for a private channel); posting to the channel")
        return None
    # Newest first; the whole message (text, blocks, attachments) is searched, since Sentry
    # puts the alert name and link in blocks and attachments
    for message in body.get("messages", []):
        if is_from_sentry(message) and any(n in json.dumps(message).lower() for n in needles):
            return message["ts"]
    print("No Sentry alert message found to reply under; posting to the channel")
    return None


def post(text, blocks, alert=None):
    """Post with an existing Slack bot's token if configured (in the thread of Sentry's alert
    message when there is one), else an incoming webhook, else print (the job log)."""
    token = os.environ.get("SELFHEAL_SLACK_BOT_TOKEN")
    channel = os.environ.get("SELFHEAL_SLACK_CHANNEL")
    url = os.environ.get("SELFHEAL_SLACK_WEBHOOK_URL")
    if token and channel:
        message = {"channel": channel, "text": text, "blocks": blocks, "unfurl_links": False}
        thread_ts = find_alert_thread(token, channel, alert or {})
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


def variant_section(variant, results):
    stats = load(os.path.join(results, variant, "stats.json"))
    check = load(os.path.join(results, variant, "verify.json"))
    agent = load(os.path.join(results, variant, "result.json"))
    if not stats:
        return f"*{variant}*: no result (job failed before the agent finished)", {}

    status = "✅ PR ready" if check.get("pr_url") else "❌ no PR"
    pr = f"<{check['pr_url']}|draft PR>" if check.get("pr_url") else "—"
    lines = [
        f"*{variant}* · {status} · {pr}",
        f"⏱ {stats['duration_s']}s · 🔁 {stats['turns']} turns · 🔧 {stats['tool_calls']} tool calls"
        f" · 🪙 {stats['input_tokens'] + stats['output_tokens']:,} tokens · 💵 ${stats['cost_usd']:.2f}"
        f" · Seer calls: {stats['seer_calls']}",
        f"Tests: {'pass' if check.get('tests_passed') else 'fail'} · Replay: HTTP {check.get('replay_status')}",
    ]
    if agent.get("root_cause"):
        lines.append(f"> {agent['root_cause']}")
    return "\n".join(lines), agent


def report_run(args):
    alert = load(args.alert)
    sections, first_agent = [], {}
    # Only variants that ran upload a scorecard (with-seer can be switched off)
    ran = [v for v in VARIANTS if os.path.isdir(os.path.join(args.results, v))] or list(VARIANTS)
    for variant in ran:
        text, agent = variant_section(variant, args.results)
        sections.append(text)
        first_agent = first_agent or agent
    issue = first_agent.get("issue_short_id")

    run_url = f"{os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
    headline = f"📊 Self-heal scorecard: {alert.get('title', 'Checkout failing')}"
    context = f"<{alert.get('url', '')}|Alert>" if alert.get("url") else "Alert"
    if issue:
        context += f" · Issue {issue}"
    context += f" · <{run_url}|Actions run> · A human must review and merge."

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": headline[:150]}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": context}]},
        {"type": "section", "text": {"type": "mrkdwn", "text": problem_line(alert, first_agent)
                                     + "\n" + impact_line(first_agent.get("impact") or {})}},
    ]
    for text in sections:
        blocks += [{"type": "divider"}, {"type": "section", "text": {"type": "mrkdwn", "text": text}}]
    post(headline, blocks, alert)


def problem_line(alert, agent):
    """What's happening, in customer terms, plus the alert that caught it."""
    problem = agent.get("problem") or "Checkout is failing for customers."
    title = alert.get("title")
    if title and alert.get("url"):
        problem += f" Alert: <{alert['url']}|{title}>"
    elif title:
        problem += f" Alert: {title}"
    return f"🚨 *Problem:* {problem}"


def impact_line(impact):
    """Business impact from the Sentry numbers the agent collected. Missing numbers are left out."""
    parts = []
    if impact.get("lost_revenue_usd") is not None:
        parts.append(f"~${impact['lost_revenue_usd']:,.0f} in failed orders")
    if impact.get("failed_checkouts") is not None:
        parts.append(f"{impact['failed_checkouts']:,} failed checkouts")
    # 0 usually means events carry no user identity, not that nobody was affected
    if impact.get("users_affected"):
        parts.append(f"{impact['users_affected']:,} customers affected")
    if impact.get("first_seen"):
        parts.append(f"since {impact['first_seen']}")
    line = "💸 *Business impact:* " + (" · ".join(parts) if parts else "revenue from checkout is dropping")
    if impact.get("summary"):
        line += f"\n> {impact['summary']}"
    return line


def report_review(args):
    """The human-in-the-loop ping: a verified fix and the reviewer's verdict, with the PR link."""
    with open(args.review) as f:
        review = [line.strip() for line in f.read().strip().splitlines() if line.strip()]
    verdict = review[0].replace("**", "") if review else "Verdict: ?"
    # The first line of explanation after the verdict, without the footer we append
    reason = next((line for line in review[1:] if not line.startswith("_Reviewer agent")), "")

    stats = load(os.path.join(args.results, "stats.json"))
    check = load(os.path.join(args.results, "verify.json"))
    agent = load(os.path.join(args.results, "result.json"))
    alert = load(os.path.join(args.results, "alert.json"))
    pr_number = args.pr_url.rstrip("/").rsplit("/", 1)[-1]
    issue = agent.get("issue_short_id", "the checkout failure")

    headline = f"👀 Fix ready for your review: {issue} ({args.variant})"
    lines = [
        f"*<{args.pr_url}|PR #{pr_number}>* · {args.variant} · draft, waiting for a human to review and merge",
        problem_line(alert, agent),
        impact_line(agent.get("impact") or {}),
        f"*Root cause:* {agent.get('root_cause', 'see the PR')}",
        f"*Verified:* tests {'pass' if check.get('tests_passed') else 'fail'}"
        f" · replay of the failing production cart: HTTP {check.get('replay_status')}",
        f"*Reviewer agent:* {verdict}" + (f" — {reason[:300]}" if reason else ""),
    ]
    if stats:
        lines.append(f"⏱ {stats['duration_s']}s · 🔁 {stats['turns']} turns · 💵 ${stats['cost_usd']:.2f}"
                     f" · Seer calls: {stats['seer_calls']}")
    post(headline, [
        {"type": "header", "text": {"type": "plain_text", "text": headline[:150]}},
        {"type": "section", "text": {"type": "mrkdwn", "text": "\n".join(lines)}},
    ], alert)


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
    args = parser.parse_args()
    report_run(args) if args.mode == "run" else report_review(args)
