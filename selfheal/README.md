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
drive.py live ──► flask-selfheal /checkout ──► 500, checkout.captured.revenue drops
                                                        │
          Sentry metric alert (revenue drop) goes critical; backup issue alert on new issue
                                                        │ internal integration webhook
          receiver/ (Cloud Run): verify signature · only "critical"/"triggered" · skip if a run
          is in flight or an agent PR is open → repository_dispatch "selfheal-alert"
                                                        │
          .github/workflows/selfheal-runner.yml, one job per version:
            without-seer: MCP ?disable-skills=seer, analyze_issue_with_seer denied
            with-seer:    MCP + analyze_issue_with_seer
            → fix + regression test → pull cart_json from Sentry Logs → replay → 200
            → harness re-runs pytest + replay itself → draft PR (bot token)
                                                        │
          selfheal-tests.yml (required check) · selfheal-reviewer.yml comments MERGE/ADJUST/CLOSE
          Slack: "<alert> → root cause → PR ready" + scorecard (time, turns, tokens, cost)
          Sentry selfheal-harness project: one gen_ai.invoke_agent span per run (Agent Tracing)
                                                        │
          Presenter approves and merges one PR (branch protection requires a human)
                                                        │
          selfheal-deploy.yml: deploy flask-selfheal, release flask-selfheal@<sha> with commits,
          "Fixes FLASK-SELFHEAL-N" resolves the issue, sibling agent PR is closed
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
| `../selfheal.env` | `./deploy flask --env=selfheal` config: App Engine service `flask-selfheal`, environment `selfheal`, release = commit SHA. |
| `../AGENTS.md` | Rules for agents on this branch. |

## One-time setup

### GitHub (`sentry-demos/empower`)

1. **Runner on master.** GitHub only starts `repository_dispatch` workflows whose file is on the
   default branch, so `.github/workflows/selfheal-runner.yml` must also be committed to `master`.
   It checks out `selfheal/base` for everything else. In the same PR to master:
   - add `flask-selfheal selfheal-harness` to the `--exclude` list in `cleanup_projects.yml`,
     or those projects get deleted every 2 hours.
2. **Branch protection on `selfheal/base`** (repo admin): require a pull request with 1 approval,
   require the `pytest` status check, no bypass for the bot.
3. **Bot account**: a separate GitHub user, not `sentry[bot]` or `cursor[bot]`, so
   `close_bot_prs_except_label_example.yml` leaves its PRs alone. Give it write access, and
   create a fine-grained token with Contents (read/write) and Pull requests (read/write).
   It can open PRs but can't merge: branch protection requires a human approval.
4. **Repository secrets**:

   | Secret | Value |
   |---|---|
   | `SELFHEAL_BOT_TOKEN` | Bot token (checkout, push, PRs). Not `GITHUB_TOKEN`: PRs opened with `GITHUB_TOKEN` don't trigger other workflows, so the pytest check would never run. |
   | `SELFHEAL_ANTHROPIC_API_KEY` | Anthropic API key for `claude -p`. |
   | `SELFHEAL_SENTRY_MCP_TOKEN` | Sentry user auth token for the MCP (no browser sign-in). |
   | `SELFHEAL_SENTRY_ORG_TOKEN` | Sentry org token for `sentry-cli` releases in the deploy. |
   | `SELFHEAL_HARNESS_DSN` | DSN of the `selfheal-harness` project (scorecard spans). |
   | `SELFHEAL_SLACK_WEBHOOK_URL` | Slack incoming webhook for the demo channel. |

   The deploy reuses the existing `GCP_WORKLOAD_IDENTITY_PROVIDER` and `GCP_SERVICE_ACCOUNT`.
   If that provider has an attribute condition limited to `refs/heads/master`, add `selfheal/base`.

