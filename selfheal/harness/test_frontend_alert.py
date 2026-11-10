"""Alerts on a frontend issue (a browser 500 from /checkout): the run starts from that issue and
follows its trace to the backend error, which is what gets diagnosed and fixed.

Run from the repo root: python -m pytest selfheal/harness
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prepare  # noqa: E402
import seer_handoff  # noqa: E402
import target  # noqa: E402

FRONTEND = {"id": "7835000001", "shortId": "FRONTEND-REACT-77Q", "title": "Error: 500 - Internal Server Error",
            "permalink": "https://demo.sentry.io/issues/7835000001/", "userCount": 5736,
            "project": {"slug": "frontend-react", "id": "5808623"}}
BACKEND = {"id": "7835218820", "shortId": "BACKEND-FLASK-KB", "title": "Exception: Error validating enough inventory",
           "permalink": "https://demo.sentry.io/issues/7835218820/", "count": "13179", "userCount": 156,
           "firstSeen": "2026-11-08T03:43:39Z", "project": {"slug": "backend-flask", "id": "1"}}
TRACE = "edca4bddfa394e129c723a4329bab8d8"


def env_for(project_slug):
    name, config = target.resolve({"org": "demo", "project": project_slug}, target.load_targets())
    return name, target.env_lines(name, config, {"org": "demo", "project_slug": project_slug})


def test_frontend_alert_keeps_the_backend_as_the_sentry_project():
    name, lines = env_for("frontend-react")
    assert name == "checkout"
    assert (lines["SENTRY_PROJECT"], lines["FRONTEND_PROJECT"]) == ("backend-flask", "frontend-react")


def test_backend_alert_has_no_frontend_project():
    _, lines = env_for("selfheal-flask")
    assert (lines["SENTRY_PROJECT"], lines["FRONTEND_PROJECT"]) == ("selfheal-flask", "")


def test_prompt_says_to_follow_the_trace_only_for_frontend_alerts():
    note = prepare.frontend_note("frontend-react", "backend-flask")
    assert "`frontend-react`" in note and "trace" in note and "change no code" in note
    assert "{{" not in note
    assert prepare.frontend_note("", "backend-flask") == ""


@pytest.fixture
def calls(monkeypatch):
    """Fake Sentry API: the frontend issue's latest event, the errors in its trace, the backend issue."""
    class Calls(list):
        rows = [{"issue.id": 7835218820, "issue": "BACKEND-FLASK-KB", "title": BACKEND["title"]}]
    seen = Calls()
    monkeypatch.setattr(seer_handoff, "PROJECT", "backend-flask")
    monkeypatch.setattr(seer_handoff, "CALLS", [])

    def sentry(method, path, layer, label, **kwargs):
        seen.append((path, kwargs.get("params")))
        seer_handoff.CALLS.append({"call": label})
        if path.endswith("/events/latest/"):
            return {"eventID": "e1", "contexts": {"trace": {"trace_id": TRACE}}}
        if path.endswith("/events/"):
            return {"data": seen.rows}
        return BACKEND
    monkeypatch.setattr(seer_handoff, "sentry", sentry)
    return seen


def test_handoff_follows_the_trace_to_the_backend_issue(calls):
    issue, trace_id = seer_handoff.backend_issue_from_trace(FRONTEND)
    assert (issue["shortId"], trace_id) == ("BACKEND-FLASK-KB", TRACE)
    assert calls[1][1]["query"] == f"trace:{TRACE} project:backend-flask"
    assert calls[2][0] == "/organizations/demo/issues/7835218820/"


def test_handoff_stops_when_another_backend_served_the_request(calls, capsys):
    calls.rows = []
    with pytest.raises(SystemExit):
        seer_handoff.backend_issue_from_trace(FRONTEND)
    assert "has no backend-flask error" in capsys.readouterr().out


def test_handoff_names_the_alerts_issue_and_shows_the_path(tmp_path):
    seer = {"run_id": 1, "status": "completed", "reused": True, "root_cause": "quantities is read too early"}
    logs = {"saved": False, "lost_revenue_usd": None}
    impact, markdown = seer_handoff.handoff_md(BACKEND, seer, logs, str(tmp_path), FRONTEND, TRACE)
    assert '"issue_short_id": "FRONTEND-REACT-77Q"' in markdown
    assert "**Alert issue (frontend):** [FRONTEND-REACT-77Q]" in markdown
    assert f"`{TRACE}`" in markdown and "**Issue:** [BACKEND-FLASK-KB]" in markdown
    assert (impact["failed_checkouts"], impact["users_affected"]) == (13179, 5736)
