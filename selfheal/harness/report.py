"""Post self-heal results to Slack.

    python selfheal/harness/report.py review --pr-url URL --review FILE --variant V --results DIR
        Posted once per agent PR, after the reviewer agent has commented: the notification
        that tells a human a verified fix is waiting for them. DIR holds that variant's
        stats.json, verify.json and result.json.

    python selfheal/harness/report.py started --alert alert.json --variants '["without-seer"]'
        Posted when the run starts: the agents are on it, with a link to the run.

    python selfheal/harness/report.py status --kind seer|sentry --variant V --dir DIR
        Progress while a fix job runs: Seer's root cause was queried (with-seer), or what the
        agent pulled from Sentry (without-seer). open_pr.py also posts "Opening draft PR".

    python selfheal/harness/report.py run --alert alert.json --results DIR
        Posted when the run ends: the side-by-side scorecard. DIR holds one sub-directory
        per variant with the files above.

Slack: SELFHEAL_SLACK_BOT_TOKEN, an existing bot's xoxb- token (chat:write, channels:history,
ideally channels:join). Without it, messages are only printed in the job log.

Threads only: every message is a reply in the thread of Sentry's own alert message, never a
post in a channel. Where to look: the Slack channels the alert itself posts to
(SELFHEAL_SLACK_CHANNELS, looked up in Sentry by slack_channels.py in the plan job), or
SELFHEAL_SLACK_CHANNEL when that lookup found none. The bot joins a public channel it isn't in
yet (needs channels:join); private channels need an invite. If no thread is found (the alert
posts to another Slack workspace, the bot can't read the channel, a trigger.sh run has no alert
message), the message isn't posted: the job logs it and shows a "Slack message not posted"
warning on the run.

Finding the thread: the most recent message from the Sentry app that matches, most
specific first: the issue's link (issue alerts; within SELFHEAL_SLACK_ISSUE_THREAD_DAYS, default
30, since Sentry threads a repeat issue alert under the issue's first alert message), then
within SELFHEAL_SLACK_THREAD_HOURS (default 6) the alert's title or link, then the target's match text
(SELFHEAL_SLACK_ALERT_MATCH, set per target in targets.json). When the alert names a version
(with-seer / without-seer), the title/link and match-text rules also need the message to name
it, so two alerts on the same metric each get their own thread. Needs channels:history
(groups:history for a private channel).
"""
import argparse
import json
import os
import time

import requests

from plan import alert_variant, issue_category  # same directory: python puts the script's folder on sys.path

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
    """ts of Sentry's alert message to reply under, or None. Never raises: with no thread
    (missing scope, no match), the message just isn't posted in this channel.

    attempts > 1 retries a missing match: the run can start a few seconds before Sentry's
    Slack message lands, so the first message of a run waits a little for it."""
    for attempt in range(attempts):
        ts, retry = lookup_alert_message(token, channel, alert)
        if ts or not retry:
            return ts
        if attempt < attempts - 1:
            print(f"No Sentry alert message yet; retrying in {wait_s}s")
            time.sleep(wait_s)
    print(f"No Sentry alert message in {channel} to reply under")
    return None


