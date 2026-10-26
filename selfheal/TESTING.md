# Testing the self-heal loop

The loop runs in `sentry-demos/empower` on credentials the repo already has: the Actions
`GITHUB_TOKEN`, the existing GCP login (`GCP_WORKLOAD_IDENTITY_PROVIDER` / `GCP_SERVICE_ACCOUNT`),
and a model key read from GCP Secret Manager at runtime. Flask runs on your laptop, so nothing
deploys to GCP.

## What this touches, and what it doesn't

Nothing here changes existing behavior: no edits to master, to existing workflows, or to the
apps other people demo. It does add these:

| Added | Notes |
|---|---|
| Branch `selfheal/base` | Only the selfheal workflows react to it. |
| Short-lived `selfheal/run/<id>` branches | One per run. The runner deletes it when it finishes. |
| Draft PRs into `selfheal/base`, labeled `selfheal-agent` | Opened by `github-actions[bot]`, which the hourly bot-PR closer doesn't target. |
| Repo variables `SELFHEAL_*` and one secret `SELFHEAL_SENTRY_MCP_TOKEN` | Inert for every other workflow. |
| Sentry projects `selfheal-flask` and `selfheal-harness` in `demo` | `cleanup_projects` deletes projects not on its keep list every 2 hours (see step 2). |
| Model spend on the key you point it at | Defaults to `AGENT_OPENROUTER_API_KEY`, the agent demo's key, owned by EPD. Ask EPD first. |

Two things stay off: the App Engine deploy (`SELFHEAL_DEPLOY` unset) and Slack (no
`SELFHEAL_SLACK_WEBHOOK_URL`, so results print in the job log).

## Cost

The agent demo costs about **$0.0024 per conversation**, measured from its `gen_ai.chat` spans
in `demo`: $24.58 across 10,327 runs in 30 days, on gpt-5-mini and gpt-5-nano. The self-heal
loop is much heavier. Each run is 4 Claude Code sessions (2 fixers, 2 reviewers), each reading
code and Sentry data for up to `SELFHEAL_MAX_TURNS` turns. Each run's real cost is in the job log
(`cost_usd` on the `■` line) and on the `selfheal-harness` spans. Through OpenRouter, Claude
Code's cost figure is its own estimate, so check OpenRouter's activity page for the billed amount.

## 0. Local checks (no accounts needed)

Run everything from the worktree at `~/empower/.claude/worktrees/selfheal`, which is on
`selfheal/base`. Use Python 3.11, which is what the Flask Dockerfile uses; some pinned
dependencies don't install on newer Pythons.

```bash
cd ~/empower/.claude/worktrees/selfheal
uv venv -p 3.11 venv && source venv/bin/activate        # or: python3.11 -m venv venv (gitignored)
uv pip install -r flask/requirements.txt -r selfheal/receiver/requirements.txt pytest
python -m pytest flask/src/test                          # 9 passed
(cd selfheal/receiver && python -m pytest)               # 9 passed
```

Keep this venv active in each terminal you open for later steps.

## 1. Before the first run

