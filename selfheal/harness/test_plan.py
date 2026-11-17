"""Which version an alert runs: names and se tags (plan.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import plan  # noqa: E402


def no_lookup(issue_id, org=None):
    return ""


def tagged(se):
    return lambda issue_id, org=None: se


def test_reinvent_tag_runs_with_seer():
    alert = {"issue_id": "1", "se": "reinvent", "rule": "reinvent - Frontend Checkout Issue"}
    assert plan.choose(alert, default='["without-seer"]', lookup=tagged("reinvent")) == ["with-seer"]


def test_reinvent_tag_from_issue_lookup_only():
    # The receiver got no tags on the event; the plan job's issue lookup finds se=reinvent
    alert = {"issue_id": "1", "se": "", "rule": "some alert"}
    assert plan.choose(alert, default='["without-seer"]', lookup=tagged("Reinvent")) == ["with-seer"]


def test_alert_name_wins_over_mapped_tag():
    alert = {"issue_id": "1", "se": "reinvent", "rule": "reinvent checkout [without-seer]"}
    assert plan.choose(alert, default='["with-seer"]', lookup=tagged("reinvent")) == ["without-seer"]


def test_receiver_variant_wins_over_mapped_tag():
    alert = {"issue_id": "1", "se": "reinvent", "variant": "without-seer"}
    assert plan.choose(alert, lookup=tagged("reinvent")) == ["without-seer"]


def test_unmapped_tag_uses_default():
    alert = {"issue_id": "1", "se": "kunal2", "rule": "x"}
    assert plan.choose(alert, default='["without-seer"]', lookup=tagged("kunal2")) == ["without-seer"]


def test_partial_match_is_not_mapped():
    alert = {"issue_id": "1", "se": "reinvent-old", "rule": "x"}
    assert plan.choose(alert, default='["without-seer"]', lookup=tagged("reinvent-old")) == ["without-seer"]


def test_target_limit_still_applies():
    # agent-context runs without Seer only, whatever the tag says
    alert = {"issue_id": "1", "se": "reinvent", "rule": "x"}
    assert plan.variants_for(alert, lookup=tagged("reinvent"), allowed=["without-seer"]) == ["without-seer"]
