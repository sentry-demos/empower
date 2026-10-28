"""Which agent version(s) a self-heal run starts, from the alert that triggered it.

Each alert picks its version, so two alerts can drive the two versions separately:
  1. `variant` in alert.json, set by the receiver from the event's `se` tag
     (se=selfheal-with-seer / se=selfheal-without-seer) or from the alert rule's name.
  2. Otherwise "with-seer" / "without-seer" in the alert's title or description. The
     receiver puts the rule name there, so naming the alert e.g.
     "Checkout revenue dropped [with-seer]" is enough.
  3. Otherwise the default: SELFHEAL_VARIANTS (both, side by side, or a repo-chosen list).

Usage (prints the JSON list for the workflow matrix):
    python selfheal/harness/plan.py .selfheal/alert.json
"""
import json
import os
import sys

VARIANTS = ("without-seer", "with-seer")


def variant_in(*texts):
    """The version named in any of the texts, or "". "without-seer" is checked first:
    it doesn't contain "with-seer", but checking it first keeps that obvious."""
    for text in texts:
        text = str(text or "").lower()
        for variant in VARIANTS:
            if variant in text:
                return variant
    return ""


def alert_variant(alert):
    """The single version this alert asks for, or "" if it doesn't say."""
    if alert.get("variant") in VARIANTS:
        return alert["variant"]
    return variant_in(alert.get("se"), alert.get("rule"), alert.get("title"), alert.get("description"))


def variants_for(alert, default=None):
    variant = alert_variant(alert)
    if variant:
        return [variant]
    if default is None:
        default = os.environ.get("SELFHEAL_VARIANTS") or '["without-seer"]'
    chosen = [v for v in json.loads(default) if v in VARIANTS]
    return chosen or ["without-seer"]


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        alert = json.load(f)
    print(json.dumps(variants_for(alert)))
