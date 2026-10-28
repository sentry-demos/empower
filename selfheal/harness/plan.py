"""Which agent version(s) a self-heal run starts, from the alert that triggered it.

Each alert picks its version, so two alerts can drive the two versions separately:
  1. `variant` in alert.json, set by the receiver from the event's `se` tag
     (se=selfheal-with-seer / se=selfheal-without-seer) or from the alert rule's name.
  2. Otherwise, for an issue alert, the issue's own `se` tag, looked up in Sentry. The Flask
     app groups issues by `se`, so each issue carries exactly one value. Needs
     SENTRY_MCP_TOKEN; any problem with the lookup just moves on to the next rule.
  3. Otherwise "with-seer" / "without-seer" in the alert's title or description. The
     receiver puts the rule name there, so naming the alert e.g.
     "Checkout revenue dropped [with-seer]" is enough.
  4. Otherwise the default: SELFHEAL_VARIANTS (both, side by side, or a repo-chosen list).

Usage (prints the JSON list for the workflow matrix):
    python selfheal/harness/plan.py .selfheal/alert.json
"""
import json
import os
import sys
import urllib.parse
import urllib.request

VARIANTS = ("without-seer", "with-seer")


def variant_in(*texts):
    """The version named in any of the texts, or "". "without-seer" is checked first:
    it doesn't contain "with-seer", but checking it first keeps that obvious."""
    for text in texts:
        text = str(text or "").lower()
        for variant in VARIANTS:
            if variant in text:
                return variant
    return ""


def issue_se_tag(issue_id):
    """The `se` tag on the issue's latest event, or "" if it can't be read. Uses only the
    standard library, so the plan job needs no installs."""
    token = os.environ.get("SENTRY_MCP_TOKEN")
    if not (issue_id and token):
        return ""
    api = os.environ.get("SENTRY_API_URL", "https://sentry.io/api/0").rstrip("/")
    org = os.environ.get("SENTRY_ORG") or "demo"
    url = f"{api}/organizations/{org}/issues/{urllib.parse.quote(str(issue_id))}/events/latest/"
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            event = json.load(response)
    except (OSError, ValueError) as err:
        print(f"::warning title=se tag lookup::issue {issue_id}: {err}", file=sys.stderr)
        return ""
    for tag in event.get("tags") or []:
        if isinstance(tag, dict) and tag.get("key") == "se":
            return str(tag.get("value") or "")
    return ""


def alert_variant(alert):
    """The single version this alert asks for, or "" if it doesn't say."""
    if alert.get("variant") in VARIANTS:
        return alert["variant"]
    return variant_in(alert.get("se"), alert.get("rule"), alert.get("title"), alert.get("description"))


def variants_for(alert, default=None, lookup=issue_se_tag):
    variant = alert.get("variant") if alert.get("variant") in VARIANTS else ""
    if not variant and alert.get("issue_id"):
        se = lookup(alert["issue_id"])
        print(f"Issue {alert['issue_id']} has se={se or '(none)'}", file=sys.stderr)
        variant = variant_in(se)
    variant = variant or alert_variant(alert)
    if variant:
        return [variant]
    if default is None:
        default = os.environ.get("SELFHEAL_VARIANTS") or '["without-seer"]'
    chosen = [v for v in json.loads(default) if v in VARIANTS]
    return chosen or ["without-seer"]


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        alert = json.load(f)
    print(json.dumps(variants_for(alert)))
