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
              with-seer:    no MCP. The harness (seer_handoff.py) gets the issue, Seer's root
                            cause (reusing Seer's automatic analysis if there is one), the failing
                            cart and the impact, and hands them to the agent in its prompt
              → fix + regression test → replay the cart from Sentry Logs → 200
              → harness re-runs pytest + replay itself → draft PR (GITHUB_TOKEN)
                + `pytest` commit status on the PR head
            review job per PR: comments MERGE/ADJUST/CLOSE (never approves)
            report job: scorecard, then deletes the run branch
                                                        │
          Slack, in the thread of Sentry's alert: per PR a four-line "Fix ready for review"
          (PR link, impact, root cause, verification + verdict). If an agent opens no PR, a
          one-line "No fix proposed" with the run log instead. The PR carries the detail, including "How this fix was found": every
          Sentry MCP call, Seer call and agent step. Agent PRs stay open for demos.
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
| `harness/seer_handoff.py` | With-Seer runs: gets Seer's root cause, the failing cart and the impact before the agent starts. |
| `harness/prepare.py` | Renders the prompt for each version, and the Sentry MCP config for without-Seer. |
| `harness/run_agent.py` | Runs headless `claude -p`, streams each step to the Actions log, writes `stats.json`, sends the scorecard span. |
| `harness/replay.py` | Replays a captured cart against the working tree. Exits 0 on HTTP 200. |
| `harness/open_pr.py` | Re-checks scope, tests and replay, then opens the draft PR. |
| `harness/report.py` | Slack messages for the run scorecard and for reviewer verdicts. |
| `prompts/` | Without-Seer diagnose + fix, with-Seer fix from Seer's handoff (`fix_from_seer.md`), reviewer, PR template. |
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
   carries the alert webhook. For Slack: `SELFHEAL_SLACK_BOT_TOKEN` (an existing approved bot's
   `xoxb-` token with `chat:write`) plus the `SELFHEAL_SLACK_CHANNEL` variable (channel ID), or
   an incoming webhook in `SELFHEAL_SLACK_WEBHOOK_URL`.
3. **Repository variables:**
   - `SELFHEAL_ENABLED=true` turns the selfheal workflows on. They do nothing without it.
   - `SELFHEAL_MODEL` is the model id (an OpenRouter `provider/model` id when using OpenRouter).
   - `SELFHEAL_HARNESS_DSN` is the DSN of `selfheal-harness`, for the scorecard spans.
   - `SELFHEAL_DEPLOY=true` lets merges deploy to App Engine.
   - Optional: `SELFHEAL_MODEL_PROVIDER` (`openrouter` or `anthropic`),
     `SELFHEAL_MODEL_KEY_SECRET` (`AGENT_OPENROUTER_API_KEY`), `SELFHEAL_GCP_PROJECT`
     (`sales-engineering-sf`), `SELFHEAL_MAX_TURNS` (40), `SELFHEAL_SENTRY_ORG` (`demo`), and
     `SELFHEAL_HAIKU_MODEL` (`anthropic/claude-haiku-5.5`).
   - Where the agents look in Sentry: `SELFHEAL_SENTRY_PROJECT` / `SELFHEAL_SENTRY_ENVIRONMENT`.
     The default is the test app (`selfheal-flask` / `selfheal`). Set `backend-flask` /
     `production` to run on production's scheduled checkout drops. Production logs the cart as a
     Python dict in the message; the agents and `replay.py` handle both forms.
   - Which agents run: `SELFHEAL_VARIANTS`, default `["without-seer"]`. Once Seer works for the
     project (repository connected), set it to `["without-seer", "with-seer"]`.
   - Agent PRs stay open for demos, but only the latest run's: once a run opens a PR, its
     `report` job closes agent PRs from earlier runs.
   - The Sentry MCP runs inside the job as `@sentry/mcp-server` (pinned in
     `harness/prepare.py`), because the hosted MCP only takes OAuth sign-ins.
4. **Keep-list (master, optional):** add `selfheal-flask selfheal-harness` to `--exclude` in
   `cleanup_projects.yml`, or those projects get deleted every 2 hours.
5. **Branch protection on `selfheal/base`** (repo admin): require a pull request with 1 approval
   and the `pytest` status check. The repo lets `GITHUB_TOKEN` approve PRs, and nothing in the
   harness ever approves. To make that a hard rule, also require approval of the most recent push
   by someone other than its author.
6. Push the `selfheal-armed` tag. `arm.sh` restores the buggy files from it.
7. **Receiver's GitHub access: a GitHub App** (org-owned, no personal token). The receiver runs
   outside Actions, so it creates run branches with installation tokens it mints from the app's
   private key. To set it up:
   1. github.com → `sentry-demos` org → Settings → Developer settings → GitHub Apps → **New
      GitHub App**. Creating an org-owned app needs an org owner or GitHub App manager.
      - Name: `empower-selfheal`. Homepage URL: the repo URL.
      - Webhook: uncheck **Active** (the app doesn't receive events).
      - Repository permissions: **Contents** Read and write, **Actions** Read-only,
        **Pull requests** Read-only. Metadata: Read-only (automatic).
      - Where can it be installed: **Only on this account**.
   2. Create it, then note the **App ID** at the top of its settings page.
   3. **Generate a private key**, which downloads a `.pem` file.
   4. **Install App** → `sentry-demos` → Only select repositories → `empower`.
   5. Store the key, then delete the local copy:
      `gcloud secrets create SELFHEAL_GITHUB_APP_PRIVATE_KEY --project sales-engineering-sf --data-file=path/to/key.pem`
   6. Deploy with `GITHUB_APP_ID=<App ID> selfheal/receiver/deploy.sh`.

   Fallback: a token in Secret Manager `SELFHEAL_GITHUB_TOKEN` with `GITHUB_AUTH=token`. Until the
   receiver is deployed, start runs with `scripts/trigger.sh`.

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
# Secrets the receiver reads (--data-file=- reads stdin: paste, then Ctrl-D twice)
gcloud secrets create SELFHEAL_SENTRY_CLIENT_SECRET --data-file=-
gcloud secrets create SELFHEAL_GITHUB_APP_PRIVATE_KEY --data-file=path/to/key.pem   # GitHub step 7
# Receiver (prints the webhook URL for step 5 above)
GITHUB_APP_ID=<App ID> selfheal/receiver/deploy.sh
# First deploy of selfheal-flask (later ones run from selfheal-deploy.yml)
GITHUB_SHA=$(git rev-parse HEAD) SENTRY_AUTH_TOKEN=... ./deploy flask --env=selfheal
```

`SELFHEAL_FLASK_URL` for the scripts is the service URL, for example
`https://selfheal-flask-dot-sales-engineering-sf.uc.r.appspot.com`.

## More orgs and targets

`selfheal/targets.json` lists where each alert's fix happens. One receiver serves every org: it
checks which org's client secret signed the webhook, picks that org's target (by project when an
org has several), and builds the run on the target's base branch. demo's checkout flow is the
`checkout` target and the default.

| Target | Org / project | Base branch | Code | Proof the fix works |
|---|---|---|---|---|
| `checkout` | `demo` / `backend-flask` | `selfheal/base` | `flask/` | Flask tests; replay of the failing cart from Sentry Logs |
| `agent-context` | `team-se` / `kunal-manager-agent` | `selfheal/agent-base` | `agent/` | Agent tests; `harness/checks/policy_tokens.py` (policy answer under 4,000 tokens, still answering) |

**`agent-context`** is the "context snowball" in Kunal's shopping-agent scenarios
(sentry-demos/empower#1692, from his fork). The alert is a metric issue: one `gen_ai.chat` span
with ~48k input tokens, caused by the `search_policies` tool returning the whole help-centre
export. `selfheal/agent-base` is his PR branch plus this harness, built by
`scripts/refresh-agent-base.sh`; agent PRs target it, so his PR and fork are never touched. Re-run
the script (then `git push --force origin selfheal/agent-base`) when his PR or the harness
changes. His tests pin the bug on purpose; the agent is told to update them to the correct
behaviour. It runs without Seer only (`variants` in targets.json): the with-Seer handoff
(`seer_handoff.py`, `fix_from_seer.md`) is written for the checkout bug.

**Adding an org:**
1. In that org: a `selfheal` internal integration (Alert Rule Action on, webhook URL = the same
   receiver `…/sentry`; Organization, Project and Team Read; Issue & Event Read & Write), and the
   `selfheal` action on the alert.
2. Its client secret in GCP as `SELFHEAL_SENTRY_CLIENT_SECRET_<ORG>` (e.g. `_TEAM_SE`). Add the org
   to `EXTRA_ORGS` when running `receiver/deploy.sh` (default `team-se`) and redeploy.
3. Its token as the GitHub secret `SELFHEAL_SENTRY_MCP_TOKEN_<ORG>`, passed in the runner's
   "Prepare prompt and Sentry MCP" and "Verify" steps.
4. A target for it in `targets.json`.

Manual runs: `SELFHEAL_TARGET=agent-context selfheal/scripts/trigger.sh "Kunal LLM Context Snowball" 7813412119`.

## Choosing with or without Seer

Each alert picks its version (`harness/plan.py`), so you can show one, the other, or both:

- **Issue alerts**: the event's `se` tag. Browse the site with `?se=selfheal-with-seer` or
  `?se=selfheal-without-seer`; the tag reaches the Flask backend and gives each version its own
  issue. Make one issue alert per tag: project `backend-flask`, environment `production`, when
  "a new issue is created" or "the issue changes from resolved to unresolved", if tag `se`
  equals the value, then the selfheal internal integration (and Slack).
- **Metric alerts**: the alert's name. Put `with-seer` or `without-seer` in it, e.g.
  "Revenue Metric Alert [with-seer]". Both fire on the same drop, each starts its own version,
  and each version replies in its own alert's Slack thread.
- **Either kind**: an alert with `with-seer` / `without-seer` in its name always gets that
  version. An alert that names neither runs `SELFHEAL_VARIANTS`.

The receiver reads the `se` tag from the alert's event. If the event comes without tags, the
runner's plan job looks up the issue's `se` tag in Sentry itself, so issue alerts never need the
version in their name. Runs for the two versions are independent: one in flight doesn't hold
back an alert for the other.

The with-Seer agent doesn't use the Sentry MCP. `harness/seer_handoff.py` gets the issue, Seer's
root cause (reusing Seer's automatic analysis if there is one, else starting a run and waiting
for it), the failing cart and the impact, and hands them to the agent in its prompt.

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

To run without an alert: `selfheal/scripts/trigger.sh "Alert title" [issue-id] [with-seer|without-seer]`.

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
