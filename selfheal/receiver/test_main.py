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


def test_dispatches_on_critical(client):
    with patch.object(main, "already_handling", return_value=""), \
         patch.object(main, "github") as gh:
        response = deliver(client, "metric_alert", CRITICAL)

    assert response.status_code == 202
    method, path = gh.call_args.args
    assert (method, path) == ("POST", "/repos/sentry-demos/empower/dispatches")
    sent = gh.call_args.kwargs["json"]
    assert sent["event_type"] == "selfheal-alert"
    assert sent["client_payload"]["title"] == "Critical: Checkout revenue dropped"


def test_skips_repeat_while_run_in_flight(client):
    with patch.object(main, "already_handling", return_value="runner already in_progress"), \
         patch.object(main, "github") as gh:
        response = deliver(client, "metric_alert", CRITICAL)
    assert response.json["status"] == "skipped"
    gh.assert_not_called()


def test_dispatches_issue_alert_with_issue_id(client):
    payload = {"action": "triggered", "data": {
        "event": {"title": "Exception: Error validating enough inventory for product",
                  "issue_id": 12345, "web_url": "https://demo.sentry.io/issues/12345/"},
        "triggered_rule": "selfheal backup issue alert",
    }}
    with patch.object(main, "already_handling", return_value=""), \
         patch.object(main, "github") as gh:
        deliver(client, "event_alert", payload)
    assert gh.call_args.kwargs["json"]["client_payload"]["issue_id"] == "12345"


def test_already_handling_finds_open_agent_pr():
    responses = {
        "queued": {"total_count": 0},
        "in_progress": {"total_count": 0},
    }

    def fake_github(method, path, params=None, **kwargs):
        class R:
            def json(self):
                if path.endswith("/runs"):
                    return responses[params["status"]]
                return [{"number": 7, "labels": [{"name": "selfheal-agent"}]}]
        return R()

    with patch.object(main, "github", side_effect=fake_github):
        assert main.already_handling() == "agent PR #7 is still open"
