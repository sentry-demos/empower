"""The Slack channels the alert that started this run posts to, so the bot replies there.

Sentry's webhook doesn't say where the alert posts in Slack, so this looks the alert up by
name in the alert's org and reads its Slack actions:
  1. Alerts (Monitors & Alerts, which also serves older issue alerts):
     /organizations/<org>/workflows/, Slack actions' config.targetIdentifier.
  2. Older issue alert rules: /projects/<org>/<project>/rules/, Slack actions' channel_id.
Names needn't be unique, so among same-named alerts, those that also call a webhook or
integration (the selfheal one) win. Any problem returns [] and the bot posts to
SELFHEAL_SLACK_CHANNEL as before. Uses only the standard library (the plan job has no installs).

Usage (prints a JSON list of channel IDs):
    python selfheal/harness/slack_channels.py .selfheal/alert.json
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

from plan import sentry_token  # same directory: python puts the script's folder on sys.path

CHANNEL_ID_RE = re.compile(r"^[CG][A-Z0-9]{6,}$")  # public (C) or private (G) channel IDs
WEBHOOK_ACTION_TYPES = {"webhook", "sentry_app"}
MAX_PAGES = 5


def sentry_get(org, path, params=None):
    """(json, next cursor) for a Sentry API GET, or (None, None) if it can't be read."""
    token = sentry_token(org)
    if not token:
        return None, None
    api = os.environ.get("SENTRY_API_URL", "https://sentry.io/api/0").rstrip("/")
    url = f"{api}{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            body = json.load(response)
            link = response.headers.get("Link") or ""
    except (OSError, ValueError) as err:
        print(f"::warning title=Slack channel lookup::{path}: {err}", file=sys.stderr)
        return None, None
    # Sentry paginates with Link: <...>; rel="next"; results="true"; cursor="..."
    match = re.search(r'rel="next"; results="true"; cursor="([^"]+)"', link)
    return body, (match.group(1) if match else None)


def named(org, path, name, params=None):
    """Every item at `path` (a Sentry list endpoint) whose name is exactly `name`."""
    found, cursor = [], None
    for _ in range(MAX_PAGES):
        page_params = {**(params or {}), "per_page": 100, **({"cursor": cursor} if cursor else {})}
        items, cursor = sentry_get(org, path, page_params)
        if not isinstance(items, list):
            break
        found += [item for item in items if item.get("name") == name]
        if not cursor:
            break
    return found


def workflow_actions(workflow):
    return [action for group in workflow.get("actionFilters") or [] for action in group.get("actions") or []]


def workflow_channels(workflow):
    return [str((action.get("config") or {}).get("targetIdentifier") or "")
            for action in workflow_actions(workflow) if action.get("type") == "slack"]


def calls_webhook(workflow):
    return any(action.get("type") in WEBHOOK_ACTION_TYPES for action in workflow_actions(workflow))


def rule_channels(rule):
    return [str(action.get("channel_id") or "") for action in rule.get("actions") or []
            if "slack" in str(action.get("id", "")).lower()]


def rule_calls_webhook(rule):
    return any(any(word in str(action.get("id", "")).lower() for word in ("sentry_app", "webhook", "notify_event"))
               for action in rule.get("actions") or [])


def preferred(items, calls):
    """Same-named alerts: the ones that call a webhook (ours) if any do, else all of them."""
    with_webhook = [item for item in items if calls(item)]
    return with_webhook or items


def alert_workflows(alert):
    """The alert that fired, as Sentry workflows (usually one): same-named ones that call a
    webhook win. [] if it can't be found."""
    org, name = alert.get("org"), alert.get("rule")
    if not (org and name):
        return []
    # The name search narrows the list; if it finds nothing (its syntax can differ), list them all
    workflows = (named(org, f"/organizations/{org}/workflows/", name, {"query": name})
                 or named(org, f"/organizations/{org}/workflows/", name))
    return preferred(workflows, calls_webhook)


def alert_slack_channels(alert):
    """Slack channel IDs the alert posts to, in a stable order, or [] if unknown."""
    org, name = alert.get("org"), alert.get("rule")
    if not (org and name):
        return []
    channels = []
    workflows = alert_workflows(alert)
    for workflow in workflows:
        channels += workflow_channels(workflow)
    if not workflows and alert.get("project_slug"):
        rules = named(org, f"/projects/{org}/{alert['project_slug']}/rules/", name)
        for rule in preferred(rules, rule_calls_webhook):
            channels += rule_channels(rule)
    # Channel IDs only: history and threading need IDs, not #names
    return list(dict.fromkeys(c for c in channels if CHANNEL_ID_RE.match(c)))


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        print(json.dumps(alert_slack_channels(json.load(f))))
