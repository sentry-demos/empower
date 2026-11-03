"""The progress lines the fix job posts in the alert's Slack thread.

Run from the repo root: python -m pytest selfheal/harness
"""
import json
import os
import sys
from argparse import Namespace

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report  # noqa: E402

ISSUE = "https://team-se.sentry.io/issues/7825689300/"

# The Sentry calls behind PR #1721, as run_agent.py records them in timeline.json
TIMELINE = [
    {"type": "tool", "name": "ToolSearch", "input": {}, "at_s": 9.0, "seconds": 0.5, "error": False},
    {"type": "tool", "name": "mcp__sentry__get_sentry_resource", "at_s": 13.8, "seconds": 1.2, "error": False,
     "input": {"resourceType": "issue", "resourceId": "7813412119"}},
    {"type": "tool", "name": "mcp__sentry__get_sentry_resource", "at_s": 20.0, "seconds": 0.6, "error": False,
     "input": {"resourceType": "trace", "resourceId": "4a864dae24f0401393d0606d38613550"}},
    {"type": "tool", "name": "mcp__sentry__search_events", "at_s": 20.8, "seconds": 3.1, "error": False,
     "input": {"dataset": "spans", "query": "span.op:gen_ai.chat"}},
    {"type": "tool", "name": "mcp__sentry__search_events", "at_s": 30.7, "seconds": 0.4, "error": True,
     "input": {"dataset": "spans", "query": "trace:82f36e2bfa854f5eaa78876e6e75dd01"}},
    {"type": "tool", "name": "mcp__sentry__search_events", "at_s": 49.6, "seconds": 2.0, "error": False,
     "input": {"dataset": "spans", "query": "span.op:gen_ai.execute_tool"}},
    {"type": "tool", "name": "mcp__sentry__execute_sentry_tool", "at_s": 55.0, "seconds": 1.0, "error": False,
     "input": {"name": "search_logs", "arguments": {"query": "policy"}}},
    {"type": "note", "text": "Baseline check fails at 47.2k tokens."},
    {"type": "tool", "name": "Read", "input": {"file_path": "agent/app/tools/shop/policies.py"},
     "at_s": 60.0, "seconds": 0.1, "error": False},
]


@pytest.fixture
def no_slack(monkeypatch):
    for name in ("SELFHEAL_SLACK_BOT_TOKEN", "SELFHEAL_SLACK_CHANNEL", "SELFHEAL_SLACK_WEBHOOK_URL"):
        monkeypatch.delenv(name, raising=False)


def run_dir(tmp_path, **files):
    files.setdefault("alert.json", {"issue_id": "7825689300", "url": ISSUE})
    for name, content in files.items():
        (tmp_path / name).write_text(json.dumps(content))
    return str(tmp_path)


def test_sentry_summary_names_what_the_agent_read():
    assert report.sentry_summary(TIMELINE, "KUNAL-MANAGER-AGENT-7") == (
        "Investigated KUNAL-MANAGER-AGENT-7 with 5 Sentry MCP calls (56s): read the issue, 1 trace,"
        " 2 span searches and 1 log search.")


def test_sentry_summary_is_empty_without_sentry_calls():
    assert report.sentry_summary([t for t in TIMELINE if not t.get("name", "").startswith("mcp__")], "X-1") == ""


def test_without_seer_status(tmp_path, no_slack, capsys):
    out = run_dir(tmp_path, **{"timeline.json": TIMELINE, "result.json": {"issue_short_id": "KUNAL-MANAGER-AGENT-7"}})
    report.report_status(Namespace(kind="sentry", variant="without-seer", dir=out))
    assert capsys.readouterr().out.startswith(
        "🔎 *Sentry telemetry* · Investigated KUNAL-MANAGER-AGENT-7 with 5 Sentry MCP calls")


def test_seer_status(tmp_path, no_slack, capsys):
    handoff = {"issue": {"short_id": "BACKEND-FLASK-JJ"},
               "seer": {"run_id": 42, "reused": True, "seconds": 2.4,
                        "root_cause": "In checkout(), `quantities` is read before it is assigned. The guard..."}}
    report.report_status(Namespace(kind="seer", variant="with-seer", dir=run_dir(tmp_path, **{"handoff.json": handoff})))
    assert capsys.readouterr().out.splitlines()[0] == (
        "🔎 *Seer root cause* · pulled BACKEND-FLASK-JJ, its logs and impact from Sentry, then queried"
        " Seer (its earlier analysis, 2s): In checkout(), `quantities` is read before it is assigned.")


