# Testing the self-heal loop in isolation

This runs the whole loop in **your own fork, your own Sentry org, and on your laptop**. Nothing
touches `sentry-demos/empower`, the `demo` Sentry org, or the shared GCP project.

| Shared thing | Why this setup doesn't touch it |
|---|---|
| `sentry-demos/empower` (master, workflows, other people's PRs) | You push only to your fork. The existing workflows (auto-deploy, both cleanups, the bot PR closer) all have `if: github.repository_owner == 'sentry-demos'`, so they're skipped in a fork. |
| Selfheal workflows | Each is opt-in with the repo variable `SELFHEAL_ENABLED=true`. Set it only on your fork. |
| GCP `sales-engineering-sf` (App Engine, shared DB, Redis) | `selfheal-deploy` only deploys when `SELFHEAL_DEPLOY=true`. Leave it unset and run Flask locally with `local_server.py`, which stubs the DB, Redis and Statsig. |
| `demo` Sentry org and its cleanup job | Use a personal or test org. |
| Team Slack | Leave `SELFHEAL_SLACK_WEBHOOK_URL` unset (the message prints to the Actions log), or point it at a private channel. |

## API key and cost

There's no Anthropic key in this repo or its GCP secrets today. The existing agent demo
(`agent/`) uses OpenRouter (`AGENT_OPENROUTER_API_KEY` in GCP Secret Manager, owned by EPD), and
the `go` and `flask-otlp` apps use `OPENAI_API_KEY`. Claude Code can't run on either of those
keys, so get an Anthropic API key for this test. Use a personal or team key with a spend limit,
not one of the shared secrets above. (Later option: Claude Code can also run on Vertex AI in
the GCP project with `CLAUDE_CODE_USE_VERTEX=1`, reusing GCP auth instead of a separate key.
Not wired up yet.)

For scale: the agent demo costs about **$0.0024 per conversation**, measured from its own
`gen_ai.chat` spans in the `demo` org: $24.58 across 10,327 runs in the last 30 days, on
gpt-5-mini and gpt-5-nano. The self-heal loop is far heavier: each alert runs 4 Claude Code
sessions (2 fixers, 2 reviewers), each one up to `SELFHEAL_MAX_TURNS` turns reading code and Sentry
data. Expect a single alert to cost more than days of agent-demo traffic. The real number for each
run shows up in the scorecard (`cost_usd`) and on the `selfheal-harness` spans. To keep test runs
cheap, start with a smaller model and a lower turn cap (step 1).

## 0. Offline checks (no accounts needed)

Run every command in this guide from a checkout of `selfheal/base`. On your machine that's the
worktree at `~/empower/.claude/worktrees/selfheal`. Your main `~/empower` checkout is on another
branch. Use Python 3.11, which is what the Flask Dockerfile uses; some pinned dependencies don't
install on newer Pythons.

```bash
cd ~/empower/.claude/worktrees/selfheal
uv venv -p 3.11 venv && source venv/bin/activate        # or: python3.11 -m venv venv (gitignored)
uv pip install -r flask/requirements.txt -r selfheal/receiver/requirements.txt pytest
python -m pytest flask/src/test                          # 9 passed
(cd selfheal/receiver && python -m pytest)               # 7 passed
```

Keep this venv active in each terminal you open for steps 3 to 7.

## 1. Fork

**Already done for `cstavitsky/empower`:** forked, `selfheal/base` and the `selfheal-armed` tag
pushed, `selfheal/base` set as the default branch, Actions enabled, `SELFHEAL_ENABLED=true`,
and a git remote named `fork` in your local clone. To repeat this for someone else:

```bash
gh repo fork sentry-demos/empower --clone=false          # -> <you>/empower
git remote add fork https://github.com/<you>/empower.git
git push fork selfheal/base refs/tags/selfheal-armed
gh repo edit <you>/empower --default-branch selfheal/base
gh variable set SELFHEAL_ENABLED --repo <you>/empower --body true
```

Making `selfheal/base` the fork's default branch matters. GitHub only starts
`repository_dispatch` and manual `workflow_dispatch` runs from workflow files on the default
branch, and this way you don't have to touch master.

**Still to do:** secrets and variables. `gh secret set` prompts for each value, so nothing ends
up in your shell history.

```bash
R=cstavitsky/empower
gh variable set SELFHEAL_SENTRY_ORG --repo $R --body <your-test-org-slug>   # otherwise defaults to demo
gh variable set SELFHEAL_MODEL --repo $R --body claude-sonnet-5-5          # cheaper while testing
gh variable set SELFHEAL_MAX_TURNS --repo $R --body 25
gh secret set SELFHEAL_BOT_TOKEN --repo $R           # fine-grained PAT, only this fork: Contents + Pull requests read/write
gh secret set SELFHEAL_ANTHROPIC_API_KEY --repo $R   # see "API key and cost"
gh secret set SELFHEAL_SENTRY_MCP_TOKEN --repo $R    # user auth token in your test org
gh secret set SELFHEAL_HARNESS_DSN --repo $R         # DSN of selfheal-harness (step 2)
# Optional: gh secret set SELFHEAL_SLACK_WEBHOOK_URL --repo $R   (a private channel)
gh secret list --repo $R && gh variable list --repo $R  # check
```

Leave `SELFHEAL_DEPLOY` unset so nothing deploys to GCP. For testing, the "bot" can be your own
account. Branch protection on the fork's `selfheal/base` is optional. Add it if you want to
rehearse the "agent can't merge" guardrail. Once the loop works, set `SELFHEAL_MODEL` back to
`claude-opus-5-5` (or delete the variable) to rehearse with the model you'll demo.

## 2. Sentry (your test org)

1. Create projects `flask-selfheal` (Flask) and `selfheal-harness` (Python). Turn on Logs for `flask-selfheal`.
2. Connect the GitHub integration to your fork. Add a code mapping for `flask-selfheal`: branch
   `selfheal/base`, stack trace root `src/`, source code root `flask/src/`.
3. Seer: available in the org, automatic runs **off** for `flask-selfheal`.

If your org doesn't have Seer, the without-Seer job still works end to end. The with-Seer job
shows what happens when the Seer tool fails.

## 3. Generate real telemetry from your laptop

```bash
FLASK_DSN=<flask-selfheal DSN> python selfheal/scripts/local_server.py --port 8080
# second terminal
export SELFHEAL_FLASK_URL=http://localhost:8080
python selfheal/scripts/drive.py baseline --minutes 5   # 200s, revenue metric flows
python selfheal/scripts/drive.py live                    # 500s: issue + "Failed to validate inventory" logs with cart_json
```

Check in Sentry that `flask-selfheal` has the issue (environment `selfheal`, release
`flask-selfheal@<sha>`), and that Logs shows the line with a `cart_json` attribute.

## 4. Trigger the agents by hand

```bash
gh workflow run selfheal-runner.yml --repo cstavitsky/empower -f title="Critical: Checkout revenue dropped"
gh run watch --repo cstavitsky/empower
```

You should see two `fix` jobs streaming their steps, then two draft PRs in the fork labeled
`selfheal-agent`, a `pytest` check and a reviewer comment on each, and the scorecard (in Slack,
or at the end of the `report` job log). Sentry `selfheal-harness` → Agents shows one
`invoke_agent` trace per run.

## 5. Close the loop locally

1. Merge one PR in the fork. `selfheal-deploy` closes the other one. The deploy job is skipped
   because `SELFHEAL_DEPLOY` isn't set.
2. Pull and restart the local server. The new commit becomes the new release:
   ```bash
   git pull fork selfheal/base
   FLASK_DSN=... python selfheal/scripts/local_server.py --port 8080
   ```
3. Optional: so `Fixes FLASK-SELFHEAL-N` resolves the issue, create the release with commits:
   ```bash
   V=flask-selfheal@$(git rev-parse HEAD)
   sentry-cli releases -o <org> -p flask-selfheal new $V
   sentry-cli releases -o <org> -p flask-selfheal set-commits --auto $V
   sentry-cli releases -o <org> -p flask-selfheal finalize $V
   ```
4. `drive.py live` now returns 200s.

## 6. Optional: the real alert → webhook path

```bash
cd selfheal/receiver
SENTRY_CLIENT_SECRET=<internal integration secret> GITHUB_TOKEN=<your PAT> GITHUB_REPO=cstavitsky/empower \
  gunicorn -b :8081 main:app
cloudflared tunnel --url http://localhost:8081      # or ngrok http 8081
```

In your test org, create an internal integration with Alert Rule Action on and webhook
`<tunnel URL>/sentry`. Then add the metric alert (revenue drop) and/or the issue alert from
`README.md`, with the integration as the action. Run `drive.py baseline`, then `drive.py live`,
and wait for the alert to dispatch the runner. The receiver ignores repeats while a run is
active or an agent PR is open.

## 7. Reset between tries

```bash
SELFHEAL_REPO=cstavitsky/empower SELFHEAL_REMOTE=fork SENTRY_ORG=<org> SENTRY_AUTH_TOKEN=... selfheal/scripts/reset.sh
git pull fork selfheal/base     # then restart local_server.py
```

## Cleaning up

Delete the fork (`gh repo delete cstavitsky/empower`), the two Sentry projects, and the internal integration.
Nothing else was created.
