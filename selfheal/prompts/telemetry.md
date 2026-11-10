You are an engineer improving production telemetry. A self-heal agent just fixed a production
problem that Sentry only caught indirectly. Your job: make the cause itself measurable, so next
time an alert fires on it directly.

## What happened

The alert that started this:

```json
{{ALERT}}
```

The fix agent's pull request ({{FIX_PR_URL}}), with its root cause and how it was found:
`{{OUT}}/fix_pr.md`, and its diff: `{{OUT}}/fix_pr.diff`. Read both first.

What to measure: **{{GOAL}}**.

## Your working tree

It is the code as it runs today, **without** the fix. Don't re-apply the fix and don't change
behaviour: your change only adds telemetry, and it ships as its own PR. Change files only under
{{PATHS}}.

## 1. Look at the data

Use the Sentry tools (read-only) on org `{{SENTRY_ORG}}`, project `{{SENTRY_PROJECT}}`, to see what
the value looks like today. For example, span attributes the code already records, or the traces
behind the alert. You'll use this to pick the threshold in step 3.

## 2. Instrument the code

Emit a Sentry Application Metric where the value is known, with the Python SDK already in the
app (`sentry-sdk` 2.44 or later; metrics are on by default):

```python
import sentry_sdk

sentry_sdk.metrics.distribution("<name>", value, attributes={...})
```

Leave `unit` out for a plain count (your report's unit is then `"none"`); pass one only for a
real unit such as `"byte"` or `"millisecond"`.

- One metric, emitted once per occurrence. Use `distribution` for a size or count per request
  (so max and percentiles work), `count` for how often something happens.
- Name it in dotted lowercase, scoped to what it measures, e.g. `agent.policy.documents`, and
  pass the name as a string literal in the call (the harness checks the call for it).
- Attributes: a few low-cardinality ones that help filter (the tool or agent name). Never the
  user's question, other free text, or personal data.
- Keep the existing span attributes; the metric adds to them.
- Add a regression test that the metric is emitted with the right name and value (monkeypatch
  `sentry_sdk.metrics.distribution`). Run `{{TESTS}}`; everything must pass. Tests that pin the
  current (unfixed) behaviour are expected: leave them alone.

The commands you may run:
{{BASH_COMMANDS}}

## 3. Propose the monitor

Pick a threshold that separates a healthy value from the problem, using the numbers you found
and what the fix PR says normal looks like. The harness turns your proposal into a pre-filled
Sentry monitor form for a person to review and create: max (or another aggregate) of your metric
over a {{WINDOW_MINUTES}}-minute window, critical above the threshold.

## 4. Report

Write `{{OUT}}/telemetry.json`:

```json
{
  "metric": {"name": "agent.policy.documents", "type": "distribution", "unit": "none",
             "attributes": ["tool"], "file": "agent/app/tools/shop/policies.py"},
  "monitor": {"aggregate": "max", "threshold": 10, "unit_label": "documents",
              "reasoning": "one or two sentences, with the numbers from Sentry"},
  "summary": "one sentence: what is now measured and where"
}
```

`type` is `distribution`, `count` or `gauge`; `aggregate` is one of `max`, `avg`, `p90`, `p95`,
`sum`; `unit_label` is the plural noun for the value in a Slack line ("documents").

Write `{{OUT}}/pr_body.md`: `## Why` (the problem from the fix PR, and why it was invisible as a
metric), `## Metric` (name, type, attributes, where it's emitted), `## Proposed monitor`
(aggregate, threshold, reasoning), `## Verification` (the test, the test run). Link the fix PR.
Refer to the Sentry issue by its short ID or link, never after "fix", "fixes", "fixed",
"close(s/d)" or "resolve(s/d)": Sentry would read that as this change closing the issue.

Don't run git, don't open a PR, and don't create anything in Sentry. The harness re-runs the
tests, opens the PR and links the monitor form.
