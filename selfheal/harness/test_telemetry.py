"""The telemetry follow-up: the agent's proposal, the instrumentation PR, and the monitor.

Run from the repo root: python -m pytest selfheal/harness
"""
import json
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import create_monitor  # noqa: E402
import open_telemetry_pr  # noqa: E402
import prepare  # noqa: E402
import report  # noqa: E402
import target  # noqa: E402
import telemetry_spec  # noqa: E402

SPEC = {
    "metric": {"name": "agent.policy.documents", "type": "distribution", "unit": "none", "attributes": ["tool"],
               "file": "agent/app/tools/shop/policies.py"},
    "monitor": {"aggregate": "max", "threshold": 10, "unit_label": "documents",
                "reasoning": "Normal answers use 3 or fewer pages; the spike sent all 50."},
    "summary": "search_policies now reports how many pages it sends to the agent.",
}
ALERT = {"org": "team-se", "rule": "Notify via selfheal", "issue_id": "7825689300",
         "title": "Chris LLM Context Snowball — max input tokens spike"}
SETTINGS = {"goal": "the number of help-centre documents", "project": "kunal-manager-agent",
            "window_seconds": 300, "frequency_minutes": 5}
SLACK_ACTION = {"id": "17582152", "type": "slack", "integrationId": "1", "status": "active", "data": {},
                "config": {"targetType": "specific", "targetDisplay": "demo-selfhealing", "targetIdentifier": "C0CCD3THU0H"}}
WEBHOOK_ACTION = {"id": "17582151", "type": "webhook", "integrationId": None, "data": {},
                  "config": {"targetIdentifier": "selfheal-4cd71e"}}


def write(tmp_path, **files):
    for name, content in files.items():
        (tmp_path / name).write_text(content if isinstance(content, str) else json.dumps(content))
    return str(tmp_path)


@pytest.fixture
def no_slack(monkeypatch):
    for name in ("SELFHEAL_SLACK_BOT_TOKEN", "SELFHEAL_SLACK_CHANNEL", "SELFHEAL_SLACK_CHANNELS"):
        monkeypatch.delenv(name, raising=False)


# --- the proposal ---------------------------------------------------------------------------

def test_spec_builds_sentrys_metric_aggregate(tmp_path):
    spec = telemetry_spec.load(write(tmp_path, **{"telemetry.json": SPEC}))
    # The same syntax Sentry's Explore uses for application metrics
    assert spec["monitor"]["sentry_aggregate"] == "max(value,agent.policy.documents,distribution,-)"
    assert telemetry_spec.describe(spec, 300) == "max > 10 documents in 5 min"


def test_counter_metric_uses_sentrys_counter_type(tmp_path):
    spec = {**SPEC, "metric": {**SPEC["metric"], "type": "count"}, "monitor": {**SPEC["monitor"], "aggregate": "sum"}}
    loaded = telemetry_spec.load(write(tmp_path, **{"telemetry.json": spec}))
    assert loaded["monitor"]["sentry_aggregate"] == "sum(value,agent.policy.documents,counter,-)"


@pytest.mark.parametrize("change, error", [
    ({"metric": {**SPEC["metric"], "name": "Documents Sent"}}, "dotted lowercase"),
    ({"metric": {**SPEC["metric"], "name": "agent.docs,distribution),count("}}, "dotted lowercase"),
    ({"metric": {**SPEC["metric"], "type": "histogram"}}, "metric type"),
    ({"monitor": {**SPEC["monitor"], "aggregate": "p95"}, "metric": {**SPEC["metric"], "type": "gauge"}}, "doesn't apply"),
    ({"monitor": {**SPEC["monitor"], "threshold": 0}}, "positive number"),
    ({"monitor": {**SPEC["monitor"], "threshold": "10"}}, "positive number"),
    ({"metric": {**SPEC["metric"], "unit": "docs; drop"}}, "unit"),
])
def test_bad_proposals_never_reach_sentry(tmp_path, change, error):
    with pytest.raises(telemetry_spec.SpecError, match=error):
        telemetry_spec.load(write(tmp_path, **{"telemetry.json": {**SPEC, **change}}))


# --- the instrumentation PR -----------------------------------------------------------------

