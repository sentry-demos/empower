"""The telemetry follow-up: the agent's proposal, the instrumentation PR, the monitor form and the
dashboard preview.

Run from the repo root: python -m pytest selfheal/harness
"""
import json
import os
import subprocess
import sys
from urllib.parse import parse_qs, urlparse

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dashboard_preview  # noqa: E402
import monitor_preview  # noqa: E402
import open_telemetry_pr  # noqa: E402
import prepare  # noqa: E402
import target  # noqa: E402
import telemetry_spec  # noqa: E402

DOCS = {"name": "agent.policy.documents", "type": "distribution", "unit": "none", "attributes": ["tool"],
        "file": "agent/app/tools/shop/policies.py", "new": True}
REPLY = {"name": "chat.reply_received", "type": "count", "unit": "none", "attributes": [],
         "file": "react/src/components/ChatWidget.jsx", "new": True}
SENT = {"name": "chat.message_sent", "type": "count", "unit": "none", "attributes": [],
        "file": "react/src/components/ChatWidget.jsx", "new": False}
STAGES = [
    {"name": "Message sent", "frontend_query": 'span.op:ui.action.click span.description:"Send Message"',
     "backend_query": 'transaction:"POST /chat"', "metric": "chat.message_sent", "metric_aggregate": "sum",
     "error_query": 'transaction:"POST /chat"'},
    {"name": "Policy search", "frontend_query": "",
     "backend_query": "span.op:gen_ai.execute_tool gen_ai.tool.name:search_policies",
     "metric": "agent.policy.documents", "metric_aggregate": "p95", "error_query": "culprit:*policies*"},
    {"name": "Reply received", "frontend_query": "span.op:http.client span.description:*chat*", "backend_query": "",
     "metric": "chat.reply_received", "metric_aggregate": "sum", "error_query": "transaction:/chat"},
]
SPEC = {
    "metrics": [SENT, DOCS, REPLY],
    "monitor": {"metric": "agent.policy.documents", "aggregate": "max", "threshold": 10, "unit_label": "documents",
                "reasoning": "Normal answers use 3 or fewer pages; the spike sent all 50."},
    "stages": STAGES,
    "summary": "The chatbot flow now reports a metric per stage.",
}
ALERT = {"org": "demo", "rule": "Notify via selfheal", "issue_id": "7825689300",
         "title": "High Agent Token Usage"}
SETTINGS = {"goal": "the chatbot's critical experience", "project": "manager-agent",
            "paths": ["agent/", "react/"], "window_seconds": 300,
            "dashboard": {"title": "Chatbot critical experience", "projects": ["frontend-react", "manager-agent"],
                          "environment": "production"}}


def write(tmp_path, **files):
    for name, content in files.items():
        (tmp_path / name).write_text(content if isinstance(content, str) else json.dumps(content))
    return str(tmp_path)


def load(tmp_path, spec=SPEC):
    return telemetry_spec.load(write(tmp_path, **{"telemetry.json": spec}))


@pytest.fixture
def no_slack(monkeypatch):
    for name in ("SELFHEAL_SLACK_BOT_TOKEN", "SELFHEAL_SLACK_CHANNEL", "SELFHEAL_SLACK_CHANNELS"):
        monkeypatch.delenv(name, raising=False)


# --- the proposal ---------------------------------------------------------------------------

def test_spec_builds_sentrys_metric_aggregates(tmp_path):
    spec = load(tmp_path)
    # The same syntax Sentry's Explore uses for application metrics
    assert spec["monitor"]["sentry_aggregate"] == "max(value,agent.policy.documents,distribution,-)"
    assert telemetry_spec.describe(spec, 300) == "max > 10 documents in 5 min"
    assert [s["sentry_metric_aggregate"] for s in spec["stages"]] == [
        "sum(value,chat.message_sent,counter,-)", "p95(value,agent.policy.documents,distribution,-)",
        "sum(value,chat.reply_received,counter,-)"]
    assert spec["metric"]["name"] == "agent.policy.documents"  # the monitored metric


def bad(**change):
    return {**SPEC, **change}