5. **Repository variables**: `SELFHEAL_ENABLED=true` turns the selfheal workflows on (they do
   nothing without it), and `SELFHEAL_DEPLOY=true` lets merges deploy to App Engine. To test
   privately first, see [TESTING.md](TESTING.md). Optional: `SELFHEAL_MODEL` (default `claude-opus-5-5`),
   `SELFHEAL_MAX_TURNS` (40), `SELFHEAL_SENTRY_ORG` (`demo`), `SELFHEAL_SENTRY_MCP_URL`
   (`https://mcp.sentry.dev/mcp`), `SELFHEAL_SENTRY_MCP_AUTH_HEADER` / `_AUTH_PREFIX`
   (`Authorization` / `Bearer `), `SELFHEAL_BOT_NAME`, `SELFHEAL_BOT_EMAIL`.

6. Push the `selfheal-armed` tag. `arm.sh` restores the buggy files from it.

### Sentry (`demo` org)

1. Projects: `flask-selfheal` (Python/Flask) and `selfheal-harness`. Logs on for `flask-selfheal`.
2. Add the `flask-selfheal` DSN to GCP Secret Manager as `FLASK_SELFHEAL_DSN`.
3. Seer on for the org. GitHub integration code mapping: `flask-selfheal` → `sentry-demos/empower`
   branch `selfheal/base`, stack root `src/`, source root `flask/src/`.
4. Seer automatic runs **off** for `flask-selfheal`, so Seer doesn't open its own PR and race
   the agents.
5. Internal integration with **Alert Rule Action** on and webhook URL `<receiver URL>/sentry`.
   Put its client secret in GCP Secret Manager as `SELFHEAL_SENTRY_CLIENT_SECRET`.
6. **Metric alert (primary)**: `sum(checkout.captured.revenue)` in `flask-selfheal`,
   `environment:selfheal`, 5-minute window. Critical when it drops below what `drive.py baseline`
   produces (about $1,000 per 5 minutes at the default rate), or use a percent-change threshold.
   Action: the internal integration.
7. **Issue alert (backup)**: new issue in `flask-selfheal`, `environment:selfheal`, action:
   the internal integration.
8. Resolve through commits works because the deploy sets commits on the release and the PR body
   says `Fixes FLASK-SELFHEAL-N`.

### GCP (`sales-engineering-sf`)

```bash
# Secrets the receiver reads
gcloud secrets create SELFHEAL_SENTRY_CLIENT_SECRET --data-file=-
gcloud secrets create SELFHEAL_GITHUB_TOKEN --data-file=-   # bot token
# Receiver (prints the webhook URL for step 5 above)
selfheal/receiver/deploy.sh
# First deploy of flask-selfheal (later ones run from selfheal-deploy.yml)
GITHUB_SHA=$(git rev-parse HEAD) SENTRY_AUTH_TOKEN=... ./deploy flask --env=selfheal
```

`SELFHEAL_FLASK_URL` for the scripts is the service URL, for example
`https://flask-selfheal-dot-sales-engineering-sf.uc.r.appspot.com`.

## Running the demo

```bash
export SELFHEAL_FLASK_URL=https://flask-selfheal-dot-sales-engineering-sf.uc.r.appspot.com
selfheal/scripts/arm.sh                    # bug on selfheal/base and deployed
python selfheal/scripts/drive.py baseline  # ~15 min before: healthy revenue baseline
# On stage, when it's time for production to break:
python selfheal/scripts/drive.py live      # real checkouts → 500s → revenue drops
```

Within the alert window the metric alert goes critical. Open the `selfheal-runner` run in
Actions and watch both agents work, then Slack for the scorecard and the reviewer's verdicts.
Approve and merge one PR. Keep `drive.py live` running: after `selfheal-deploy` finishes,
checkouts succeed, revenue recovers, the alert resolves and the issue shows resolved in the release.

To dry-run without an alert: Actions → selfheal-runner → Run workflow.

After the demo:

```bash
SENTRY_AUTH_TOKEN=... selfheal/scripts/reset.sh
```

## Guardrails

- The bot token can open PRs but not merge. `selfheal/base` requires a human approval and the
  `pytest` check.
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
