"""Opening the PR survives GitHub hiccups (PR #1739: created, but `gh pr create` failed on labels).

Run from the repo root: python -m pytest selfheal/harness
"""
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import open_pr  # noqa: E402

URL = "https://github.com/sentry-demos/empower/pull/1739"
BRANCH = "selfheal/fix-without-seer-k6df77c1326-41736415459"
LABELS = ("selfheal-agent", "selfheal:without-seer")


class FakeGh:
    """Answers `gh pr create`, `gh pr view` and `gh pr edit` from a script of outcomes."""

    def __init__(self, create=(0, URL + "\n", ""), view=(1, "", "no pull requests found"), edits=((0, "", ""),)):
        self.create, self.view, self.edits = create, view, list(edits)
        self.calls = []

    def __call__(self, cmd, cwd=None, check=False, text=True, capture_output=True):
        self.calls.append(list(cmd))
        code, out, err = {"create": self.create, "view": self.view}.get(cmd[2]) or self.edits.pop(0)
        return subprocess.CompletedProcess(cmd, code, out, err)


@pytest.fixture
def gh(monkeypatch):
    def install(**outcomes):
        fake = FakeGh(**outcomes)
        monkeypatch.setattr(open_pr.subprocess, "run", fake)
        monkeypatch.setattr(open_pr.time, "sleep", lambda s: None)
        return fake
    return install


def test_pr_opens_then_gets_its_labels(gh):
    fake = gh()
    assert open_pr.create_pr(BRANCH, "title", "body.md", LABELS) == URL
    assert "--label" not in fake.calls[0]  # labels aren't part of creating the PR any more
    assert fake.calls[1] == ["gh", "pr", "edit", URL, "--add-label", "selfheal-agent",
                             "--add-label", "selfheal:without-seer"]


def test_pr_created_despite_an_error_is_found_and_used(gh, capsys):
    # What happened to #1739: the PR exists, but gh exited 1
    fake = gh(create=(1, "", "GraphQL: Something went wrong while executing your query"),
              view=(0, URL + "\n", ""))
    assert open_pr.create_pr(BRANCH, "title", "body.md", LABELS) == URL
    out = capsys.readouterr().out
    assert "GraphQL: Something went wrong" in out  # GitHub's own message is in the log now
    assert f"but {URL} exists" in out
    assert fake.calls[-1][:4] == ["gh", "pr", "edit", URL]


def test_labels_are_retried_and_never_fail_the_pr(gh, capsys):
    gh(edits=[(1, "", "HTTP 502")] * 3)
    assert open_pr.create_pr(BRANCH, "title", "body.md", LABELS) == URL
    assert "::warning title=PR labels::Couldn't add selfheal-agent, selfheal:without-seer" in capsys.readouterr().out


def test_no_pr_at_all_still_fails_with_githubs_reason(gh):
    gh(create=(1, "", "pull request create failed: GraphQL: Head sha can't be blank"))
    with pytest.raises(RuntimeError, match="Head sha can't be blank"):
        open_pr.create_pr(BRANCH, "title", "body.md", LABELS)
