# Self-healing demo

Production breaks, Sentry notices, an unattended agent diagnoses and fixes it, a human merges,
and Sentry confirms the fix. Two agents run on the same alert, **with Seer** and **without Seer**
(Sentry MCP + Claude only), and a scorecard compares them.

The bug is in the Flask `/checkout` handler (`flask/src/main.py`): it reads `quantities` before
assigning it. The resulting `UnboundLocalError` is re-raised as the misleading
`"Error validating enough inventory for product"`. The right fix moves one line. A careless fix
wraps or rewords the exception, and the reviewer agent is told to flag that.

## Flow

```
drive.py live ──► selfheal-flask /checkout ──► 500, checkout.captured.revenue drops
                                                        │
          Sentry metric alert (revenue drop) goes critical; backup issue alert on new issue
                                                        │ internal integration webhook
          receiver/ (Cloud Run): verify signature · only "critical"/"triggered" · skip if a run
          is in flight or an agent PR is open → push branch selfheal/run/<id> (+ .selfheal/alert.json)
          (scripts/trigger.sh does the same by hand)
                                                        │
          .github/workflows/selfheal-runner.yml (push trigger, so nothing lives on master):
            model key read from GCP Secret Manager via the existing GCP login
            fix job per version:
              without-seer: MCP ?disable-skills=seer, analyze_issue_with_seer denied
              with-seer:    MCP + analyze_issue_with_seer
              → fix + regression test → pull cart_json from Sentry Logs → replay → 200
              → harness re-runs pytest + replay itself → draft PR (GITHUB_TOKEN)
                + `pytest` commit status on the PR head
            review job per PR: comments MERGE/ADJUST/CLOSE (never approves)
            report job: scorecard, then deletes the run branch
                                                        │
          Slack: "<alert> → root cause → PR ready" + scorecard (time, turns, tokens, cost)
          Sentry selfheal-harness project: one gen_ai.invoke_agent span per run (Agent Tracing)
                                                        │
          Presenter approves and merges one PR (branch protection requires a human)
                                                        │
          selfheal-deploy.yml: deploy selfheal-flask, release selfheal-flask@<sha> with commits,
          "Fixes SELFHEAL-FLASK-N" resolves the issue, sibling agent PR is closed
          → live traffic succeeds → revenue recovers → alert resolves
```

## What's where

| Path | What it does |
|---|---|
| `receiver/` | Webhook receiver for Cloud Run. `deploy.sh` deploys it. |
| `harness/prepare.py` | Renders the prompt and the Sentry MCP config for each version. |
| `harness/run_agent.py` | Runs headless `claude -p`, streams each step to the Actions log, writes `stats.json`, sends the scorecard span. |
| `harness/replay.py` | Replays a captured cart against the working tree. Exits 0 on HTTP 200. |
| `harness/open_pr.py` | Re-checks scope, tests and replay, then opens the draft PR. |
| `harness/report.py` | Slack messages for the run scorecard and for reviewer verdicts. |
| `prompts/` | Diagnose + fix (with one diagnosis section per version), reviewer, PR template. |
| `scripts/drive.py` | Purchase traffic: `baseline` (healthy revenue) or `live` (real checkouts). |
| `scripts/arm.sh` | Makes sure the bug is on `selfheal/base` and deployed. |
| `scripts/reset.sh` | Closes agent PRs, resolves issues, re-arms. |
| `../selfheal.env` | `./deploy flask --env=selfheal` config: App Engine service `selfheal-flask`, environment `selfheal`, release = commit SHA. |
| `../AGENTS.md` | Rules for agents on this branch. |

## One-time setup

### GitHub (`sentry-demos/empower`)

Everything runs on credentials the repo already has. Nothing goes on master, except the
optional `cleanup_projects` keep-list change in point 4. Step-by-step test instructions are in
[TESTING.md](TESTING.md).

1. **Credentials.** Agents push and open PRs with the Actions `GITHUB_TOKEN` (the repo allows
   Actions to create PRs). The model key is read at runtime from GCP Secret Manager through the
   existing `GCP_WORKLOAD_IDENTITY_PROVIDER` / `GCP_SERVICE_ACCOUNT`. The default is
   `AGENT_OPENROUTER_API_KEY` (owned by EPD), sent through OpenRouter's Anthropic-compatible
   endpoint. The deploy uses the existing `SENTRY_AUTH_TOKEN`. If the workload identity
   provider only allows certain refs, `selfheal/*` refs need to be allowed.
2. **New secret:** only `SELFHEAL_SENTRY_MCP_TOKEN`, the token of a `selfheal` internal
   integration (org-owned, no browser sign-in; see TESTING.md step 1). The same integration
   carries the alert webhook. Optional: `SELFHEAL_SLACK_WEBHOOK_URL` for a demo channel.
3. **Repository variables:**
   - `SELFHEAL_ENABLED=true` turns the selfheal workflows on. They do nothing without it.
   - `SELFHEAL_MODEL` is the model id (an OpenRouter `provider/model` id when using OpenRouter).
   - `SELFHEAL_HARNESS_DSN` is the DSN of `selfheal-harness`, for the scorecard spans.
   - `SELFHEAL_DEPLOY=true` lets merges deploy to App Engine.
   - Optional: `SELFHEAL_MODEL_PROVIDER` (`openrouter` or `anthropic`),
     `SELFHEAL_MODEL_KEY_SECRET` (`AGENT_OPENROUTER_API_KEY`), `SELFHEAL_GCP_PROJECT`
     (`sales-engineering-sf`), `SELFHEAL_MAX_TURNS` (40), `SELFHEAL_SENTRY_ORG` (`demo`),
     `SELFHEAL_SENTRY_MCP_URL` (`https://mcp.sentry.dev/mcp`), and
     `SELFHEAL_SENTRY_MCP_AUTH_HEADER` / `_AUTH_PREFIX` (`Authorization` / `Bearer `).