@pytest.mark.parametrize("spec, error", [
    (bad(metrics=[{**DOCS, "name": "Documents Sent"}, SENT, REPLY]), "dotted lowercase"),
    (bad(metrics=[{**DOCS, "name": "agent.docs,distribution),count("}, SENT, REPLY]), "dotted lowercase"),
    (bad(metrics=[{**DOCS, "type": "histogram"}, SENT, REPLY]), "type"),
    (bad(metrics=[{**DOCS, "unit": "docs; drop"}, SENT, REPLY]), "unit"),
    (bad(metrics=[{**DOCS, "new": False}, SENT, {**REPLY, "new": False}]), "no new metrics"),
    (bad(metrics=[DOCS, DOCS, SENT, REPLY]), "listed twice"),
    (bad(monitor={**SPEC["monitor"], "metric": "agent.unknown"}), "monitor.metric"),
    (bad(monitor={**SPEC["monitor"], "threshold": 0}), "positive number"),
    (bad(monitor={**SPEC["monitor"], "threshold": "10"}), "positive number"),
    (bad(monitor={**SPEC["monitor"], "metric": "chat.reply_received", "aggregate": "p95"}), "doesn't apply"),
    (bad(stages=STAGES[:2]), "3 to 8"),
    (bad(stages=STAGES + [{**STAGES[0], "metric": "agent.unknown"}]), "isn't one of the listed metrics"),
    (bad(stages=STAGES + [{**STAGES[0], "frontend_query": "", "backend_query": ""}]), "neither a frontend_query"),
    (bad(stages=STAGES + [{**STAGES[0], "frontend_query": "x" * 301}]), "longer than"),
    (bad(stages=STAGES + [{**STAGES[0], "error_query": ""}]), "no error_query"),
])
def test_bad_proposals_never_reach_sentry(tmp_path, spec, error):
    with pytest.raises(telemetry_spec.SpecError, match=error):
        load(tmp_path, spec)


# --- the instrumentation PR -----------------------------------------------------------------

@pytest.mark.parametrize("added, missing", [
    (['    sentry_sdk.metrics.distribution("agent.policy.documents", len(pages), attributes={"tool": "x"})',
      "    Sentry.metrics.count('chat.reply_received', 1);"], []),
    (["    sentry_sdk.metrics.distribution(", '        "agent.policy.documents",', "        len(pages),", "    )",
      "  Sentry.metrics.count(", "    'chat.reply_received',", "    1,", "  );"], []),
    (['    sentry_sdk.metrics.distribution("agent.policy.pages", len(pages))',
      "    Sentry.metrics.count('chat.reply_received', 1);"], ["agent.policy.documents"]),   # another name
    (['    sentry_sdk.metrics.count("agent.policy.documents", 1)'],
     ["agent.policy.documents", "chat.reply_received"]),                                     # another type
    (["    // TODO: Sentry.metrics.count chat.reply_received"],
     ["agent.policy.documents", "chat.reply_received"]),
])
def test_harness_checks_the_code_emits_every_new_metric(tmp_path, added, missing):
    # chat.message_sent already exists ("new": false), so the change needn't emit it
    assert open_telemetry_pr.missing_metrics(added, load(tmp_path)) == missing


def test_blockers_name_every_problem():
    check = {"secrets_found": [], "in_scope": False, "tests_passed": False, "spec_error": None,
             "missing_metrics": ["chat.reply_received"]}
    found = open_telemetry_pr.blockers(check)
    assert any("outside" in b for b in found) and "tests fail" in found
    assert any("doesn't emit chat.reply_received" in b for b in found)


def test_slack_message_lists_the_new_metrics(tmp_path):
    assert open_telemetry_pr.slack_text("https://github.com/sentry-demos/empower/pull/1751", load(tmp_path)) == (
        "*Telemetry PR ready for review* · <https://github.com/sentry-demos/empower/pull/1751|PR #1751>\n\n"
        "• New application metrics along the chatbot flow: `agent.policy.documents`, `chat.reply_received`")


