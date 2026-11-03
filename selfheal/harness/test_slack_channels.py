"""Where the bot posts: the alert's own Slack channels, looked up in Sentry.

Run from the repo root: python -m pytest selfheal/harness
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report  # noqa: E402
import slack_channels  # noqa: E402
import target  # noqa: E402

ALERT = {"org": "demo", "rule": "Chris S. every event alert", "issue_id": "7762252014",
         "project_slug": "backend-flask", "title": "Exception: Error validating enough inventory for product",
         "url": "https://sentry.io/organizations/demo/issues/7762252014/events/e18af8c1/"}


def workflow(name, *actions, id="555"):
    """Shaped like /organizations/demo/workflows/ (alert 555, as Sentry returned it)."""
    return {"id": id, "name": name, "actionFilters": [{"logicType": "all", "actions": list(actions)}]}


SLACK_SENTRY_ALERTS = {"type": "slack", "integrationId": "182226",
                       "config": {"targetType": "specific", "targetDisplay": "sentry-alerts",
                                  "targetIdentifier": "C0587CAE9QD"}}
SELFHEAL = {"type": "webhook", "integrationId": None, "config": {"targetIdentifier": "selfheal-a13635"}}


@pytest.fixture
def sentry(monkeypatch):
    def install(pages):
        calls = []

        def fake_get(org, path, params=None):
            calls.append((path, params))
            for prefix, items in pages.items():
                if path.startswith(prefix):
                    return items, None
            return None, None
        monkeypatch.setattr(slack_channels, "sentry_get", fake_get)
        return calls
    return install


def test_run_key_matches_the_receivers():
    # selfheal/receiver/test_main.py pins the same value for the same alert
    assert target.run_key(ALERT) == "k6df77c1326"
    assert target.run_key({**ALERT, "run_key": "kfromreceiv"}) == "kfromreceiv"


def test_alerts_slack_channel_comes_from_sentry(sentry):
    calls = sentry({"/organizations/demo/workflows/": [workflow("Chris S. every event alert", SLACK_SENTRY_ALERTS, SELFHEAL)]})
    assert slack_channels.alert_slack_channels(ALERT) == ["C0587CAE9QD"]
    assert calls[0][1]["query"] == "Chris S. every event alert"


def test_same_named_alerts_prefer_the_one_that_calls_selfheal(sentry):
    other = {**SLACK_SENTRY_ALERTS, "config": {"targetIdentifier": "C0OTHERCHAN"}}
    sentry({"/organizations/demo/workflows/": [
        workflow("Chris S. every event alert", other, id="1"),
        workflow("Chris S. every event alert", SLACK_SENTRY_ALERTS, SELFHEAL, id="2"),
        workflow("Someone else's alert", {**SLACK_SENTRY_ALERTS, "config": {"targetIdentifier": "C0NOTMINE1"}}),
    ]})
    assert slack_channels.alert_slack_channels(ALERT) == ["C0587CAE9QD"]


def test_older_issue_alert_rules_are_read_too(sentry):
    rule = {"name": "Chris S. every event alert", "actions": [
        {"id": "sentry.integrations.slack.notify_action.SlackNotifyServiceAction", "channel_id": "C0587CAE9QD",
         "channel": "#sentry-alerts"},
        {"id": "sentry.rules.actions.notify_event_sentry_app.NotifyEventSentryAppAction"}]}
    sentry({"/organizations/demo/workflows/": [], "/projects/demo/backend-flask/rules/": [rule]})
    assert slack_channels.alert_slack_channels(ALERT) == ["C0587CAE9QD"]


@pytest.mark.parametrize("alert, pages", [
    ({**ALERT, "rule": ""}, {}),                                                    # trigger.sh: no rule
    (ALERT, {}),                                                                    # Sentry unreachable
    (ALERT, {"/organizations/demo/workflows/": [workflow("Chris S. every event alert", SELFHEAL)]}),  # no Slack action
    (ALERT, {"/organizations/demo/workflows/": [workflow("Chris S. every event alert",
                                                        {**SLACK_SENTRY_ALERTS, "config": {"targetIdentifier": "#sentry-alerts"}})]}),
])
def test_unknown_channel_falls_back_to_the_default(sentry, alert, pages):
    sentry(pages)
    assert slack_channels.alert_slack_channels(alert) == []


class FakeSlack:
    """conversations.history / conversations.join / chat.postMessage for a few channels."""

    def __init__(self, history, member=(), joinable=(), missing=()):
        self.history, self.member, self.joinable, self.missing = history, set(member), set(joinable), set(missing)
        self.posted = []

    def get(self, url, headers=None, params=None, timeout=None):
        channel = params["channel"]
        if channel in self.missing:
            body = {"ok": False, "error": "channel_not_found"}
        elif channel not in self.member:
            body = {"ok": False, "error": "not_in_channel"}
        else:
            body = {"ok": True, "messages": self.history.get(channel, [])}
        return self.response(body)

    def post(self, url, headers=None, json=None, timeout=None):
        channel = json["channel"]
        if url.endswith("conversations.join"):
            ok = channel in self.joinable
            if ok:
                self.member.add(channel)
            return self.response({"ok": ok} if ok else {"ok": False, "error": "method_not_supported_for_channel_type"})
        if channel in self.missing or channel not in self.member:
            return self.response({"ok": False, "error": "channel_not_found" if channel in self.missing else "not_in_channel"})
        self.posted.append((channel, json.get("thread_ts")))
        return self.response({"ok": True})

    @staticmethod
    def response(body):
        return type("Response", (), {"json": lambda self: body, "raise_for_status": lambda self: None})()


SENTRY_MESSAGE = {"ts": "1793740538.000100", "bot_profile": {"name": "Sentry"},
                  "text": "<https://demo.sentry.io/issues/7762252014/?referrer=slack|*Exception*>"}


@pytest.fixture
def slack(monkeypatch):
    def install(fake, channels):
        monkeypatch.setenv("SELFHEAL_SLACK_BOT_TOKEN", "xoxb-test")
        monkeypatch.setenv("SELFHEAL_SLACK_CHANNEL", "C0DEMOSELF1")
        monkeypatch.setenv("SELFHEAL_SLACK_CHANNELS", json.dumps(channels))
        monkeypatch.setattr(report.requests, "get", fake.get)
        monkeypatch.setattr(report.requests, "post", fake.post)
        return fake
    return install


def test_posts_in_the_alerts_thread_in_its_own_channel(slack):
    fake = slack(FakeSlack({"C0587CAE9QD": [SENTRY_MESSAGE]}, member={"C0587CAE9QD", "C0DEMOSELF1"}), ["C0587CAE9QD"])
    report.post("Self-heal started", [], ALERT)
    assert fake.posted == [("C0587CAE9QD", SENTRY_MESSAGE["ts"])]  # not #demo-selfhealing


def test_joins_a_public_channel_it_isnt_in(slack):
    fake = slack(FakeSlack({"C0587CAE9QD": [SENTRY_MESSAGE]}, member={"C0DEMOSELF1"}, joinable={"C0587CAE9QD"}),
                 ["C0587CAE9QD"])
    report.post("Self-heal started", [], ALERT)
    assert fake.posted == [("C0587CAE9QD", SENTRY_MESSAGE["ts"])]


@pytest.mark.parametrize("fake_kwargs", [
    {"member": {"C0DEMOSELF1"}},                                  # private channel, bot not invited
    {"member": {"C0DEMOSELF1"}, "missing": {"C0587CAE9QD"}},      # another workspace
])
def test_falls_back_to_the_default_channel(slack, fake_kwargs):
    fake = slack(FakeSlack({}, **fake_kwargs), ["C0587CAE9QD"])
    report.post("Self-heal started", [], ALERT)
    assert fake.posted == [("C0DEMOSELF1", None)]


def test_no_alert_channels_posts_to_the_default_as_before(slack):
    fake = slack(FakeSlack({"C0DEMOSELF1": [SENTRY_MESSAGE]}, member={"C0DEMOSELF1"}), [])
    report.post("Self-heal started", [], ALERT)
    assert fake.posted == [("C0DEMOSELF1", SENTRY_MESSAGE["ts"])]


def test_alert_posting_to_two_channels_gets_replies_in_both(slack):
    fake = slack(FakeSlack({"C0587CAE9QD": [SENTRY_MESSAGE], "C0SECOND01": [SENTRY_MESSAGE]},
                           member={"C0587CAE9QD", "C0SECOND01", "C0DEMOSELF1"}), ["C0587CAE9QD", "C0SECOND01"])
    report.post("Self-heal started", [], ALERT)
    assert [channel for channel, _ in fake.posted] == ["C0587CAE9QD", "C0SECOND01"]