def lookup_alert_message(token, channel, alert):
    """(ts, retryable): ts of the newest matching Sentry message, or None and whether a
    retry could help (no match yet) or not (Slack refused the lookup)."""
    hours = float(os.environ.get("SELFHEAL_SLACK_THREAD_HOURS") or 6)
    variant = alert_variant(alert)
    specific = [n.lower() for n in (alert.get("title"), alert.get("url")) if n]
    fallback = (os.environ.get("SELFHEAL_SLACK_ALERT_MATCH") or "").lower()

    recent = time.time() - hours * 3600

    def names_variant(text):
        return not variant or variant in text

    # Most specific first: the issue's own link (issue alerts), then this alert's title or link,
    # then the target's match text, so a reply can't land under another org's or target's alert.
    # The last two must come with the version's name when the alert has one, and look only at
    # recent messages. The issue's link is specific enough to look further back: with Slack
    # threads on for issue alerts, Sentry posts a repeat alert as a reply under the issue's
    # first alert message, which can be days old, and conversations.history only lists that one.
    rules = []
    oldest = recent
    if alert.get("issue_id"):
        rules.append(lambda message, text: f"issues/{alert['issue_id']}" in text)
        oldest = time.time() - float(os.environ.get("SELFHEAL_SLACK_ISSUE_THREAD_DAYS") or 30) * 86400
    rules.append(lambda message, text: float(message["ts"]) >= recent
                 and any(n in text for n in specific) and names_variant(text))
    if fallback:
        rules.append(lambda message, text: float(message["ts"]) >= recent
                     and fallback in text and names_variant(text))
    messages, error = channel_history(token, channel, oldest)
    if error == "not_in_channel" and join_channel(token, channel):
        messages, error = channel_history(token, channel, oldest)
    if error:
        why = (" (the channel is in another Slack workspace, or the bot can't see it)" if error == "channel_not_found"
               else " (needs channels:history, or groups:history and an invite for a private channel)")
        print(f"Slack thread lookup in {channel} failed: {error}{why}")
        return None, False
    # Newest first; the whole message (text, blocks, attachments) is searched, since Sentry
    # puts the alert name and link in blocks and attachments. ensure_ascii=False keeps titles
    # like "Context Snowball — max input tokens" matchable (the em dash isn't escaped)
    messages = [(m, json.dumps(m, ensure_ascii=False).lower()) for m in messages if is_from_sentry(m)]
    for rule in rules:
        for message, text in messages:
            if rule(message, text):
                # A match that is itself a reply (sent to the channel too) belongs to its thread
                return message.get("thread_ts") or message["ts"], False
    return None, True


