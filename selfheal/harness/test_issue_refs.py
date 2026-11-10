"""Agent commits and PRs must never read, to Sentry, as fixing the issue they respond to.

Run from the repo root: python -m pytest selfheal/harness
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import issue_refs  # noqa: E402
import open_pr  # noqa: E402

SHORT_ID = "KUNAL-MANAGER-AGENT-5"
URL = "https://team-se.sentry.io/issues/123/"


@pytest.mark.parametrize("text", [
    "Fixes KUNAL-MANAGER-AGENT-5",
    "fix the bug, KUNAL-MANAGER-AGENT-5",
    "Fix the policy search, KUNAL-MANAGER-AGENT-5",
    "This resolves\nKUNAL-MANAGER-AGENT-5",
    "Closed: kunal-manager-agent-5",
    "Fixes [KUNAL-MANAGER-AGENT-5](https://team-se.sentry.io/issues/123/)",
    "Resolves https://team-se.sentry.io/issues/123/",
    "fixed https://team-se.sentry.io/organizations/team-se/issues/123/events/abc/",
])
def test_guard_catches_closing_references(text):
    assert issue_refs.closing_references(text, SHORT_ID, URL)
    with pytest.raises(issue_refs.ClosingReference):
        issue_refs.check({"body": text}, SHORT_ID, URL)


@pytest.mark.parametrize("text", [
    "Sentry issue: KUNAL-MANAGER-AGENT-5 https://team-se.sentry.io/issues/123/",
    "[without-seer] KUNAL-MANAGER-AGENT-5: search_policies returns only matching pages",
    "## Sentry issue\n\n[KUNAL-MANAGER-AGENT-5](https://team-se.sentry.io/issues/123/) — spike",
    "Fixes the policy search. Context: KUNAL-MANAGER-AGENT-5",  # the period ends Sentry's capture
    "Fixes KUNAL-MANAGER-AGENT-50",  # a different issue
    "Prefix KUNAL-MANAGER-AGENT-5",
])
def test_guard_allows_plain_references(text):
    assert issue_refs.closing_references(text, SHORT_ID, URL) == []


def test_neutralize_rewords_only_keywords_that_lead_to_the_issue():
    text = "We fix one thing. Then this Fixes KUNAL-MANAGER-AGENT-5 and RESOLVES " + URL
    out = issue_refs.neutralize(text, SHORT_ID, URL)
    assert out == "We fix one thing. Then this Addresses KUNAL-MANAGER-AGENT-5 and ADDRESSES " + URL
    assert issue_refs.closing_references(out, SHORT_ID, URL) == []


def write_run(tmp_path, body):
    (tmp_path / "result.json").write_text(json.dumps({
        "issue_short_id": SHORT_ID, "issue_url": URL,
        "fix_summary": "Fix KUNAL-MANAGER-AGENT-5 by ranking policy pages against the query",
    }))
    (tmp_path / "pr_body.md").write_text(body)
    timeline = [{"type": "note", "text": "Tests pass, which fixes KUNAL-MANAGER-AGENT-5."}]
    (tmp_path / "timeline.json").write_text(json.dumps(timeline))
    return str(tmp_path)


CHECK = {"files_changed": ["agent/app/tools/shop/policies.py"], "tests_passed": True,
         "tests_summary": "49 passed", "replay_status": None, "check_passed": True,
         "check_label": "policy answer under the token budget", "check_summary": "{\"ok\": true}"}


def test_generated_title_commit_and_body_never_close_the_issue(tmp_path):
    # What the agent wrote for PR #1721, plus the old footer and agent notes that say "fixes <ID>"
    body = open(os.path.join(os.path.dirname(open_pr.__file__), "..", "prompts", "pr_template.md")).read()
    body += "\nThis change fixes the spike, KUNAL-MANAGER-AGENT-5.\n\nFixes KUNAL-MANAGER-AGENT-5\n"
    title, message, body = open_pr.pr_text("without-seer", write_run(tmp_path, body), CHECK)

    for text in (title, message, body):
        assert issue_refs.closing_references(text, SHORT_ID, URL) == []
    # Reviewers can still trace the PR back to Sentry
    assert title.startswith(f"[without-seer] {SHORT_ID}: ")
    assert message == f"Sentry issue: {SHORT_ID} {URL}"
    assert SHORT_ID in body


def test_pr_is_blocked_if_a_closing_reference_survives(tmp_path, monkeypatch):
    monkeypatch.setattr(issue_refs, "neutralize", lambda text, *args: text)
    with pytest.raises(issue_refs.ClosingReference):
        open_pr.pr_text("without-seer", write_run(tmp_path, "Fixes KUNAL-MANAGER-AGENT-5"), CHECK)