@pytest.mark.parametrize("added, emits", [
    (['    sentry_sdk.metrics.distribution("agent.policy.documents", len(pages), attributes={"tool": "search_policies"})'], True),
    (["    sentry_sdk.metrics.distribution(", '        "agent.policy.documents",', "        len(pages),", "    )"], True),
    (['    sentry_sdk.metrics.distribution("agent.policy.pages", len(pages))'], False),   # another name
    (['    sentry_sdk.metrics.count("agent.policy.documents", 1)'], False),               # another type
    (['    # TODO: emit agent.policy.documents via sentry_sdk.metrics.distribution'], False),
])
def test_harness_checks_the_code_really_emits_the_metric(tmp_path, added, emits):
    spec = telemetry_spec.load(write(tmp_path, **{"telemetry.json": SPEC}))
    assert open_telemetry_pr.emits_metric(added, spec) is emits


def test_blockers_name_every_problem():
    check = {"secrets_found": [], "in_scope": False, "tests_passed": False, "spec_error": None, "emits_metric": False}
    found = open_telemetry_pr.blockers(check)
    assert any("outside" in b for b in found) and "tests fail" in found
    assert any("doesn't emit" in b for b in found)


def test_slack_message_matches_fix_ready_for_review(tmp_path):
    spec = telemetry_spec.load(write(tmp_path, **{"telemetry.json": SPEC}))
    assert open_telemetry_pr.slack_text("https://github.com/sentry-demos/empower/pull/1751", spec) == (
        "*Telemetry improvement* 🔧: <https://github.com/sentry-demos/empower/pull/1751|PR #1751>\n"
        "Instrumented code to capture new application metric in Sentry · agent.policy.documents")


def test_pr_text_links_the_fix_and_never_closes_the_issue(tmp_path, monkeypatch):
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    out = write(tmp_path, **{"telemetry.json": SPEC,
                             "pr_body.md": "## Why\n\nThis fixes KUNAL-MANAGER-AGENT-7 for good.\n"})
    spec = telemetry_spec.load(out)
    check = {"files_changed": ["agent/app/tools/shop/policies.py"], "tests_summary": "50 passed"}
    fix = {"issue_short_id": "KUNAL-MANAGER-AGENT-7", "issue_url": "https://team-se.sentry.io/issues/KUNAL-MANAGER-AGENT-7"}
    title, message, body = open_telemetry_pr.pr_text(out, spec, check, "https://github.com/o/r/pull/1725", fix)
    assert title == "[telemetry] KUNAL-MANAGER-AGENT-7: measure agent.policy.documents as a Sentry application metric"
    assert message.startswith("Follows https://github.com/o/r/pull/1725")
    assert "_Telemetry follow-up to the self-heal fix in https://github.com/o/r/pull/1725._" in body
    assert "`max(value,agent.policy.documents,distribution,-)`, alerts when max > 10 documents in 5 min" in body
    assert "addresses KUNAL-MANAGER-AGENT-7" in body  # the agent's "fixes" was reworded


# --- the monitor ----------------------------------------------------------------------------

class FakeSentry:
    """Sentry's API for the calls create_monitor makes, recording what was sent."""

    def __init__(self, existing=(), workflows=(), fail=None):
        self.existing, self.workflows, self.fail = list(existing), list(workflows), fail
        self.sent = []

    def __call__(self, org, method, path, body=None, params=None):
        self.sent.append((method, path, body, params))
        if self.fail and self.fail in path and method == "POST":
            raise create_monitor.SentryError(f"POST {path}: HTTP 400: {{\"dataSources\": [\"invalid aggregate\"]}}")
        if path == f"/projects/{org}/kunal-manager-agent/":
            return {"id": "4512069456953344", "slug": "kunal-manager-agent"}
        # As Sentry does: monitors are listed per org but created under their project
        if path == f"/organizations/{org}/detectors/" and method == "GET":
            return self.existing
        if path == f"/organizations/{org}/detectors/":
            raise create_monitor.SentryError(f"POST {path}: HTTP 405: {{\"detail\":\"Method \\\"POST\\\" not allowed.\"}}")
        if path == f"/projects/{org}/kunal-manager-agent/detectors/":
            raise create_monitor.SentryError(f"POST {path}: HTTP 404: ")
        if path == f"/organizations/{org}/projects/kunal-manager-agent/detectors/" and method == "POST":
            return {"id": "10900001", **body}
        if path == f"/organizations/{org}/workflows/" and method == "POST":
            return {"id": "6300001", **body}
        raise AssertionError(f"unexpected Sentry call {method} {path}")

    def posted(self, suffix):
        return [body for method, path, body, _ in self.sent if method == "POST" and path.endswith(suffix)]