def test_pr_text_links_the_fix_shows_the_dashboard_and_never_closes_the_issue(tmp_path, monkeypatch):
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    out = write(tmp_path, **{"telemetry.json": SPEC,
                             "pr_body.md": "## Why\n\nThis fixes MANAGER-AGENT-5 for good.\n"})
    spec = telemetry_spec.load(out)
    check = {"files_changed": ["agent/app/tools/shop/policies.py", "react/src/components/ChatWidget.jsx"],
             "tests_summary": "50 passed"}
    fix = {"issue_short_id": "MANAGER-AGENT-5", "issue_url": "https://demo.sentry.io/issues/MANAGER-AGENT-5"}
    title, message, body = open_telemetry_pr.pr_text(out, spec, check, "https://github.com/o/r/pull/1725", fix)
    assert title == "[telemetry] MANAGER-AGENT-5: instrument the critical flow (2 application metrics, 3 stages)"
    assert message.startswith("Follows https://github.com/o/r/pull/1725")
    assert "`max(value,agent.policy.documents,distribution,-)`, alerts when max > 10 documents in 5 min" in body
    assert ("| 2 | Policy search | - | `span.op:gen_ai.execute_tool gen_ai.tool.name:search_policies` |"
            " `p95(agent.policy.documents)` | `culprit:*policies*` |") in body
    assert '"title": "Chatbot critical experience"' in body  # the JSON, to import if the preview fails
    assert "addresses MANAGER-AGENT-5" in body  # the agent's "fixes" was reworded


# --- the monitor form -----------------------------------------------------------------------

PREVIEW = ("https://demo.sentry.io/monitors/new/settings/?detectorType=metric_issue&dataset=metrics"
           "&aggregate=max%28value%2Cagent.policy.documents%2Cdistribution%2C-%29&project=4512138284367872")


def test_monitor_link_prefills_the_form(tmp_path):
    url = monitor_preview.preview_url("demo", load(tmp_path), "4512138284367872")
    assert url == PREVIEW
    # The fields Sentry's form reads from its URL (useInitialMetricDetectorFormData)
    assert parse_qs(urlparse(url).query) == {
        "detectorType": ["metric_issue"], "dataset": ["metrics"], "project": ["4512138284367872"],
        "aggregate": ["max(value,agent.policy.documents,distribution,-)"]}


def test_monitor_line_says_what_threshold_to_set(tmp_path):
    assert monitor_preview.slack_text(PREVIEW, load(tmp_path), 300) == (
        f"*Proposed monitor*: <{PREVIEW}|preview> · max over 5 min, set threshold to *10* documents")


def test_monitor_preview_creates_nothing_in_sentry(tmp_path, no_slack, monkeypatch, capsys):
    calls = []

    def fake_get(org, path, params=None):
        calls.append(("GET", path))
        return {"id": "4512138284367872", "slug": "manager-agent"}, None
    monkeypatch.setattr(monitor_preview.slack_channels, "sentry_get", fake_get)
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    out = write(tmp_path, **{"telemetry.json": SPEC, "alert.json": ALERT})
    monkeypatch.setattr(sys, "argv", ["monitor_preview.py", "--out", out])
    monitor_preview.main()
    assert calls == [("GET", "/projects/demo/manager-agent/")]  # one read, no writes
    assert json.loads((tmp_path / "monitor_preview.json").read_text())["url"] == PREVIEW
    assert f"<{PREVIEW}|preview>" in capsys.readouterr().out


def test_bad_proposal_gets_no_monitor_link(tmp_path, no_slack, monkeypatch, capsys):
    out = write(tmp_path, **{"telemetry.json": bad(monitor={**SPEC["monitor"], "threshold": -1}),
                             "alert.json": ALERT})
    monkeypatch.setattr(sys, "argv", ["monitor_preview.py", "--out", out])
    with pytest.raises(SystemExit):
        monitor_preview.main()
    output = capsys.readouterr().out
    assert "::warning title=No monitor preview::" in output and "Proposed monitor" not in output


# --- the dashboard preview ------------------------------------------------------------------

def queries(widget):
    return [(q["name"], q["aggregates"][0], q["conditions"]) for q in widget["queries"]]