4. **Keep-list (master, optional):** add `selfheal-flask selfheal-harness` to `--exclude` in
   `cleanup_projects.yml`, or those projects get deleted every 2 hours.
5. **Branch protection on `selfheal/base`** (repo admin): require a pull request with 1 approval
   and the `pytest` status check. The repo lets `GITHUB_TOKEN` approve PRs, and nothing in the
   harness ever approves. To make that a hard rule, also require approval of the most recent push
   by someone other than its author.
6. Push the `selfheal-armed` tag. `arm.sh` restores the buggy files from it.
7. **Receiver token:** the receiver runs outside Actions, so it needs its own GitHub token
   (Secret Manager `SELFHEAL_GITHUB_TOKEN`) that can create branches. Until then, start runs with
   `scripts/trigger.sh`.

### Sentry (`demo` org)

1. Projects: `selfheal-flask` (Python/Flask) and `selfheal-harness`. Logs on for `selfheal-flask`.
2. Add the `selfheal-flask` DSN to GCP Secret Manager as `SELFHEAL_FLASK_DSN`.
3. Seer on for the org. GitHub integration code mapping: `selfheal-flask` → `sentry-demos/empower`
   branch `selfheal/base`, stack root `src/`, source root `flask/src/`.
4. Seer automatic runs **off** for `selfheal-flask`, so Seer doesn't open its own PR and race
   the agents.
5. Internal integration with **Alert Rule Action** on and webhook URL `<receiver URL>/sentry`.
   Put its client secret in GCP Secret Manager as `SELFHEAL_SENTRY_CLIENT_SECRET`.
6. **Metric alert (primary)**: `sum(checkout.captured.revenue)` in `selfheal-flask`,
   `environment:selfheal`, 5-minute window. Critical when it drops below what `drive.py baseline`
   produces (about $1,000 per 5 minutes at the default rate), or use a percent-change threshold.
   Action: the internal integration.
7. **Issue alert (backup)**: new issue in `selfheal-flask`, `environment:selfheal`, action:
   the internal integration.
8. Resolve through commits works because the deploy sets commits on the release and the PR body
   says `Fixes SELFHEAL-FLASK-N`.

### GCP (`sales-engineering-sf`)

```bash
# Secrets the receiver reads
gcloud secrets create SELFHEAL_SENTRY_CLIENT_SECRET --data-file=-
gcloud secrets create SELFHEAL_GITHUB_TOKEN --data-file=-   # bot token
# Receiver (prints the webhook URL for step 5 above)
selfheal/receiver/deploy.sh
# First deploy of selfheal-flask (later ones run from selfheal-deploy.yml)
GITHUB_SHA=$(git rev-parse HEAD) SENTRY_AUTH_TOKEN=... ./deploy flask --env=selfheal
```

`SELFHEAL_FLASK_URL` for the scripts is the service URL, for example
`https://selfheal-flask-dot-sales-engineering-sf.uc.r.appspot.com`.

## Running the demo

```bash
export SELFHEAL_FLASK_URL=https://selfheal-flask-dot-sales-engineering-sf.uc.r.appspot.com
selfheal/scripts/arm.sh                    # bug on selfheal/base and deployed
python selfheal/scripts/drive.py baseline  # ~15 min before: healthy revenue baseline
# On stage, when it's time for production to break:
python selfheal/scripts/drive.py live      # real checkouts → 500s → revenue drops
```

Within the alert window the metric alert goes critical. Open the `selfheal-runner` run in
Actions and watch both agents work, then Slack for the scorecard and the reviewer's verdicts.
Approve and merge one PR. Keep `drive.py live` running: after `selfheal-deploy` finishes,
checkouts succeed, revenue recovers, the alert resolves and the issue shows resolved in the release.

To run without an alert: `selfheal/scripts/trigger.sh "Alert title"`.

After the demo:

```bash
SENTRY_AUTH_TOKEN=... selfheal/scripts/reset.sh
```

## Guardrails

- Agents never hold the GitHub token: the harness pushes and opens the PR after the agent
  finishes. `selfheal/base` requires a human approval and the `pytest` check to merge.
- Agent PRs are drafts. The reviewer agent only comments.
- Agent PRs target `selfheal/base`, never `master`, where the bug stays in place for everyone's demos.
- Agents get a fixed tool list: read/edit files, `python -m pytest`, `replay.py`, and the Sentry
  MCP. No git and no network access beyond the MCP. The harness, not the agent, verifies the fix
  and opens the PR, and refuses changes outside `flask/`.
- The receiver ignores repeats while a run is active or an agent PR is open. The deploy closes
  the sibling PR after a merge, so the next break fires a fresh run.

## Testing locally

```bash
pip install -r flask/requirements.txt pytest
python -m pytest flask/src/test                     # Flask tests (offline)
(cd selfheal/receiver && python -m pytest)          # receiver tests
python selfheal/harness/replay.py some-cart.json    # 500 on selfheal/base
```
