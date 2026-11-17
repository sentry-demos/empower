"""An unsaved Sentry dashboard for the critical flow the telemetry agent instrumented: one row per
funnel stage, with its throughput, its custom metric, its latency and its errors.

Nothing is saved in Sentry (so SEs demoing at once don't each leave a dashboard behind). Sentry
shows an unsaved, pre-filled dashboard only through its "create dashboard with Seer" flow:
POST /organizations/{org}/dashboards/generate/ with a prompt and the dashboard as
`current_dashboard` starts a run, and
    https://{org}.sentry.io/dashboards/new/from-seer/?seerRunId=<run_id>
opens the result in preview mode, where a person can save it or leave it.

Usage (repo root, after open_telemetry_pr.py):
    python selfheal/harness/dashboard_preview.py --out DIR
Reads OUT/telemetry.json, OUT/alert.json and OUT/telemetry_verify.json; writes OUT/dashboard.json
and OUT/dashboard_preview.json. Needs the org's Sentry token (SENTRY_MCP_TOKEN[_<ORG>]).
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

import report  # same directory: python puts the script's folder on sys.path
import slack_channels
import telemetry_spec

# Each stage is one row of Sentry's 6-column grid: (kind, width, display type)
ROW = (("throughput", 1, "big_number"), ("metric", 2, "line"), ("latency", 2, "line"), ("errors", 1, "big_number"))
ROW_HEIGHT = 2


def widget(title, widget_type, display_type, aggregate, conditions, x, y, w, description=""):
    return {
        "title": title[:255], "description": description[:255], "displayType": display_type,
        "widgetType": widget_type, "interval": "1h", "limit": None,
        "queries": [{"name": "", "fields": [aggregate], "aggregates": [aggregate], "columns": [],
                     "conditions": conditions, "orderby": ""}],
        "layout": {"x": x, "y": y, "w": w, "h": ROW_HEIGHT, "minH": ROW_HEIGHT},
    }


def stage_widgets(number, stage, y):
    """The row for one stage: throughput, its custom metric, latency (p95), errors."""
    name = f"{number}. {stage['name']}"
    span_query, error_query = stage["span_query"], stage["error_query"]
    cells = {
        "throughput": ("spans", "count()", span_query, f"{name} · throughput",
                       "How often this stage runs (spans matching the stage)"),
        "metric": ("tracemetrics", stage["sentry_metric_aggregate"], "",
                   f"{name} · {stage['metric_aggregate']}({stage['metric']})", "The stage's application metric"),
        "latency": ("spans", "p95(span.duration)", span_query, f"{name} · p95 latency",
                    "Browser and agent spans for this stage"),
        "errors": ("error-events", "count()", error_query, f"{name} · errors", "Errors in this stage's code"),
    }
    widgets, x = [], 0
    for kind, width, display in ROW:
        widget_type, aggregate, conditions, title, description = cells[kind]
        widgets.append(widget(title, widget_type, display, aggregate, conditions, x, y, width, description))
        x += width
    return widgets


def build_dashboard(spec, settings, project_ids=()):
    """The dashboard as Sentry's dashboards API takes it: a row per stage, top to bottom."""
    board = settings.get("dashboard") or {}
    widgets = []
    for number, stage in enumerate(spec["stages"], 1):
        widgets += stage_widgets(number, stage, (number - 1) * ROW_HEIGHT)
    dashboard = {"title": (board.get("title") or "Critical experience")[:255], "widgets": widgets,
                 "projects": [int(p) for p in project_ids], "period": "24h"}
    if board.get("environment"):
        dashboard["environment"] = [board["environment"]]
    return dashboard


def prompt(spec, dashboard):
    stages = "; ".join(f"{n}. {s['name']}" for n, s in enumerate(spec["stages"], 1))
    return (f"Build the dashboard \"{dashboard['title']}\" exactly as given in the current dashboard: keep every "
            f"widget, title, query, dataset, display type and layout, in the same order. Don't add, remove or "
            f"rename widgets. It follows one user flow, one row per stage ({stages}); each row shows the "
            f"stage's throughput, its custom application metric, its p95 latency across browser and backend "
            f"spans, and its errors.")


def project_ids(org, slugs):
    found = []
    for slug in slugs:
        project, _ = slack_channels.sentry_get(org, f"/projects/{org}/{slug}/")
        if isinstance(project, dict) and project.get("id"):
            found.append(str(project["id"]))
    return found


def start_preview(org, body):
    """(run_id, None) or (None, reason): starts Sentry's dashboard generation, which saves nothing."""
    token = slack_channels.sentry_token(org)
    if not token:
        return None, "no Sentry token for the org"
    api = os.environ.get("SENTRY_API_URL", "https://sentry.io/api/0").rstrip("/")
    request = urllib.request.Request(
        f"{api}/organizations/{org}/dashboards/generate/", data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            run_id = (json.load(response) or {}).get("run_id")
    except urllib.error.HTTPError as err:
        detail = err.read()[:200].decode(errors="replace")
        return None, f"HTTP {err.code} from dashboards/generate: {detail}"
    except (OSError, ValueError) as err:
        return None, f"dashboards/generate failed: {err}"
    return (run_id, None) if run_id else (None, "dashboards/generate returned no run_id")


def preview_url(org, run_id):
    return f"https://{org}.sentry.io/dashboards/new/from-seer/?seerRunId={run_id}"


def slack_text(url, dashboard, stages):
    return (f"*Dashboard preview* 📊: <{url}|{dashboard['title']}> · {stages} stages, each with throughput,"
            f" metric, latency and errors · not saved")


def fallback_text(pr_url):
    where = f" in <{pr_url}|the telemetry PR>" if pr_url else ""
    return f"*Dashboard preview*: couldn't open one in Sentry; the dashboard JSON is{where} to import"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    alert = report.load(os.path.join(args.out, "alert.json"))
    settings = json.loads(os.environ.get("TARGET_TELEMETRY") or "{}")
    try:
        spec = telemetry_spec.load(args.out)
    except telemetry_spec.SpecError as err:
        print(f"::warning title=No dashboard preview::{err}", flush=True)
        sys.exit(1)

    org = alert.get("org") or os.environ.get("SENTRY_ORG") or "demo"
    slugs = (settings.get("dashboard") or {}).get("projects") or []
    dashboard = build_dashboard(spec, settings, project_ids(org, slugs))
    with open(os.path.join(args.out, "dashboard.json"), "w") as f:
        json.dump(dashboard, f, indent=2)

    run_id, reason = start_preview(org, {"prompt": prompt(spec, dashboard), "current_dashboard": dashboard})
    result = {"run_id": run_id, "url": preview_url(org, run_id) if run_id else None, "error": reason,
              "stages": len(spec["stages"]), "widgets": len(dashboard["widgets"])}
    with open(os.path.join(args.out, "dashboard_preview.json"), "w") as f:
        json.dump(result, f, indent=2)

    if run_id:
        print(f"Dashboard preview: {result['url']}", flush=True)
        report.post_status(slack_text(result["url"], dashboard, len(spec["stages"])), alert)
    else:
        print(f"::warning title=No dashboard preview::{reason}", flush=True)
        pr_url = report.load(os.path.join(args.out, "telemetry_verify.json")).get("pr_url")
        report.post_status(fallback_text(pr_url), alert)
        sys.exit(1)


if __name__ == "__main__":
    main()