def channel_history(token, channel, oldest, max_pages=10):
    """(messages, error): the channel's top-level messages since `oldest`, newest first."""
    messages, cursor = [], None
    for _ in range(max_pages):
        params = {"channel": channel, "oldest": f"{oldest:.0f}", "limit": 200}
        if cursor:
            params["cursor"] = cursor
        try:
            body = requests.get(f"{SLACK_API}/conversations.history",
                                headers={"Authorization": f"Bearer {token}"},
                                params=params, timeout=15).json()
        except (requests.RequestException, ValueError) as err:
            return messages, str(err)
        if not body.get("ok"):
            return messages, body.get("error")
        messages += body.get("messages", [])
        cursor = (body.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            break
    return messages, None


def join_channel(token, channel):
    """Join a public channel so its history can be read (needs channels:join). Private channels
    need someone to invite the bot instead."""
    try:
        body = requests.post(f"{SLACK_API}/conversations.join", headers={"Authorization": f"Bearer {token}"},
                             json={"channel": channel}, timeout=15).json()
    except (requests.RequestException, ValueError) as err:
        body = {"error": str(err)}
    if not body.get("ok"):
        print(f"Can't join {channel}: {body.get('error')} (invite the bot, or give it channels:join)")
    return bool(body.get("ok"))


def alert_channels():
    """The Slack channels the alert posts to (SELFHEAL_SLACK_CHANNELS, a JSON list of IDs the
    plan job looked up in Sentry; see slack_channels.py)."""
    try:
        channels = json.loads(os.environ.get("SELFHEAL_SLACK_CHANNELS") or "[]")
    except ValueError:
        return []
    return [c for c in channels if isinstance(c, str) and c] if isinstance(channels, list) else []


def reply_in_thread(token, channel, thread_ts, text, blocks):
    """Reply under Sentry's alert message. True if Slack took it."""
    try:
        body = requests.post(
            f"{SLACK_API}/chat.postMessage",
            headers={"Authorization": f"Bearer {token}"},
            json={"channel": channel, "thread_ts": thread_ts, "text": text, "blocks": blocks,
                  "unfurl_links": False},
            timeout=15,
        ).json()
    except (requests.RequestException, ValueError) as err:
        body = {"error": str(err)}
    # Slack answers 200 with ok: false on errors (not in channel, missing scope)
    if not body.get("ok"):
        print(f"Slack reply in {channel} failed: {body.get('error')} (needs chat:write)")
    return bool(body.get("ok"))


def not_posted(text, reason):
    """Make a dropped message visible on the GitHub run: a warning annotation plus the text."""
    first_line = " ".join(text.splitlines()[0].replace("*", "").split()) if text else ""
    # Workflow commands end at a newline, and % : , need escaping in the title/message
    message = f"{reason}: {first_line}".replace("%", "%25").replace("\r", "").replace("\n", " ")
    print(f"::warning title=Slack message not posted::{message}")
    print(text)


def post(text, blocks, alert=None, thread_attempts=1):
    """Reply in the thread of Sentry's alert message, and nowhere else. True if posted in at
    least one channel. Looks in the Slack channels the alert posts to (SELFHEAL_SLACK_CHANNELS),
    or SELFHEAL_SLACK_CHANNEL when the plan job found none. With no thread in any of them, the
    message is dropped with a warning on the run, never posted in a channel. Never raises."""
    token = os.environ.get("SELFHEAL_SLACK_BOT_TOKEN")
    if not token:
        not_posted(text, "SELFHEAL_SLACK_BOT_TOKEN isn't set")
        return False
    fallback = os.environ.get("SELFHEAL_SLACK_CHANNEL")
    channels = alert_channels() or ([fallback] if fallback else [])
    if not channels:
        not_posted(text, "No Slack channel to look in (the alert has no Slack action, and SELFHEAL_SLACK_CHANNEL isn't set)")
        return False
    posted = False
    for channel in channels:
        thread_ts = find_alert_thread(token, channel, alert or {}, attempts=thread_attempts)
        if thread_ts and reply_in_thread(token, channel, thread_ts, text, blocks):
            posted = True
    if not posted:
        not_posted(text, f"No Sentry alert thread the bot can reply in, in {', '.join(channels)}")
    return posted


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
    return " · ".join(parts) or first_sentence(impact.get("summary") or "Impact details are in the PR", 120)


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


def post_status(text, alert):
    """A progress line in the alert's thread. Never fails the step: the run matters more."""
    try:
        post(text, [{"type": "section", "text": {"type": "mrkdwn", "text": text}}], alert)
    except (requests.RequestException, RuntimeError) as err:
        print(f"Status message not posted ({err}): {text}")


# What each Sentry MCP call looked at, as (singular, plural) for a one-line summary.
# Setup calls (find_organizations, whoami, ...) are left out.
SENTRY_LOOKUPS = {
    "get_issue_details": ("the issue", "the issue"),
    "search_issues": ("issue search", "issue searches"),
    "get_trace_details": ("trace", "traces"),
    "search_traces": ("trace search", "trace searches"),
    "search_issue_events": ("event search", "event searches"),
    "search_logs": ("log search", "log searches"),
    "search_errors": ("error search", "error searches"),
    "search_metrics": ("metrics query", "metrics queries"),
    "search_replays": ("replay search", "replay searches"),
    "search_profiles": ("profile search", "profile searches"),
    "get_issue_activity": ("issue history", "issue history"),
    "get_issue_breadcrumbs": ("breadcrumb trail", "breadcrumb trails"),
}
SEARCH_EVENTS_DATASETS = {"spans": ("span search", "span searches"), "logs": ("log search", "log searches"),
                          "errors": ("error search", "error searches")}
RESOURCE_TYPES = {"issue": ("the issue", "the issue"), "trace": ("trace", "traces"),
                  "event": ("event", "events"), "breadcrumbs": ("breadcrumb trail", "breadcrumb trails")}


def sentry_lookup(name, tool_input):
    """(singular, plural) for one Sentry MCP call, or None for setup calls."""
    name = name.removeprefix("mcp__sentry__")
    if name == "execute_sentry_tool":  # the MCP's catch-all: the real tool is in its arguments
        name, tool_input = tool_input.get("name", ""), tool_input.get("arguments") or {}
    if name == "get_sentry_resource":
        kind = tool_input.get("resourceType") or ("issue" if "/issues/" in str(tool_input.get("url", "")) else "")
        return RESOURCE_TYPES.get(kind, ("Sentry resource", "Sentry resources"))
    if name == "search_events":
        return SEARCH_EVENTS_DATASETS.get(tool_input.get("dataset"), ("event search", "event searches"))
    return SENTRY_LOOKUPS.get(name)


def sentry_summary(timeline, short_id):
    """One sentence on what the agent pulled from Sentry, or "" if it pulled nothing."""
    calls = [t for t in timeline if t.get("type") == "tool" and t["name"].startswith("mcp__sentry__")
             and not t.get("error") and not t["name"].endswith("analyze_issue_with_seer")]
    counts = {}  # insertion order: the order the agent looked at things
    for call in calls:
        lookup = sentry_lookup(call["name"], call.get("input") or {})
        if lookup:
            counts[lookup] = counts.get(lookup, 0) + 1
    if not counts:
        return ""
    parts = [one if one == many else f"{n} {one if n == 1 else many}" for (one, many), n in counts.items()]
    listed = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    done_s = max(c.get("at_s", 0) + c.get("seconds", 0) for c in calls)
    return (f"Investigated {short_id or 'the issue'} with {len(calls)} Sentry MCP call{'s' if len(calls) != 1 else ''}"
            f" ({done_s:.0f}s): read {listed}.")


def report_status(args):
    """Progress in the alert's thread while a fix job runs: what Sentry (or Seer) told the agent."""
    alert = load(os.path.join(args.dir, "alert.json"))
    if args.kind == "seer":
        handoff = load(os.path.join(args.dir, "handoff.json"))
        seer = handoff.get("seer") or {}
        if not seer:
            print("No Seer handoff; nothing to post")
            return
        issue = (handoff.get("issue") or {}).get("short_id") or "the issue"
        source = "its earlier analysis" if seer.get("reused") else "a new analysis"
        text = (f"🔎 *Seer root cause* · pulled {issue}, its logs and impact from Sentry,"
                f" then queried Seer ({source}, {seer.get('seconds', 0):.0f}s): "
                f"{first_sentence(seer.get('root_cause'), 200)}")
    else:
        timeline = load(os.path.join(args.dir, "timeline.json"), default=[])
        agent = load(os.path.join(args.dir, "result.json"))
        summary = sentry_summary(timeline, agent.get("issue_short_id"))
        if not summary:
            print("The agent made no Sentry calls; nothing to post")
            return
        text = f"🔎 *Sentry telemetry* · {summary}"
    post_status(text, alert)


def is_metric_alert(alert, lookup=issue_category):
    """Metric alerts arrive as metric_alert, or (Monitors & Alerts) as an issue alert whose issue
    is a metric issue, which only Sentry can tell us."""
    if alert.get("kind") == "metric_alert":
        return True
    return bool(alert.get("issue_id")) and lookup(alert["issue_id"], alert.get("org")) == "metric"


def report_dashboard(out, lookup=issue_category):
    """For metric alerts, the target's dashboard (TARGET_DASHBOARD_URL), before the PR opens."""
    url = os.environ.get("TARGET_DASHBOARD_URL")
    alert = load(os.path.join(out, "alert.json"))
    if not url or not is_metric_alert(alert, lookup):
        return
    label = os.environ.get("TARGET_DASHBOARD_LABEL") or "dashboard"
    # Slack wants &, < and > escaped, link targets included
    url = url.replace("&", "&amp;").replace("<", "%3C").replace(">", "%3E")
    post_status(f"📊 See the impact on the <{url}|{label}>", alert)


def report_opening_pr(variant, out, check):
    """Called by open_pr.py once the harness has verified the fix, right before it opens the PR."""
    verified = "tests pass"
    if check.get("replay_status") == 200:
        verified += ", failing request now succeeds"
    if check.get("check_passed"):
        verified += f", {check.get('check_label') or 'fix check passes'}"
    post_status(f"*Opening draft PR* · fix verified: {verified}",
                load(os.path.join(out, "alert.json")))


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
    if check.get("check_passed"):
        verified += f", {check.get('check_label') or 'fix check passes'}"
    footer = f"{verified} · reviewer: {verdict}"
    if stats:
        footer += f" · {stats['duration_s']:.0f}s, ${stats['cost_usd']:.2f}"

    text = "\n".join([
        f"*Fix ready for review* · 🔧 <{args.pr_url}|PR #{pr_number}>",
        agent.get("impact_short") or impact_line(agent.get("impact") or {}),
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
    status = sub.add_parser("status")
    status.add_argument("--kind", required=True, choices=["seer", "sentry"],
                        help="seer: after the with-Seer handoff; sentry: after the agent's Sentry calls")
    status.add_argument("--variant", required=True)
    status.add_argument("--dir", required=True, help="The fix job's output dir (alert.json and handoff/timeline)")
    args = parser.parse_args()
    {"run": report_run, "review": report_review, "started": report_started,
     "status": report_status}[args.mode](args)
