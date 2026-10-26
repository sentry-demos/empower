"""Post self-heal results to Slack.

    python selfheal/harness/report.py run --alert alert.json --results DIR
        DIR holds one sub-directory per variant with stats.json, verify.json, result.json.
        Posts "checkout failing -> root cause -> PR ready" with the side-by-side scorecard.

    python selfheal/harness/report.py review --pr-url URL --review FILE
        Posts the reviewer agent's verdict for one PR.

Needs SELFHEAL_SLACK_WEBHOOK_URL (an incoming webhook). Without it, prints the message.
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
    url = os.environ.get("SELFHEAL_SLACK_WEBHOOK_URL")
    if not url:
        print(text)
        print(json.dumps(blocks, indent=2))
        return
    requests.post(url, json={"text": text, "blocks": blocks}, timeout=15).raise_for_status()


def variant_section(variant, results):
    stats = load(os.path.join(results, variant, "stats.json"))
    check = load(os.path.join(results, variant, "verify.json"))
    agent = load(os.path.join(results, variant, "result.json"))
    if not stats:
        return f"*{variant}*: no result (job failed before the agent finished)", None

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
    return "\n".join(lines), agent.get("issue_short_id")


def report_run(args):
    alert = load(args.alert)
    sections, issue = [], None
    for variant in VARIANTS:
        text, short_id = variant_section(variant, args.results)
        sections.append(text)
        issue = issue or short_id

    run_url = f"{os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
    headline = f"🚨 {alert.get('title', 'Checkout failing')} → root cause → PR ready"
    context = f"<{alert.get('url', '')}|Alert>" if alert.get("url") else "Alert"
    if issue:
        context += f" · Issue {issue}"
    context += f" · <{run_url}|Actions run> · A human must review and merge."

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": headline[:150]}},
        {"type": "context", "elements": [{"type": "mrkdwn", "text": context}]},
    ]
    for text in sections:
        blocks += [{"type": "divider"}, {"type": "section", "text": {"type": "mrkdwn", "text": text}}]
    post(headline, blocks)


def report_review(args):
    with open(args.review) as f:
        review = f.read().strip()
    verdict = review.splitlines()[0] if review else "**Verdict: ?**"
    text = f"🧐 Reviewer agent on <{args.pr_url}|PR>: {verdict.replace('**', '*')}"
    post(text, [{"type": "section", "text": {"type": "mrkdwn", "text": text}}])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="mode", required=True)
    run = sub.add_parser("run")
    run.add_argument("--alert", required=True)
    run.add_argument("--results", required=True)
    review = sub.add_parser("review")
    review.add_argument("--pr-url", required=True)
    review.add_argument("--review", required=True)
    args = parser.parse_args()
    report_run(args) if args.mode == "run" else report_review(args)
