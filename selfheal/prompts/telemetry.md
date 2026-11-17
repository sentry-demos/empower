You are an engineer improving production telemetry. A self-heal agent just fixed a production
problem that Sentry only caught indirectly. Your job: instrument the whole critical user flow it
sits in, stage by stage, so the problem (and the next one) shows up directly, and lay out the
dashboard that follows that flow.

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
{{PATHS}}: the shopping agent (Python, `agent/`) and the browser app (React, `react/`).

## 1. Map the flow

Work out the stages a shopper goes through in the chatbot, from the browser to the agent and
back, by reading the code and the traces in Sentry. Typically:

- the chat opened and a message sent (browser: `react/src/components/ChatWidget.jsx`),
- the agent's turn (`agent/app/api/routes.py` `/chat`, the orchestrator in `agent/app/agents/`),
- the tools it calls (`agent/app/tools/shop/`: product search, policy search, cart and checkout,
  orders),
- the reply reaching the shopper.

Use 4 to 7 stages. Use the Sentry tools (read-only) on org `{{SENTRY_ORG}}` (projects
`frontend-react`, `agent`, `manager-agent`, `plant-agent`, `shopping-agent`; the agent's main
project is `{{SENTRY_PROJECT}}`) to see the spans each stage produces today and to check the
queries you'll use in step 4 actually match spans (e.g. `span.op:gen_ai.execute_tool
gen_ai.tool.name:search_policies`). Look at the value behind the alert too: you'll pick the
monitor's threshold from it in step 3.

## 2. Instrument each stage

Give every stage one application metric. Reuse a metric that already exists for a stage (the
browser already counts `chat.open`, `chat.message_sent`, `chat.conversation_started` and
`chat.cart.add`); add one where a stage has none. Always add the metric for the cause behind
this alert (for this problem: how many help-centre documents one policy search sends to the
model).

Python, with the SDK already in the agent (`sentry-sdk` 2.44 or later; metrics are on by default):

```python
import sentry_sdk

sentry_sdk.metrics.distribution("<name>", value, attributes={...})
sentry_sdk.metrics.count("<name>", 1, attributes={...})
```

Browser, with the SDK already in the React app:

```js
Sentry.metrics.count('<name>', 1, { attributes: {...} });
Sentry.metrics.distribution('<name>', value, { attributes: {...} });
```

Leave `unit` out for a plain count (your report's unit is then `"none"`); pass one only for a
real unit such as `"byte"` or `"millisecond"`.

- Emit each metric once per occurrence: `distribution` for a size, count or duration per request
  (so max and percentiles work), `count` for how often something happens.
- Name metrics in dotted lowercase, scoped to what they measure (`chat.reply_received`,
  `agent.turn.tool_calls`, `agent.policy.documents`), and pass the name as a string literal in
  the call: the harness checks the calls for every new name.
- Attributes: a few low-cardinality ones (the tool or agent name, the stage). Never the user's
  message, other free text, or personal data.
- Keep the existing spans and their attributes; metrics add to them.
- Add agent tests that the new Python metrics are emitted with the right names and values
  (monkeypatch `sentry_sdk.metrics.<type>`). Run `{{TESTS}}`; everything must pass. Tests that pin
  the current (unfixed) behaviour are expected: leave them alone. Browser changes aren't run by
  the harness, so keep them to the metric calls themselves.

The commands you may run:
{{BASH_COMMANDS}}

## 3. Propose the monitor

For the metric behind the alert, pick a threshold that separates a healthy value from the
problem, using the numbers you found and what the fix PR says normal looks like. The harness
turns it into a pre-filled Sentry monitor form for a person to review and create: the aggregate
of that metric over a {{WINDOW_MINUTES}}-minute window, critical above the threshold.

## 4. Lay out the dashboard

The harness builds a dashboard with one row per stage, in flow order, laid out like demo's
Critical Experience dashboard: the funnel step (this stage's span count against the next
stage's, so the drop-off shows), the stage's metric, p95 latency with the browser (FE) and the
agent (BE) as separate series, and the issues behind the stage's errors. For each stage give:

- `frontend_query` and `backend_query`: span searches for the stage's browser spans and its
  agent spans (checked in step 1). Plain Sentry search syntax, no project filter. Use `""` for a
  side the stage doesn't have, but give at least one.
- `metric` and `metric_aggregate`: the stage's metric and how to chart it (`sum` for a count,
  `p95` or `max` for a distribution).
- `error_query`: an error search scoped to the stage's page or code (by transaction, URL or
  culprit), checked in step 1.

## 5. Report

Write `{{OUT}}/telemetry.json`:

```json
{
  "metrics": [
    {"name": "chat.message_sent", "type": "count", "unit": "none", "attributes": [],
     "file": "react/src/components/ChatWidget.jsx", "new": false},
    {"name": "agent.policy.documents", "type": "distribution", "unit": "none",
     "attributes": ["tool"], "file": "agent/app/tools/shop/policies.py", "new": true}
  ],
  "monitor": {"metric": "agent.policy.documents", "aggregate": "max", "threshold": 10,
              "unit_label": "documents", "reasoning": "one or two sentences, with the numbers from Sentry"},
  "stages": [
    {"name": "Message sent",
     "frontend_query": "span.op:ui.action.click span.description:\"Send Message\"",
     "backend_query": "transaction:\"POST /chat\"",
     "metric": "chat.message_sent", "metric_aggregate": "sum", "error_query": "transaction:\"POST /chat\""},
    {"name": "Policy search", "frontend_query": "",
     "backend_query": "span.op:gen_ai.execute_tool gen_ai.tool.name:search_policies",
     "metric": "agent.policy.documents", "metric_aggregate": "p95", "error_query": "culprit:*policies*"}
  ],
  "summary": "one sentence: what is now measured and where"
}
```

List every metric a stage or the monitor uses; `"new": true` for the ones your change adds.
`type` is `distribution`, `count` or `gauge`; aggregates are `max`, `min`, `avg`, `sum`, `count`,
`p50`, `p75`, `p90`, `p95` or `p99` (a count supports `sum` and `count`); `unit_label` is the plural
noun for the monitored value in a Slack line ("documents").

Write `{{OUT}}/pr_body.md`: `## Why` (the problem from the fix PR, and why the flow needs
stage-by-stage telemetry), `## Metrics` (a table: stage, metric, type, attributes, where it's
emitted), `## Proposed monitor` (aggregate, threshold, reasoning), `## Verification` (the tests,
the test run). Link the fix PR. Refer to the Sentry issue by its short ID or link, never after
"fix", "fixes", "fixed", "close(s/d)" or "resolve(s/d)": Sentry would read that as this change
closing the issue.

Don't run git, don't open a PR, and don't create anything in Sentry. The harness re-runs the
tests, opens the PR, links the monitor form and opens the dashboard preview.
