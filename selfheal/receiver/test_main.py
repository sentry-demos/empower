import hashlib
import hmac
import json
from unittest.mock import patch

import pytest

import main

SECRET = "test-secret"


@pytest.fixture(autouse=True)
def secret(monkeypatch):
    monkeypatch.setattr(main, "SENTRY_CLIENT_SECRET", SECRET)


@pytest.fixture
def client():
    return main.app.test_client()


def deliver(client, resource, payload, secret=SECRET):
    body = json.dumps(payload).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    return client.post("/sentry", data=body, headers={
        "Sentry-Hook-Resource": resource,
        "Sentry-Hook-Signature": signature,
        "Content-Type": "application/json",
    })


CRITICAL = {
    "action": "critical",
    "data": {
        "metric_alert": {"alert_rule": {"name": "Checkout revenue dropped"}},
        "description_title": "Critical: Checkout revenue dropped",
        "description_text": "sum(checkout.captured.revenue) < 100",
        "web_url": "https://demo.sentry.io/alerts/rules/details/1/",
    },
}


def test_rejects_bad_signature(client):
    response = deliver(client, "metric_alert", CRITICAL, secret="wrong")
    assert response.status_code == 401


@pytest.mark.parametrize("action", ["warning", "resolved"])
def test_ignores_non_critical_metric_alerts(client, action):
    with patch.object(main, "github") as gh:
        response = deliver(client, "metric_alert", {**CRITICAL, "action": action})
    assert response.json["status"] == "ignored"
    gh.assert_not_called()


def test_creates_run_branch_on_critical(client):
    with patch.object(main, "already_handling", return_value=""), \
         patch.object(main, "create_run_branch", return_value="selfheal/run/1") as create:
        response = deliver(client, "metric_alert", CRITICAL)

    assert response.status_code == 202
    assert response.json["branch"] == "selfheal/run/1"
    assert create.call_args.args[0]["title"] == "Critical: Checkout revenue dropped"


def test_create_run_branch_commits_alert_on_base():
    calls = []

    def fake_github(method, path, json=None, **kwargs):
        calls.append((method, path, json))

        class R:
            def json(self):
                if path.endswith("/ref/heads/selfheal/base"):
                    return {"object": {"sha": "base-sha"}}
                if path.endswith("/commits/base-sha"):
                    return {"tree": {"sha": "base-tree"}}
                return {"sha": "new-" + path.rsplit("/", 1)[-1]}
        return R()

    with patch.object(main, "github", side_effect=fake_github):
        branch = main.create_run_branch({"title": "Revenue dropped"})

    assert branch.startswith("selfheal/run/")
    _, _, tree = calls[2]
    assert tree["base_tree"] == "base-tree"
    assert tree["tree"][0]["path"] == ".selfheal/alert.json"
    assert '"Revenue dropped"' in tree["tree"][0]["content"]
    _, _, commit = calls[3]
    assert commit == {"message": "Self-heal run: Revenue dropped", "tree": "new-trees", "parents": ["base-sha"]}
    method, path, ref = calls[4]
    assert (method, path) == ("POST", "/repos/sentry-demos/empower/git/refs")
    assert ref == {"ref": f"refs/heads/{branch}", "sha": "new-commits"}


def test_skips_repeat_while_run_in_flight(client):
    with patch.object(main, "already_handling", return_value="runner already in_progress"), \
         patch.object(main, "github") as gh:
        response = deliver(client, "metric_alert", CRITICAL)
    assert response.json["status"] == "skipped"
    gh.assert_not_called()


def test_issue_alert_passes_issue_id(client):
    payload = {"action": "triggered", "data": {
        "event": {"title": "Exception: Error validating enough inventory for product",
                  "issue_id": 12345, "web_url": "https://demo.sentry.io/issues/12345/"},
        "triggered_rule": "selfheal backup issue alert",
    }}
    with patch.object(main, "already_handling", return_value=""), \
         patch.object(main, "create_run_branch", return_value="selfheal/run/1") as create:
        deliver(client, "event_alert", payload)
    assert create.call_args.args[0]["issue_id"] == "12345"


def test_already_handling_finds_open_agent_pr():
    responses = {
        "queued": {"total_count": 0},
        "in_progress": {"total_count": 0},
    }

    def fake_github(method, path, params=None, **kwargs):
        class R:
            def json(self):
                if "matching-refs" in path:
                    return []
                if path.endswith("/runs"):
                    return responses[params["status"]]
                return [{"number": 7, "labels": [{"name": "selfheal-agent"}]}]
        return R()

    with patch.object(main, "github", side_effect=fake_github):
        assert main.already_handling() == "agent PR #7 is still open"


def test_already_handling_finds_pending_run_branch():
    def fake_github(method, path, **kwargs):
        class R:
            def json(self):
                return [{"ref": "refs/heads/selfheal/run/20261026-180000"}]
        return R()

    with patch.object(main, "github", side_effect=fake_github):
        assert main.already_handling() == "run branch selfheal/run/20261026-180000 exists"