@pytest.fixture
def sentry(monkeypatch):
    def install(slack_actions=(SLACK_ACTION,), **kwargs):
        fake = FakeSentry(**kwargs)
        monkeypatch.setattr(create_monitor, "sentry", fake)
        monkeypatch.setattr(create_monitor.slack_channels, "alert_slack_actions", lambda alert: list(slack_actions))
        return fake
    return install


def test_creates_the_monitor_on_the_new_metric(tmp_path, sentry):
    fake = sentry()
    monitor = create_monitor.create(write(tmp_path, **{"telemetry.json": SPEC}), ALERT, SETTINGS)

    [detector] = fake.posted("/detectors/")
    # The same shape as Sentry's MCP create_metric_monitor sends
    assert detector["type"] == "metric_issue" and "projectId" not in detector
    assert detector["config"] == {"detectionType": "static", "comparisonDelta": None}
    assert detector["dataSources"] == [{
        "dataset": "events_analytics_platform", "query": "",
        "aggregate": "max(value,agent.policy.documents,distribution,-)",
        "environment": None, "eventTypes": ["trace_item_metric"], "timeWindow": 300}]
    assert detector["conditionGroup"]["conditions"] == [
        {"type": "gt", "comparison": 10, "conditionResult": 75},
        {"type": "lte", "comparison": 10, "conditionResult": 0}]
    assert monitor["url"] == "https://team-se.sentry.io/monitors/10900001/"
    assert (monitor["reused"], monitor["alert_id"]) == (False, "6300001")


def test_alert_copies_slack_actions_and_never_the_selfheal_webhook(tmp_path, sentry, monkeypatch):
    # alert_slack_actions is what filters; check it against the real "Notify via selfheal" shape
    monkeypatch.setattr(create_monitor.slack_channels, "alert_workflows",
                        lambda alert: [{"actionFilters": [{"actions": [WEBHOOK_ACTION, SLACK_ACTION]}]}])
    assert create_monitor.slack_channels.alert_slack_actions(ALERT) == [SLACK_ACTION]

    fake = sentry()
    create_monitor.create(write(tmp_path, **{"telemetry.json": SPEC}), ALERT, SETTINGS)
    [alert] = fake.posted("/workflows/")
    assert alert["detectorIds"] == ["10900001"] and alert["config"] == {"frequency": 5}
    assert alert["actionFilters"][0]["actions"] == [{
        "type": "slack", "integrationId": "1", "data": {},
        "config": {"targetType": "specific", "targetDisplay": "demo-selfhealing", "targetIdentifier": "C0CCD3THU0H"}}]


def test_existing_monitor_is_reused_not_duplicated(tmp_path, sentry):
    name = "agent.policy.documents — max above 10 (self-heal telemetry)"
    fake = sentry(existing=[{"id": "10900001", "name": name, "type": "metric_issue", "workflowIds": ["6300001"]}])
    monitor = create_monitor.create(write(tmp_path, **{"telemetry.json": SPEC}), ALERT, SETTINGS)
    assert monitor["reused"] and monitor["id"] == "10900001"
    assert fake.posted("/detectors/") == [] and fake.posted("/workflows/") == []


def test_no_slack_action_means_monitor_without_alert(tmp_path, sentry, capsys):
    fake = sentry(slack_actions=())
    monitor = create_monitor.create(write(tmp_path, **{"telemetry.json": SPEC}), ALERT, SETTINGS)
    assert monitor["alert_id"] is None and fake.posted("/workflows/") == []
    assert "no Slack action to copy" in capsys.readouterr().out


def test_slack_says_created_monitor_with_its_link(tmp_path, sentry, no_slack, monkeypatch, capsys):
    sentry()
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    out = write(tmp_path, **{"telemetry.json": SPEC, "alert.json": ALERT})
    monkeypatch.setattr(sys, "argv", ["create_monitor.py", "--out", out])
    create_monitor.main()
    assert ("<https://team-se.sentry.io/monitors/10900001/|Created monitor>: alerts when max > 10 documents"
            " in 5 min") in capsys.readouterr().out