def test_opening_pr_status(tmp_path, no_slack, capsys):
    check = {"tests_passed": True, "replay_status": None, "check_passed": True,
             "check_label": "policy answer under the token budget"}
    report.report_opening_pr("without-seer", run_dir(tmp_path), check)
    assert capsys.readouterr().out.splitlines()[0] == (
        "*Opening draft PR* · fix verified: tests pass, policy answer under the token budget")


def test_slack_failure_never_fails_the_step(tmp_path, monkeypatch, capsys):
    def refuse(*args, **kwargs):
        raise RuntimeError("Slack chat.postMessage failed: not_in_channel")
    monkeypatch.setattr(report, "post", refuse)
    report.post_status("hello", {})
    assert "Status message not posted" in capsys.readouterr().out


def test_fix_ready_footer_has_no_version(tmp_path, no_slack, capsys):
    out = run_dir(tmp_path, **{"stats.json": {"duration_s": 132.0, "cost_usd": 0.46},
                               "verify.json": {"tests_passed": True, "check_passed": True,
                                               "check_label": "policy answer under the token budget"},
                               "result.json": {"impact_short": "~47.8k input tokens per policy question",
                                               "root_cause_short": "search_policies returns every page"}})
    review = tmp_path / "review.md"
    review.write_text("**Verdict: MERGE**\n")
    report.report_review(Namespace(pr_url="https://github.com/o/r/pull/1725", review=str(review),
                                   variant="without-seer", results=out))
    assert capsys.readouterr().out.splitlines()[3] == (
        "tests pass, policy answer under the token budget · reviewer: MERGE · 132s, $0.46")


DASHBOARD = ("https://demo.sentry.io/dashboard/510044/?project=5808623&project=4508968134377472"
             "&statsPeriod=7d")


@pytest.fixture
def dashboard(monkeypatch):
    monkeypatch.setenv("TARGET_DASHBOARD_URL", DASHBOARD)
    monkeypatch.setenv("TARGET_DASHBOARD_LABEL", "Critical Experience dashboard")


def test_metric_alert_gets_the_dashboard_link(tmp_path, no_slack, dashboard, capsys):
    # Monitors & Alerts: a metric alert arrives as an issue alert on a metric issue
    out = run_dir(tmp_path, **{"alert.json": {"kind": "event_alert", "issue_id": "7825689300", "org": "team-se"}})
    seen = []
    report.report_dashboard(out, lookup=lambda issue_id, org: seen.append((issue_id, org)) or "metric")
    assert seen == [("7825689300", "team-se")]
    assert capsys.readouterr().out.splitlines()[0] == (
        "📊 See the impact on the <https://demo.sentry.io/dashboard/510044/?project=5808623"
        "&amp;project=4508968134377472&amp;statsPeriod=7d|Critical Experience dashboard>")


def test_legacy_metric_alert_needs_no_lookup(tmp_path, no_slack, dashboard, capsys):
    out = run_dir(tmp_path, **{"alert.json": {"kind": "metric_alert", "title": "Revenue drop"}})
    report.report_dashboard(out, lookup=lambda *a: pytest.fail("no lookup needed"))
    assert "Critical Experience dashboard" in capsys.readouterr().out


@pytest.mark.parametrize("category", ["error", ""])  # "" when Sentry can't be reached
def test_error_alert_gets_no_dashboard_link(tmp_path, no_slack, dashboard, capsys, category):
    out = run_dir(tmp_path, **{"alert.json": {"kind": "event_alert", "issue_id": "7817323193", "org": "demo"}})
    report.report_dashboard(out, lookup=lambda *a: category)
    assert capsys.readouterr().out == ""


def test_no_dashboard_configured_posts_nothing(tmp_path, no_slack, monkeypatch, capsys):
    monkeypatch.delenv("TARGET_DASHBOARD_URL", raising=False)
    report.report_dashboard(run_dir(tmp_path, **{"alert.json": {"kind": "metric_alert"}}))
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("org,expected", [("demo", "checkout"), ("team-se", "agent-context")])
def test_targets_carry_the_dashboard(org, expected):
    import target
    name, config = target.resolve({"org": org}, target.load_targets())
    lines = target.env_lines(name, config, {"org": org})
    assert name == expected
    assert lines["TARGET_DASHBOARD_URL"].startswith("https://demo.sentry.io/dashboard/510044/")
    assert lines["TARGET_DASHBOARD_LABEL"] == "Critical Experience dashboard"