1. **EPD's OK** to put this test's spend on `AGENT_OPENROUTER_API_KEY`. (Or point
   `SELFHEAL_MODEL_KEY_SECRET` at a different Secret Manager secret, with
   `SELFHEAL_MODEL_PROVIDER=anthropic` if it's an Anthropic key.)
2. **The OpenRouter model id.** Use `anthropic/claude-sonnet-5.5` while testing ($2 / $10 per
   million input / output tokens) and `anthropic/claude-opus-5.5` for the real demo ($4 / $20).
   Skip the `:batch` variants: they're for asynchronous batch jobs, not interactive agents.
   OpenRouter documents Claude Code support (its "Claude Code integration" guide) with the
   same settings the `selfheal-claude` action uses. Claude Code's quick background calls go to
   `anthropic/claude-haiku-5.5`; override with the `SELFHEAL_HAIKU_MODEL` variable.
3. **An org-owned Sentry token** for the MCP, from an internal integration: Org Settings →
   Developer Settings → Custom Integrations → Create New Integration → Internal Integration,
   named `selfheal`. Permissions: Project Read, Organization Read, Team Read, Issue & Event
   Read & Write (Write lets the with-Seer agent start Seer). Copy its token. The same integration
   can later carry the alert webhook (Alert Rule Action), so one org-owned credential covers both.
   Not verified yet: some endpoints only accept a real user, possibly Seer's. If the with-Seer job
   logs a 401/403 on `analyze_issue_with_seer`, use a personal token from a dedicated Sentry
   service user instead.

## 2. Sentry (`demo` org)

1. Create `selfheal-flask` (Python/Flask) and `selfheal-harness` (Python). Turn on Logs for `selfheal-flask`.
2. `cleanup_projects` runs every 2 hours and deletes projects that aren't on its keep list.
   For a short test, create them right before testing and expect to recreate them. To keep them,
   add both names to `--exclude` in `.github/workflows/cleanup_projects.yml` on master. That's a
   separate PR, and a deliberate change to an existing workflow.
3. Code mapping for `selfheal-flask` (GitHub integration): repo `sentry-demos/empower`, branch
   `selfheal/base`, stack trace root `src/`, source code root `flask/src/`.
4. Seer automatic runs **off** for `selfheal-flask`, so Seer doesn't open its own PR.

## 3. Generate real telemetry from your laptop

Use two terminals, both in the same worktree folder. There's no second checkout; a new tab
just `cd`s to the same place.

```bash
# terminal 1
cd ~/empower/.claude/worktrees/selfheal && source venv/bin/activate
FLASK_DSN=<selfheal-flask DSN> python selfheal/scripts/local_server.py --port 8080

# terminal 2
cd ~/empower/.claude/worktrees/selfheal && source venv/bin/activate
export SELFHEAL_FLASK_URL=http://localhost:8080
python selfheal/scripts/drive.py baseline --minutes 2   # 200s
python selfheal/scripts/drive.py live --minutes 2       # 500s: issue + "Failed to validate inventory" logs with cart_json
```

Check in Sentry that `selfheal-flask` has the issue (environment `selfheal`) and that Logs shows
the error line with a `cart_json` attribute.

## 4. Push the branch and set variables (when you're ready)

These are the first steps that change anything on GitHub. All of them are additive.

```bash
git push origin selfheal/base refs/tags/selfheal-armed
R=sentry-demos/empower
gh variable set SELFHEAL_ENABLED --repo $R --body true
gh variable set SELFHEAL_MODEL --repo $R --body anthropic/claude-sonnet-5.5  # opus-5.5 for the demo
gh variable set SELFHEAL_MAX_TURNS --repo $R --body 25                      # keep test runs short
gh variable set SELFHEAL_HARNESS_DSN --repo $R --body <selfheal-harness DSN>
gh secret set SELFHEAL_SENTRY_MCP_TOKEN --repo $R                            # prompts for the token from step 1
```

Optional variables: `SELFHEAL_MODEL_PROVIDER` (`openrouter` by default, or `anthropic`),
`SELFHEAL_MODEL_KEY_SECRET` (default `AGENT_OPENROUTER_API_KEY`), `SELFHEAL_SENTRY_ORG`
(`demo`), and `SELFHEAL_SENTRY_MCP_URL` / `_AUTH_HEADER` / `_AUTH_PREFIX`.

## 5. Run it

```bash
python selfheal/scripts/drive.py live --minutes 1        # fresh errors and logs
selfheal/scripts/trigger.sh "Critical: Checkout revenue dropped"
gh run watch --repo sentry-demos/empower   # pick the run; it may take a few seconds to appear
```

`trigger.sh` pushes a `selfheal/run/<id>` branch, which starts the runner. Expect:
- `fix (without-seer)` and `fix (with-seer)` streaming each agent step, then a draft PR each,
  with a `pytest` status.
- `review (...)`: a MERGE / ADJUST / CLOSE comment on each PR.
- `report`: the scorecard in the job log, then the run branch is deleted.
- In `selfheal-harness` → Agents: an `invoke_agent` trace per agent.

**Likely first-run failures:**
- **GCP login fails** in "selfheal-claude": the workload identity provider probably only allows
  certain refs. A GCP admin needs to allow `selfheal/*` refs for `sentry-demos/empower`.
- **Claude Code can't reach the model:** check `SELFHEAL_MODEL` against OpenRouter's model list.
- **MCP not connected** (the `▶` line shows `sentry=failed`): check the token, and try
  `SELFHEAL_SENTRY_MCP_AUTH_HEADER`.

## 6. Close the loop locally

1. Mark one PR ready for review, approve and merge it. `selfheal-deploy` closes the other PR.
   The deploy job is skipped.
2. Restart the server on the merged code. The new commit becomes the new release:
   ```bash
   git pull origin selfheal/base
   FLASK_DSN=... python selfheal/scripts/local_server.py --port 8080
   ```
3. `drive.py live` now returns 200s.

## 7. Reset between tries

```bash
SENTRY_AUTH_TOKEN=<your Sentry token> selfheal/scripts/reset.sh
git pull origin selfheal/base     # then restart local_server.py
```

This closes open agent PRs, resolves `selfheal-flask` issues, and restores the bug through a
PR merged with your admin rights.

## Later: the real alert path

The receiver (`selfheal/receiver/`) creates the run branch itself when a Sentry alert fires. It
runs outside Actions, so it needs a GitHub token that can create branches in empower, and the repo
doesn't have one today. Until there is one, use `trigger.sh`.

## Your fork

`cstavitsky/empower` isn't needed anymore. Delete it with `gh repo delete cstavitsky/empower`
(it's public) and `git remote remove fork`.
