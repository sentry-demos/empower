"""Which Sentry message the bot replies under.

Run from the repo root: python -m pytest selfheal/harness
"""
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import report  # noqa: E402

NOW = time.time()
SENTRY = {"bot_profile": {"name": "Sentry"}}
ISSUE_ALERT = {"kind": "event_alert", "issue_id": "7817323193", "variant": "with-seer",
               "title": "Exception: Error validating enough inventory for product",
               "url": "https://sentry.io/organizations/demo/issues/7817323193/events/c2b30ea1/"}


def sentry_message(ts, text, **extra):
    return {**SENTRY, "ts": f"{ts:.6f}", "text": text, **extra}


class History:
    """conversations.history, newest first, `per_page` messages a page, honouring `oldest`."""

    def __init__(self, messages, per_page=200):
        self.messages = sorted(messages, key=lambda m: -float(m["ts"]))
        self.per_page = per_page
        self.calls = []

    def __call__(self, url, headers=None, params=None, timeout=None):
        self.calls.append(params)
        kept = [m for m in self.messages if float(m["ts"]) >= float(params["oldest"])]
        start = int(params.get("cursor") or 0)
        page, more = kept[start:start + self.per_page], start + self.per_page < len(kept)
        body = {"ok": True, "messages": page,
                "response_metadata": {"next_cursor": str(start + self.per_page) if more else ""}}
        return type("Response", (), {"json": lambda self: body})()


@pytest.fixture
def slack(monkeypatch):
    def install(messages, per_page=200):
        history = History(messages, per_page)
        monkeypatch.setattr(report.requests, "get", history)
        return history
    return install


def test_repeat_issue_alert_replies_in_the_issues_first_thread(slack):
    # #demo-selfhealing on Nov 2: the issue's first alert is from Oct 28. Sentry posted the repeat
    # alert as a reply in that thread, so history lists only the old parent (plus newer chatter).
    parent = sentry_message(NOW - 5 * 86400, "<https://demo.sentry.io/issues/7817323193/?referrer=slack|*Exception*>")
    other = sentry_message(NOW - 600, "Critical: Chris LLM Context Snowball", thread_ts=None)
    slack([parent, other, {"ts": f"{NOW - 60:.6f}", "text": "Self-heal started", "bot_profile": {"name": "Rusted Advisor"}}])
    assert report.lookup_alert_message("xoxb-test", "C1", ISSUE_ALERT) == (parent["ts"], False)


def test_reply_sent_to_the_channel_too_resolves_to_its_thread(slack):
    parent_ts = f"{NOW - 5 * 86400:.6f}"
    broadcast = sentry_message(NOW - 120, "https://demo.sentry.io/issues/7817323193/", thread_ts=parent_ts,
                               subtype="thread_broadcast")
    slack([broadcast])
    assert report.lookup_alert_message("xoxb-test", "C1", ISSUE_ALERT) == (parent_ts, False)


def test_issue_link_is_found_on_a_later_page(slack):
    parent = sentry_message(NOW - 3 * 86400, "https://demo.sentry.io/issues/7817323193/")
    noise = [sentry_message(NOW - 100 - i, f"Critical: something else {i}") for i in range(450)]
    history = slack([parent] + noise, per_page=200)
    assert report.lookup_alert_message("xoxb-test", "C1", ISSUE_ALERT) == (parent["ts"], False)
    assert len(history.calls) == 3


def test_title_match_only_looks_at_recent_messages(slack):
    # A metric alert has no issue link: an old message with the same title isn't this alert's
    alert = {"kind": "metric_alert", "title": "Chris LLM Context Snowball"}
    slack([sentry_message(NOW - 2 * 86400, "Critical: Chris LLM Context Snowball")])
    assert report.lookup_alert_message("xoxb-test", "C1", alert) == (None, True)

    recent = sentry_message(NOW - 300, "Critical: Chris LLM Context Snowball")
    history = slack([recent])
    assert report.lookup_alert_message("xoxb-test", "C1", alert) == (recent["ts"], False)
    assert float(history.calls[0]["oldest"]) >= NOW - 6 * 3600 - 5  # no 30-day scan without an issue


def test_metric_monitor_alert_matches_by_its_title(slack, monkeypatch):
    # A metric monitor's alert arrives as an issue alert on its metric issue, but Sentry's Slack
    # message links the alert rule, not the issue, so it's found by title. No target match text
    # here: the title alone (with its em dash) has to match.
    monkeypatch.delenv("SELFHEAL_SLACK_ALERT_MATCH", raising=False)
    alert = {"kind": "event_alert", "issue_id": "7825689300",
             "title": "Chris LLM Context Snowball — max input tokens spike (Copy 11/2/26)"}
    critical = sentry_message(NOW - 120, "", attachments=[{"title": "Critical: Chris LLM Context Snowball"
                                                          " — max input tokens spike (Copy 11/2/26)",
                                                          "title_link": "https://team-se.sentry.io/alerts/rules/details/1/"}])
    slack([critical])
    assert report.lookup_alert_message("xoxb-test", "C1", alert) == (critical["ts"], False)


def test_slack_refusal_posts_to_the_channel(monkeypatch):
    body = {"ok": False, "error": "missing_scope"}
    monkeypatch.setattr(report.requests, "get",
                        lambda *a, **k: type("Response", (), {"json": lambda self: body})())
    assert report.lookup_alert_message("xoxb-test", "C1", ISSUE_ALERT) == (None, False)