def test_dashboard_rows_match_the_critical_experience_layout(tmp_path):
    board = dashboard_preview.build_dashboard(load(tmp_path), SETTINGS, ["5808623", "4512138284367872"])
    assert board["title"] == "Chatbot critical experience"
    assert board["projects"] == [5808623, 4512138284367872] and board["environment"] == ["production"]
    assert len(board["widgets"]) == 4 * len(STAGES) + 2  # a row per stage, then the extras row
    first, second = board["widgets"][0:4], board["widgets"][4:8]
    # Like demo's dashboard 134148: funnel step (w 2) · metric (w 1) · FE/BE latency (w 1) · errors (w 2)
    assert [(w["layout"]["x"], w["layout"]["y"], w["layout"]["w"], w["displayType"]) for w in second] == [
        (0, 2, 2, "area"), (2, 2, 1, "area"), (3, 2, 1, "line"), (4, 2, 2, "area")]
    assert [w["title"] for w in second] == [
        "2. Policy search vs Reply received", "Policy search: p95(agent.policy.documents)",
        "Policy search: p95 latency", "Errors in Policy search"]
    # The funnel step plots this stage and the next as two series
    assert queries(second[0]) == [
        ("Policy search", "count(span.duration)", STAGES[1]["backend_query"]),
        ("Reply received", "count(span.duration)", STAGES[2]["frontend_query"])]
    assert queries(second[1]) == [("", "p95(value,agent.policy.documents,distribution,-)", "")]
    # Latency splits browser (FE) and agent (BE) when the stage has both
    assert queries(first[2]) == [("FE", "p95(span.duration)", STAGES[0]["frontend_query"]),
                                 ("BE", "p95(span.duration)", STAGES[0]["backend_query"])]
    assert queries(second[2]) == [("BE", "p95(span.duration)", STAGES[1]["backend_query"])]
    assert first[0]["queries"][0]["conditions"] == f"({STAGES[0]['frontend_query']}) OR ({STAGES[0]['backend_query']})"
    # Errors list the issues behind them
    assert second[3]["widgetType"] == "error-events" and second[3]["queries"][0]["columns"] == ["issue", "title"]
    # The last stage has no next step; the extras row holds the alert's metric and logs
    assert board["widgets"][8]["title"] == "3. Reply received"
    extras = board["widgets"][12:]
    assert [(w["widgetType"], w["layout"]["y"]) for w in extras] == [("tracemetrics", 6), ("logs", 6)]
    assert queries(extras[0]) == [("", "max(value,agent.policy.documents,distribution,-)", "")]


def test_dashboard_filter_scopes_every_query(tmp_path):
    settings = {**SETTINGS, "dashboard": {**SETTINGS["dashboard"], "filter": "has:cexp"}}
    board = dashboard_preview.build_dashboard(load(tmp_path), settings)
    conditions = [q["conditions"] for w in board["widgets"] for q in w["queries"]]
    assert all(c.endswith("has:cexp") for c in conditions), conditions
    assert f"({STAGES[1]['backend_query']}) has:cexp" in conditions


def run_preview(tmp_path, monkeypatch, response):
    calls = []

    def fake_start(org, body):
        calls.append((org, body))
        return response
    monkeypatch.setattr(dashboard_preview, "start_preview", fake_start)
    monkeypatch.setattr(dashboard_preview, "project_ids", lambda org, slugs: ["5808623", "4512138284367872"])
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    out = write(tmp_path, **{"telemetry.json": SPEC, "alert.json": ALERT,
                             "telemetry_verify.json": {"pr_url": "https://github.com/o/r/pull/1769"}})
    monkeypatch.setattr(sys, "argv", ["dashboard_preview.py", "--out", out])
    return calls


def test_dashboard_preview_links_an_unsaved_dashboard(tmp_path, no_slack, monkeypatch, capsys):
    calls = run_preview(tmp_path, monkeypatch, (789, None))
    dashboard_preview.main()
    (org, body), = calls  # one generate call: Sentry saves nothing until a person does
    assert org == "demo" and "exactly as given" in body["prompt"]
    assert body["current_dashboard"]["title"] == "Chatbot critical experience"
    url = "https://demo.sentry.io/dashboards/new/from-seer/?seerRunId=789"
    assert json.loads((tmp_path / "dashboard_preview.json").read_text())["url"] == url
    assert f"*Dashboard preview* 📊: <{url}|Chatbot critical experience> · 3 stages" in capsys.readouterr().out


def test_dashboard_preview_falls_back_to_the_json_in_the_pr(tmp_path, no_slack, monkeypatch, capsys):
    run_preview(tmp_path, monkeypatch, (None, "HTTP 403 from dashboards/generate: AI features are disabled"))
    with pytest.raises(SystemExit):
        dashboard_preview.main()
    output = capsys.readouterr().out
    assert "::warning title=No dashboard preview::HTTP 403" in output
    assert "<https://github.com/o/r/pull/1769|the telemetry PR> to import" in output
    assert (tmp_path / "dashboard.json").exists()


# --- wiring ---------------------------------------------------------------------------------

