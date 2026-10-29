import hashlib
import hmac
import json
from unittest.mock import MagicMock, patch

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
        # Open agent PRs are kept for demos, so by default they don't block a new run
        assert main.already_handling() == ""
        with patch.object(main, "SKIP_WHILE_AGENT_PR_OPEN", True):
            assert main.already_handling() == "agent PR #7 is still open"


def test_github_app_token_is_minted_and_cached(monkeypatch):
    import jwt
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                            serialization.NoEncryption()).decode()
    monkeypatch.setattr(main, "GITHUB_APP_ID", "12345")
    monkeypatch.setattr(main, "GITHUB_APP_PRIVATE_KEY", pem)
    monkeypatch.setattr(main, "_app_token", {"value": "", "expires_at": 0.0})

    def fake_get(url, headers, timeout):
        assert url.endswith("/repos/sentry-demos/empower/installation")
        claims = jwt.decode(headers["Authorization"].removeprefix("Bearer "), key.public_key(),
                            algorithms=["RS256"])
        assert claims["iss"] == "12345"
        r = MagicMock()
        r.json.return_value = {"id": 99}
        return r

    def fake_post(url, headers, timeout):
        assert url.endswith("/app/installations/99/access_tokens")
        r = MagicMock()
        r.json.return_value = {"token": "ghs_installation"}
        return r

    with patch.object(main.requests, "get", side_effect=fake_get) as get, \
         patch.object(main.requests, "post", side_effect=fake_post):
        assert main.github_token() == "ghs_installation"
        assert main.github_token() == "ghs_installation"  # cached: no second exchange
    assert get.call_count == 1


def test_github_token_falls_back_without_app(monkeypatch):
    monkeypatch.setattr(main, "GITHUB_APP_ID", "")
    monkeypatch.setattr(main, "GITHUB_TOKEN", "github_pat_x")
    assert main.github_token() == "github_pat_x"


TEAM_SE_SECRET = "team-se-secret"
TOKEN_SPIKE = {"action": "triggered", "data": {
    "event": {"title": "Kunal LLM Context Snowball", "issue_id": 7813412119, "project": 42,
              "web_url": "https://sentry.io/organizations/team-se/issues/7813412119/events/abc/"},
    "triggered_rule": "Token spike",
}}


def test_second_org_routes_to_its_target(client, monkeypatch):
    monkeypatch.setenv("SENTRY_CLIENT_SECRET_TEAM_SE", TEAM_SE_SECRET)
    with patch.object(main, "already_handling", return_value=""), \
         patch.object(main, "create_run_branch", return_value="selfheal/run/1") as create:
        response = deliver(client, "event_alert", TOKEN_SPIKE, secret=TEAM_SE_SECRET)

    assert response.status_code == 202
    alert, base = create.call_args.args
    assert (alert["org"], alert["target"], base) == ("team-se", "agent-context", "selfheal/agent-base")
    assert alert["issue_id"] == "7813412119"


def test_default_org_still_routes_to_checkout(client):
    payload = {**TOKEN_SPIKE, "data": {**TOKEN_SPIKE["data"], "event": {
        **TOKEN_SPIKE["data"]["event"], "web_url": "https://sentry.io/organizations/demo/issues/1/"}}}
    with patch.object(main, "already_handling", return_value=""), \
         patch.object(main, "create_run_branch", return_value="selfheal/run/1") as create:
        deliver(client, "event_alert", payload)

    alert, base = create.call_args.args
    assert (alert["org"], alert["target"], base) == ("demo", "checkout", "selfheal/base")


def test_unconfigured_org_is_rejected(client, monkeypatch):
    monkeypatch.delenv("SENTRY_CLIENT_SECRET_TEAM_SE", raising=False)
    response = deliver(client, "event_alert", TOKEN_SPIKE, secret=TEAM_SE_SECRET)
    assert response.status_code == 401


def test_org_without_target_is_ignored(client, monkeypatch):
    monkeypatch.setenv("SENTRY_CLIENT_SECRET_OTHER_ORG", "other-secret")
    with patch.object(main, "create_run_branch") as create:
        response = deliver(client, "event_alert", TOKEN_SPIKE, secret="other-secret")
    assert response.json["status"] == "ignored"
    create.assert_not_called()


def test_org_from_url():
    assert main.org_from_url("https://sentry.io/organizations/demo/issues/1/") == "demo"
    assert main.org_from_url("https://team-se.sentry.io/issues/7813412119/") == "team-se"
    assert main.org_from_url("") is None


def test_already_handling_finds_pending_run_branch():
    def fake_github(method, path, **kwargs):
        class R:
            def json(self):
                return [{"ref": "refs/heads/selfheal/run/20261026-180000"}]
        return R()

    with patch.object(main, "github", side_effect=fake_github):
        assert main.already_handling() == "run branch selfheal/run/20261026-180000 exists"