def test_sentry_refusal_is_a_warning_with_sentrys_reason(tmp_path, sentry, no_slack, monkeypatch, capsys):
    sentry(fail="/detectors/")
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    out = write(tmp_path, **{"telemetry.json": SPEC, "alert.json": ALERT})
    monkeypatch.setattr(sys, "argv", ["create_monitor.py", "--out", out])
    with pytest.raises(SystemExit) as exited:
        create_monitor.main()
    assert exited.value.code == 1
    out = capsys.readouterr().out
    assert "::warning title=No monitor created::" in out and "invalid aggregate" in out
    assert "Created monitor" not in out


# --- wiring ---------------------------------------------------------------------------------

@pytest.mark.parametrize("org, has_telemetry", [("team-se", True), ("demo", False)])
def test_only_targets_with_a_telemetry_block_get_the_follow_up(org, has_telemetry):
    name, config = target.resolve({"org": org}, target.load_targets())
    settings = target.env_lines(name, config, {"org": org})["TARGET_TELEMETRY"]
    assert bool(settings) is has_telemetry
    if has_telemetry:
        assert json.loads(settings)["project"] == "kunal-manager-agent"


def test_telemetry_prompt_is_fully_rendered(tmp_path, monkeypatch):
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    monkeypatch.setenv("TARGET_TESTS", "python -m pytest agent/tests -q")
    monkeypatch.setenv("TARGET_PATHS", "agent/")
    monkeypatch.setenv("SENTRY_ORG", "team-se")
    monkeypatch.setenv("SENTRY_MCP_TOKEN_TEAM_SE", "test-token-12345")
    alert = tmp_path / "alert.json"
    alert.write_text(json.dumps(ALERT))
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["prepare.py", "telemetry", "--alert", str(alert), "--out", str(out),
                                      "--mcp-out", str(tmp_path / "secrets" / "mcp.json"),
                                      "--fix-pr-url", "https://github.com/o/r/pull/1725"])
    prepare.main()
    prompt = (out / "prompt.md").read_text()
    assert "{{" not in prompt
    assert "**the number of help-centre documents**" in prompt and "5-minute window" in prompt
    assert "project `kunal-manager-agent`" in prompt and "https://github.com/o/r/pull/1725" in prompt
    assert json.loads((tmp_path / "secrets" / "mcp.json").read_text())["mcpServers"]["sentry"]


def test_verify_against_a_real_git_tree(tmp_path, monkeypatch):
    # The instrumentation in a changed file, and its test in a new one, as the agent leaves them
    repo = tmp_path / "repo"
    (repo / "agent" / "tests").mkdir(parents=True)
    policies = repo / "agent" / "policies.py"
    policies.write_text("def search_policies(pages):\n    return pages\n")
    for args in (["init", "-q"], ["add", "."],
                 ["-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "base"]):
        subprocess.run(["git", *args], cwd=repo, check=True)
    policies.write_text("import sentry_sdk\n\ndef search_policies(pages):\n    sentry_sdk.metrics.distribution(\n"
                        "        \"agent.policy.documents\", len(pages), attributes={\"tool\": \"search_policies\"})\n"
                        "    return pages\n")
    (repo / "agent" / "tests" / "test_metric.py").write_text("def test_metric():\n    assert True\n")
    out = write(tmp_path, **{"telemetry.json": SPEC})
    monkeypatch.chdir(repo)
    monkeypatch.setenv("TARGET_PATHS", "agent/")
    monkeypatch.setenv("TARGET_TESTS", f"{sys.executable} -c pass")
    check, spec = open_telemetry_pr.verify(out)
    assert check["in_scope"] and check["tests_passed"] and check["emits_metric"], check
    assert sorted(check["files_changed"]) == ["agent/policies.py", "agent/tests/test_metric.py"]
    assert open_telemetry_pr.blockers(check) == []


def test_agent_is_denied_every_sentry_write_tool(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prepare.py", "sentry-write-tools"])
    prepare.main()
    denied = capsys.readouterr().out.split()
    for tool in ("create_metric_monitor", "create_alert_rule", "update_issue", "execute_sentry_tool"):
        assert f"mcp__sentry__{tool}" in denied
