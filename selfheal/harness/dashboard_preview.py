"""An unsaved Sentry dashboard for the critical flow the telemetry agent instrumented, laid out like
demo's Critical Experience dashboard: one row per funnel stage, with the step to the next stage,
the stage's custom metric, its FE/BE latency and the issues behind its errors.

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

# Laid out like demo's Critical Experience dashboard (134148): one row per funnel stage on Sentry's
# 6-column grid, each 2 high: the funnel step (this stage vs the next) at x 0 (w 2), the stage's
# custom metric at x 2 (w 1), p95 latency with FE and BE as separate series at x 3 (w 1), and the
# issues behind its errors at x 4 (w 2). A last row holds the alert's metric and warning/error logs.
ROW_HEIGHT = 2


def query(conditions, aggregate, name="", columns=(), orderby=""):
    return {"name": name, "fields": [*columns, aggregate], "aggregates": [aggregate], "columns": list(columns),
            "conditions": conditions, "orderby": orderby}


def widget(title, widget_type, display_type, queries, x, y, w, description="", limit=5):
    return {
        "title": title[:255], "description": description[:255], "displayType": display_type,
        "widgetType": widget_type, "interval": "1h", "limit": limit, "queries": queries,
        "layout": {"x": x, "y": y, "w": w, "h": ROW_HEIGHT, "minH": ROW_HEIGHT},
    }


def scoped(conditions, scope):
    """The stage's conditions, narrowed to the dashboard's traffic filter (like 134148's has:cexp)."""
    return f"({conditions}) {scope}" if scope and conditions else conditions or scope


def stage_widgets(number, stage, following, y, scope=""):
    """The row for one stage: funnel step, custom metric, p95 latency (FE/BE), errors by issue."""
    name = stage["name"]
    funnel = [query(scoped(stage["span_query"], scope), "count(span.duration)", name=name)]
    funnel_title = f"{number}. {name}"
    if following:
        funnel.append(query(scoped(following["span_query"], scope), "count(span.duration)", name=following["name"]))
        funnel_title += f" vs {following['name']}"
    latency = [query(scoped(stage[f"{side}_query"], scope), "p95(span.duration)", name=label)
               for side, label in (("frontend", "FE"), ("backend", "BE")) if stage[f"{side}_query"]]
    metric = stage["sentry_metric_aggregate"]
    return [
        widget(funnel_title, "spans", "area", funnel, 0, y, 2,
               "This stage vs the next (spans per hour): the gap is the drop-off"),
        widget(f"{name}: {stage['metric_aggregate']}({stage['metric']})", "tracemetrics", "area",
               [query(scope, metric, orderby=metric)], 2, y, 1, "The stage's application metric"),
        widget(f"{name}: p95 latency", "spans", "line", latency, 3, y, 1, "Browser (FE) and agent (BE) spans"),
        widget(f"Errors in {name}", "error-events", "area",
               [query(scoped(stage["error_query"], scope), "count()", columns=("issue", "title"), orderby="-count()")],
               4, y, 2, "The issues behind this stage's errors", limit=10),
    ]


def extras_row(spec, y, scope=""):
    """Like 134148's last row: the metric behind the alert, and warning/error logs."""
    monitor = spec["monitor"]
    metric = monitor["sentry_aggregate"]
    return [
        widget(f"Alert metric: {monitor['aggregate']}({monitor['metric']})", "tracemetrics", "line",
               [query(scope, metric, orderby=metric)], 0, y, 3,
               f"Proposed monitor: critical above {monitor['threshold']}"),
        widget("Agent logs WARN/ERROR", "logs", "area",
               [query(scoped("severity:[warn,error]", scope), "count()", columns=("severity",), orderby="-count()")],
               3, y, 3, "Warnings and errors logged along the flow"),
    ]


def build_dashboard(spec, settings, project_ids=()):
    """The dashboard as Sentry's dashboards API takes it: a row per stage, top to bottom."""
    board = settings.get("dashboard") or {}
    scope = " ".join(str(board.get("filter") or "").split())
    stages, widgets = spec["stages"], []
    for number, stage in enumerate(stages, 1):
        following = stages[number] if number < len(stages) else None
        widgets += stage_widgets(number, stage, following, (number - 1) * ROW_HEIGHT, scope)
    widgets += extras_row(spec, len(stages) * ROW_HEIGHT, scope)
    dashboard = {"title": (board.get("title") or "Critical experience")[:255], "widgets": widgets,
                 "projects": [int(p) for p in project_ids], "period": "24h"}
    if board.get("environment"):
        dashboard["environment"] = [board["environment"]]
    return dashboard


def prompt(spec, dashboard):
    stages = "; ".join(f"{n}. {s['name']}" for n, s in enumerate(spec["stages"], 1))
    return (f"Build the dashboard \"{dashboard['title']}\" exactly as given in the current dashboard: keep every "
            f"widget, title, query, dataset, display type and layout, in the same order. Don't add, remove or "
            f"rename widgets. It follows one user flow, one row per stage ({stages}), laid out like a Critical "
            f"Experience dashboard: each row shows the funnel step from this stage to the next, the stage's "
            f"custom application metric, its p95 latency with frontend and backend as separate series, and "
            f"the issues behind its errors. The last row has the alert's metric and warning/error logs.")


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
    return (f"*Dashboard preview* 📊: <{url}|{dashboard['title']}> · {stages} stages, each with funnel step,"
            f" metric, FE/BE latency and errors · not saved")


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
