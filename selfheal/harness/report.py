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
"""
import argparse
import json
import os

import requests

VARIANTS = ("without-seer", "with-seer")


def load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default if default is not None else {}


def post(text, blocks):
    """Post with an existing Slack bot's token if configured, else an incoming webhook,
    else print (the message still shows in the job log)."""
    token = os.environ.get("SELFHEAL_SLACK_BOT_TOKEN")
    channel = os.environ.get("SELFHEAL_SLACK_CHANNEL")
    url = os.environ.get("SELFHEAL_SLACK_WEBHOOK_URL")
    if token and channel:
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": channel, "text": text, "blocks": blocks, "unfurl_links": False},
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
    post(headline, blocks)


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
    ])


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
