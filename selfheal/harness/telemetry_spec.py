"""The telemetry agent's proposal (OUT/telemetry.json): the metric it added and the monitor for it.

The agent proposes; the harness checks the proposal here before it opens the PR or creates
anything in Sentry, so a bad value can't reach Sentry's API.
"""
import json
import os
import re

NAME_RE = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+$")  # dotted lowercase, e.g. agent.policy.documents
# The agent's metric type -> the type in Sentry's metric aggregates, and the aggregates it supports
TYPES = {
    "distribution": ("distribution", {"max", "min", "avg", "sum", "count", "p50", "p90", "p95", "p99"}),
    "count": ("counter", {"sum", "count"}),
    "gauge": ("gauge", {"max", "min", "avg", "sum", "count"}),
}


class SpecError(ValueError):
    pass


def load(out):
    """The validated proposal, with the monitor's aggregate filled in. Raises SpecError."""
    try:
        with open(os.path.join(out, "telemetry.json")) as f:
            spec = json.load(f)
    except (OSError, json.JSONDecodeError) as err:
        raise SpecError(f"no readable telemetry.json ({err})")
    metric, monitor = spec.get("metric") or {}, spec.get("monitor") or {}

    name = str(metric.get("name") or "")
    if not NAME_RE.match(name) or len(name) > 100:
        raise SpecError(f"metric name {name!r} isn't dotted lowercase (e.g. agent.policy.documents)")
    kind = str(metric.get("type") or "distribution")
    if kind not in TYPES:
        raise SpecError(f"metric type {kind!r} isn't one of {', '.join(TYPES)}")
    sentry_type, aggregates = TYPES[kind]
    aggregate = str(monitor.get("aggregate") or "max")
    if aggregate not in aggregates:
        raise SpecError(f"aggregate {aggregate!r} doesn't apply to a {kind} (use {', '.join(sorted(aggregates))})")
    threshold = monitor.get("threshold")
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)) or threshold <= 0:
        raise SpecError(f"threshold {threshold!r} isn't a positive number")
    unit = str(metric.get("unit") or "none")
    if not re.match(r"^[a-z_]+$", unit):
        raise SpecError(f"unit {unit!r} isn't a Sentry unit name")

    spec["metric"] = {**metric, "name": name, "type": kind, "unit": unit}
    spec["monitor"] = {
        **monitor, "aggregate": aggregate, "threshold": threshold,
        "unit_label": str(monitor.get("unit_label") or "")[:30],
        # Sentry's aggregate over application metrics: fn(value,<name>,<type>,<unit or ->)
        "sentry_aggregate": f"{aggregate}(value,{name},{sentry_type},{'-' if unit == 'none' else unit})",
    }
    return spec


def describe(spec, window_seconds):
    """'max > 10 documents in 5 min', for Slack and the PR."""
    monitor = spec["monitor"]
    threshold = monitor["threshold"]
    threshold = int(threshold) if float(threshold).is_integer() else threshold
    label = f" {monitor['unit_label']}" if monitor["unit_label"] else ""
    return f"{monitor['aggregate']} > {threshold}{label} in {int(window_seconds) // 60} min"
