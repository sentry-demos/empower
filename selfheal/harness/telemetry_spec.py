"""The telemetry agent's proposal (OUT/telemetry.json): the metrics it added along the critical
flow, the funnel stages for the dashboard, and the monitor for the metric behind the alert.

The agent proposes; the harness checks the proposal here before it opens the PR or sends
anything to Sentry, so a bad value can't reach Sentry's API.

    {
      "metrics": [{"name": "agent.policy.documents", "type": "distribution", "unit": "none",
                   "attributes": ["tool"], "file": "agent/app/tools/shop/policies.py", "new": true}, ...],
      "monitor": {"metric": "agent.policy.documents", "aggregate": "max", "threshold": 10,
                  "unit_label": "documents", "reasoning": "..."},
      "stages": [{"name": "Policy search", "frontend_query": "", "backend_query": "...",
                  "metric": "agent.policy.documents", "metric_aggregate": "p95", "error_query": "..."}, ...],
      "summary": "..."
    }
"""
import json
import os
import re

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")  # dotted lowercase, e.g. agent.policy.documents
# The agent's metric type -> the type in Sentry's metric aggregates, and the aggregates it supports
TYPES = {
    "distribution": ("distribution", {"max", "min", "avg", "sum", "count", "p50", "p75", "p90", "p95", "p99"}),
    "count": ("counter", {"sum", "count"}),
    "gauge": ("gauge", {"max", "min", "avg", "sum", "count"}),
}
MIN_STAGES, MAX_STAGES = 3, 8
MAX_QUERY = 300


class SpecError(ValueError):
    pass


def sentry_aggregate(aggregate, metric):
    """Sentry's aggregate over an application metric: fn(value,<name>,<type>,<unit or ->)."""
    unit = metric["unit"]
    return f"{aggregate}(value,{metric['name']},{TYPES[metric['type']][0]},{'-' if unit == 'none' else unit})"


def _metric(raw):
    name = str(raw.get("name") or "")
    if not NAME_RE.match(name) or len(name) > 100:
        raise SpecError(f"metric name {name!r} isn't dotted lowercase (e.g. agent.policy.documents)")
    kind = str(raw.get("type") or "distribution")
    if kind not in TYPES:
        raise SpecError(f"metric {name}: type {kind!r} isn't one of {', '.join(TYPES)}")
    unit = str(raw.get("unit") or "none")
    if not re.match(r"^[a-z_]+$", unit):
        raise SpecError(f"metric {name}: unit {unit!r} isn't a Sentry unit name")
    return {**raw, "name": name, "type": kind, "unit": unit, "new": raw.get("new", True) is not False}


def _query(stage, key):
    value = " ".join(str(stage.get(key) or "").split())
    if len(value) > MAX_QUERY:
        raise SpecError(f"stage {stage.get('name')!r}: {key} is longer than {MAX_QUERY} characters")
    return value


def _aggregate(metric, aggregate, where):
    aggregates = TYPES[metric["type"]][1]
    if aggregate not in aggregates:
        raise SpecError(f"{where}: aggregate {aggregate!r} doesn't apply to a {metric['type']}"
                        f" (use {', '.join(sorted(aggregates))})")
    return aggregate


def load(out):
    """The validated proposal, with Sentry's aggregates filled in. Raises SpecError."""
    try:
        with open(os.path.join(out, "telemetry.json")) as f:
            spec = json.load(f)
    except (OSError, json.JSONDecodeError) as err:
        raise SpecError(f"no readable telemetry.json ({err})")

    metrics = [_metric(m) for m in spec.get("metrics") or [] if isinstance(m, dict)]
    if not any(m["new"] for m in metrics):
        raise SpecError("no new metrics: list each one the change adds, with \"new\": true")
    by_name = {}
    for metric in metrics:
        if metric["name"] in by_name:
            raise SpecError(f"metric {metric['name']} is listed twice")
        by_name[metric["name"]] = metric

    monitor = spec.get("monitor") or {}
    watched = by_name.get(str(monitor.get("metric") or ""))
    if not watched:
        raise SpecError(f"monitor.metric {monitor.get('metric')!r} isn't one of the listed metrics")
    aggregate = _aggregate(watched, str(monitor.get("aggregate") or "max"), "monitor")
    threshold = monitor.get("threshold")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or threshold <= 0:
        raise SpecError(f"threshold {threshold!r} isn't a positive number")

    stages = []
    for raw in spec.get("stages") or []:
        if not isinstance(raw, dict):
            continue
        name = " ".join(str(raw.get("name") or "").split())[:60]
        if not name:
            raise SpecError("a stage has no name")
        metric = by_name.get(str(raw.get("metric") or ""))
        if not metric:
            raise SpecError(f"stage {name!r}: metric {raw.get('metric')!r} isn't one of the listed metrics")
        stage_aggregate = _aggregate(metric, str(raw.get("metric_aggregate") or ("sum" if metric["type"] == "count" else "p95")),
                                     f"stage {name!r}")
        frontend, backend = _query(raw, "frontend_query"), _query(raw, "backend_query")
        if not (frontend or backend):
            raise SpecError(f"stage {name!r} has neither a frontend_query nor a backend_query")
        error_query = _query(raw, "error_query")
        if not error_query:
            raise SpecError(f"stage {name!r} has no error_query (scope it to the stage's page or code)")
        stages.append({**raw, "name": name, "metric": metric["name"], "metric_aggregate": stage_aggregate,
                       "frontend_query": frontend, "backend_query": backend, "error_query": error_query,
                       "span_query": f"({frontend}) OR ({backend})" if frontend and backend else frontend or backend,
                       "sentry_metric_aggregate": sentry_aggregate(stage_aggregate, metric)})
    if not MIN_STAGES <= len(stages) <= MAX_STAGES:
        raise SpecError(f"{len(stages)} stages; the dashboard needs {MIN_STAGES} to {MAX_STAGES}")

    spec["metrics"] = metrics
    spec["stages"] = stages
    spec["metric"] = watched  # the metric the monitor watches
    spec["monitor"] = {
        **monitor, "metric": watched["name"], "aggregate": aggregate, "threshold": threshold,
        "unit_label": str(monitor.get("unit_label") or "")[:30],
        "sentry_aggregate": sentry_aggregate(aggregate, watched),
    }
    return spec


def describe(spec, window_seconds):
    """'max > 10 documents in 5 min', for Slack and the PR."""
    monitor = spec["monitor"]
    threshold = monitor["threshold"]
    threshold = int(threshold) if float(threshold).is_integer() else threshold
    label = f" {monitor['unit_label']}" if monitor["unit_label"] else ""
    return f"{monitor['aggregate']} > {threshold}{label} in {int(window_seconds) // 60} min"
