"""Link a pre-filled "new monitor" form for the metric the telemetry agent added, without
creating anything in Sentry (so SEs demoing at once don't each leave a monitor behind).

Sentry's new-monitor page fills its project, dataset and aggregate from the URL (the same link
Sentry's own Insights pages build: detectors/.../useInitialMetricDetectorFormData.tsx), e.g.
    https://team-se.sentry.io/monitors/new/settings/?detectorType=metric_issue&project=<id>
        &dataset=metrics&aggregate=max(value,agent.policy.documents,distribution,-)
It doesn't read a threshold or name from the URL, so the Slack line says what threshold to set:
    "<Preview monitor>: max of agent.policy.documents over 5 min · set the threshold to 10
     documents · open to review and create"

Usage (repo root, after open_telemetry_pr.py):
    python selfheal/harness/monitor_preview.py --out DIR
Reads OUT/telemetry.json and OUT/alert.json; writes OUT/monitor_preview.json. The org's Sentry
token is only used to look up the project's ID (read-only); without it the link has no project.
"""
import argparse
import json
import os
import sys
import urllib.parse

import report  # same directory: python puts the script's folder on sys.path
import slack_channels
import telemetry_spec


def project_id(org, slug):
    """The project's numeric ID (the form's project field), or None if it can't be read."""
    if not slug:
        return None
    found, _ = slack_channels.sentry_get(org, f"/projects/{org}/{slug}/")
    return str(found["id"]) if isinstance(found, dict) and found.get("id") else None


def preview_url(org, spec, project=None):
    params = {"detectorType": "metric_issue", "dataset": "metrics",
              "aggregate": spec["monitor"]["sentry_aggregate"]}
    if project:
        params["project"] = project
    return f"https://{org}.sentry.io/monitors/new/settings/?{urllib.parse.urlencode(params)}"


def slack_text(url, spec, window_seconds):
    monitor = spec["monitor"]
    threshold = monitor["threshold"]
    threshold = int(threshold) if float(threshold).is_integer() else threshold
    label = f" {monitor['unit_label']}" if monitor["unit_label"] else ""
    return (f"<{url}|Preview monitor>: {monitor['aggregate']} of {spec['metric']['name']} over"
            f" {int(window_seconds) // 60} min · set the threshold to *{threshold}*{label}"
            f" · open to review and create")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    alert = report.load(os.path.join(args.out, "alert.json"))
    settings = json.loads(os.environ.get("TARGET_TELEMETRY") or "{}")
    try:
        spec = telemetry_spec.load(args.out)
    except telemetry_spec.SpecError as err:
        print(f"::warning title=No monitor preview::{err}", flush=True)
        sys.exit(1)

    org = alert.get("org") or os.environ.get("SENTRY_ORG") or "demo"
    window = int(settings.get("window_seconds") or 300)
    project = project_id(org, settings.get("project") or os.environ.get("SENTRY_PROJECT"))
    if not project:
        print("::warning title=Monitor preview::Couldn't look up the project's ID; the form will ask for"
              " the project", flush=True)
    url = preview_url(org, spec, project)
    with open(os.path.join(args.out, "monitor_preview.json"), "w") as f:
        json.dump({"url": url, "aggregate": spec["monitor"]["sentry_aggregate"],
                   "threshold": spec["monitor"]["threshold"], "window_seconds": window}, f, indent=2)
    print(f"Monitor preview: {url}", flush=True)
    report.post_status(slack_text(url, spec, window), alert)


if __name__ == "__main__":
    main()