@pytest.mark.parametrize("project, has_telemetry", [("manager-agent", True), ("backend-flask", False)])
def test_only_targets_with_a_telemetry_block_get_the_follow_up(project, has_telemetry):
    alert = {"org": "demo", "project": project, "project_slug": project}
    name, config = target.resolve(alert, target.load_targets())
    lines = target.env_lines(name, config, alert)
    assert bool(lines["TARGET_TELEMETRY"]) is has_telemetry
    if has_telemetry:
        settings = json.loads(lines["TARGET_TELEMETRY"])
        assert settings["project"] == "manager-agent" and settings["dashboard"]["title"]
        # The fix stays in agent/; the telemetry follow-up may also change the browser
        assert lines["TARGET_PATHS"] == "agent/"
        assert target.telemetry_lines(lines, config)["TARGET_PATHS"] == "agent/,react/"


def test_telemetry_prompt_is_fully_rendered(tmp_path, monkeypatch):
    monkeypatch.setenv("TARGET_TELEMETRY", json.dumps(SETTINGS))
    monkeypatch.setenv("TARGET_TESTS", "python -m pytest agent/tests -q")
    monkeypatch.setenv("TARGET_PATHS", "agent/,react/")
    monkeypatch.setenv("SENTRY_ORG", "demo")
    monkeypatch.setenv("SENTRY_MCP_TOKEN", "test-token-12345")
    alert = tmp_path / "alert.json"
    alert.write_text(json.dumps(ALERT))
    out = tmp_path / "out"
    monkeypatch.setattr(sys, "argv", ["prepare.py", "telemetry", "--alert", str(alert), "--out", str(out),
                                      "--mcp-out", str(tmp_path / "secrets" / "mcp.json"),
                                      "--fix-pr-url", "https://github.com/o/r/pull/1725"])
    prepare.main()
    prompt = (out / "prompt.md").read_text()
    assert "{{" not in prompt
    assert "**the chatbot's critical experience**" in prompt and "5-minute window" in prompt
    assert "`agent/`, `react/`" in prompt and "project is `manager-agent`" in prompt
    assert "https://github.com/o/r/pull/1725" in prompt
    assert json.loads((tmp_path / "secrets" / "mcp.json").read_text())["mcpServers"]["sentry"]


def test_verify_against_a_real_git_tree(tmp_path, monkeypatch):
    # Instrumentation in the agent and the browser, and a new test, as the agent leaves them
    repo = tmp_path / "repo"
    (repo / "agent" / "tests").mkdir(parents=True)
    (repo / "react" / "src").mkdir(parents=True)
    policies, widget = repo / "agent" / "policies.py", repo / "react" / "src" / "ChatWidget.jsx"
    policies.write_text("def search_policies(pages):\n    return pages\n")
    widget.write_text("export function onReply() {}\n")
    for args in (["init", "-q"], ["add", "."],
                 ["-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "base"]):
        subprocess.run(["git", *args], cwd=repo, check=True)
    policies.write_text("import sentry_sdk\n\ndef search_policies(pages):\n    sentry_sdk.metrics.distribution(\n"
                        "        \"agent.policy.documents\", len(pages), attributes={\"tool\": \"search_policies\"})\n"
                        "    return pages\n")
    widget.write_text("export function onReply() {\n  Sentry.metrics.count('chat.reply_received', 1);\n}\n")
    (repo / "agent" / "tests" / "test_metric.py").write_text("def test_metric():\n    assert True\n")
    out = write(tmp_path, **{"telemetry.json": SPEC})
    monkeypatch.chdir(repo)
    monkeypatch.setenv("TARGET_PATHS", "agent/,react/")
    monkeypatch.setenv("TARGET_TESTS", f"{sys.executable} -c pass")
    check, spec = open_telemetry_pr.verify(out)
    assert check["in_scope"] and check["tests_passed"] and check["missing_metrics"] == [], check
    assert sorted(check["files_changed"]) == ["agent/policies.py", "agent/tests/test_metric.py",
                                              "react/src/ChatWidget.jsx"]
    assert open_telemetry_pr.blockers(check) == []


def test_agent_is_denied_every_sentry_write_tool(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prepare.py", "sentry-write-tools"])
    prepare.main()
    denied = capsys.readouterr().out.split()
    for tool in ("create_metric_monitor", "create_alert_rule", "update_issue", "execute_sentry_tool"):
        assert f"mcp__sentry__{tool}" in denied
