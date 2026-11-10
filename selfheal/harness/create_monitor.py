"""Create the metric monitor the telemetry agent proposed, and an alert for it.

From OUT/telemetry.json (checked by telemetry_spec.py):
  1. A Metric Monitor in the target's telemetry project, on the new Application Metric: e.g.
     max(value,agent.policy.documents,distribution,-) over 5 minutes, critical above the
     threshold. One with the same name already there is reused, so reruns don't pile up
     monitors.
  2. An Alert on that monitor with the Slack action(s) of the alert that started this run (never
     its selfheal webhook, so a breach notifies people without starting another agent run).
  3. "<Created monitor>: alerts when max > 10 documents in 5 min" in the alert's Slack thread.

Usage (repo root, after open_telemetry_pr.py):
    python selfheal/harness/create_monitor.py --out DIR
Needs the org's Sentry token with Alerts: Read & Write (SENTRY_MCP_TOKEN[_<ORG>]).
Writes DIR/monitor.json.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

import report  # same directory: python puts the script's folder on sys.path
import slack_channels
import telemetry_spec
from plan import sentry_token

METRIC_EVENT_TYPE = "trace_item_metric"  # Application Metrics on Sentry's events platform
# Requests below are shaped like those of Sentry's own MCP server (@sentry/mcp-server 0.49:
# createMetricMonitor and createAlertRule), whose tools create monitors and alerts that work.


class SentryError(RuntimeError):
    pass


def sentry(org, method, path, body=None, params=None):
    """A Sentry API call; raises SentryError with Sentry's own message on failure."""
    token = sentry_token(org)
    if not token:
        raise SentryError(f"no Sentry token for org {org}")
    api = os.environ.get("SENTRY_API_URL", "https://sentry.io/api/0").rstrip("/")
    url = f"{api}{path}" + (f"?{urllib.parse.urlencode(params)}" if params else "")
    request = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            text = response.read().decode() or "null"
    except urllib.error.HTTPError as err:
        raise SentryError(f"{method} {path}: HTTP {err.code}: {err.read().decode(errors='replace')[:1000]}")
    except OSError as err:
        raise SentryError(f"{method} {path}: {err}")
    return json.loads(text)


def monitor_name(spec):
    m = spec["monitor"]
    return f"{spec['metric']['name']} — {m['aggregate']} above {m['threshold']} (self-heal telemetry)"


def detector_payload(spec, name, window_seconds):
    threshold = spec["monitor"]["threshold"]
    return {
        "type": "metric_issue",
        "name": name,
        "description": spec["monitor"].get("reasoning") or None,
        "config": {"detectionType": "static", "comparisonDelta": None},
        "conditionGroup": {"logicType": "any", "conditions": [
            {"type": "gt", "comparison": threshold, "conditionResult": 75},   # critical
            {"type": "lte", "comparison": threshold, "conditionResult": 0},   # resolved
        ]},
        "dataSources": [{
            "dataset": "events_analytics_platform",
            "query": "",
            "aggregate": spec["monitor"]["sentry_aggregate"],
            "environment": None,
            "eventTypes": [METRIC_EVENT_TYPE],
            "timeWindow": int(window_seconds),
        }],
        "workflowIds": [],
    }


def alert_payload(name, detector_id, slack_actions, frequency_minutes):
    """An Alert on the monitor: notify when its issue opens or comes back."""
    return {
        "name": f"Notify: {name}",
        "enabled": True,
        "environment": None,
        "config": {"frequency": int(frequency_minutes)},
        "triggers": {"logicType": "any-short", "conditions": [
            {"type": "first_seen_event", "comparison": True, "conditionResult": True},
            {"type": "regression_event", "comparison": True, "conditionResult": True},
        ]},
        "actionFilters": [{"logicType": "all", "conditions": [], "actions": [
            {key: action[key] for key in ("type", "integrationId", "config", "data") if key in action}
            for action in slack_actions
        ]}],
        "detectorIds": [str(detector_id)],
    }


def find_monitor(org, project_id, name):
    found = sentry(org, "GET", f"/organizations/{org}/detectors/", params={"project": project_id, "query": name})
    return next((d for d in found or [] if d.get("name") == name and d.get("type") == "metric_issue"), None)


def create(out, alert, settings):
    spec = telemetry_spec.load(out)
    org = alert.get("org") or os.environ.get("SENTRY_ORG") or "demo"
    project = settings.get("project") or os.environ.get("SENTRY_PROJECT")
    window = int(settings.get("window_seconds") or 300)
    project_id = sentry(org, "GET", f"/projects/{org}/{project}/")["id"]
    name = monitor_name(spec)

    detector = find_monitor(org, project_id, name)
    reused = detector is not None
    if not reused:
        # Created under the org's project (/projects/<org>/<project>/detectors/ is a 404, and
        # /organizations/<org>/detectors/ only lists them: 405)
        detector = sentry(org, "POST", f"/organizations/{org}/projects/{project}/detectors/",
                          detector_payload(spec, name, window))
    result = {"id": str(detector["id"]), "name": name, "reused": reused, "org": org, "project": project,
              "aggregate": spec["monitor"]["sentry_aggregate"], "threshold": spec["monitor"]["threshold"],
              "url": f"https://{org}.sentry.io/monitors/{detector['id']}/",
              "description": telemetry_spec.describe(spec, window), "alert_id": None}

    # An alert only if the monitor has none yet (a reused one keeps whatever it's connected to)
    if not detector.get("workflowIds"):
        slack = slack_channels.alert_slack_actions(alert)
        if slack:
            workflow = sentry(org, "POST", f"/organizations/{org}/workflows/",
                              alert_payload(name, detector["id"], slack, settings.get("frequency_minutes") or 5))
            result["alert_id"] = str(workflow["id"])
        else:
            print("::warning title=Monitor alert::The alert that started this run has no Slack action to copy;"
                  " the monitor was created without an alert", flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    alert = report.load(os.path.join(args.out, "alert.json"))
    settings = json.loads(os.environ.get("TARGET_TELEMETRY") or "{}")
    try:
        monitor = create(args.out, alert, settings)
    except (telemetry_spec.SpecError, SentryError, KeyError, TypeError) as err:
        print(f"::warning title=No monitor created::{err}".replace("\n", " "), flush=True)
        sys.exit(1)
    with open(os.path.join(args.out, "monitor.json"), "w") as f:
        json.dump(monitor, f, indent=2)
    print(f"Monitor: {monitor['url']} ({'reused' if monitor['reused'] else 'created'})", flush=True)
    link = "Created monitor" if not monitor["reused"] else "Monitor already in place"
    report.post_status(f"<{monitor['url']}|{link}>: alerts when {monitor['description']}", alert)


if __name__ == "__main__":
    main()
