# Guidelines for AI agents working in `empower`

> [!IMPORTANT]
> **This repo uses a custom `./deploy` framework. NEVER run or build a project
> directly** (`npm run`, `npm start`, `npm build`, `mvn`, `flask run`, `go run`,
> etc.). Those commands will fail or misbehave, because `./deploy` first generates
> each project's `*.template` files and injects the required env/secrets. Always
> go through `./deploy --env=<env> <project>` (see "Local development & testing").

`empower` ("Empower Plant") is Sentry's multi-framework demo app. Its main
purpose is to **generate realistic data in Sentry** (errors, logs, traces, spans,
replays, etc.) for demos — this makes it distinct from a reference or example
application. **Most of the app code is never seen by customers**, so for the
majority of changes the priority is reliably producing the intended demo data,
not code elegance. It is **not production code** — it's co-owned by Solutions
Engineers (SEs) who aren't all expert SWEs, so minimize unnecessary change and
complexity.

The exception is **code that shows up in the Sentry UI during a demo** — e.g. the
source lines shown as stack-trace / code context around a captured error, or certain
database queries that show up in spans the demo audience may see, for example in a
"Slow DB query" issue, or function names in Profiling. That code *is* on display, 
so hold it to a higher bar (see below).

## Sentry demo philosophy

- **Never resolve or close Sentry issues from this repo.** The errors it produces
  are intentional demo data that must keep firing. Do not put `Fixes <SENTRY-SHORT-ID>`
  (e.g. `Fixes FRONTEND-REACT-715`) in commits or PRs, and do not otherwise mark
  demo issues resolved.
- **In demo-visible code, keep standard Sentry SDK calls explicit and readable at
  the call site.** This applies to code a customer will see in the Sentry UI
  (stack-trace context around a captured error, etc.). There the plain SDK usage is
  the point, e.g. `Sentry.captureException(...)` — don't hide it behind wrappers or abstractions. A helper may *prepare* context (scope, tags, captured location, etc.), but the actual SDK call should stay where a viewer can see it.
- **Chesterton's Fence — don't remove or "modernize" what you don't understand.**
  Hacks, scaffolding, "internal" comments, and deliberately outdated instrumentation
  are often intentional to keep the picture in `demo.sentry.io` looking right. Don't
  delete them or proactively upgrade the Sentry SDK / other instrumentation; when
  unsure about the purpose of existing code, ask the user (an SE) before changing it.
- **Never touch Sentry Org or Project settings** as part of a code change.
- **No real or real-looking PII in demo data.** Emails must always be
  `@example.com` (never a plausible real address); don't introduce real names,
  tokens, or secrets.

## Git / PR workflow

- **Branch off the latest `origin/master`**, not off whatever branch happens to be
  checked out. Local/feature branches often carry unrelated, unmerged commits that
  would otherwise leak into your PR.
- **Keep each PR to a single focused change.** Before pushing, confirm scope by 
  running git diff and git log.
  - If cleanup is needed, rebase onto `origin/master` rather than merging.
- **Open PRs as drafts, and only after testing has passed** (see Local
  development & testing) — don't publish a PR straight from an untested change.
- **Every PR must include a brief `## Testing` section** stating how it was
  tested: the deploy command used and what was verified (if not sure how what 
  the user tested - ask them, they must supply it! Just say that you are supposed
  to ask that, that's the protocol), e.g.

  ```
  ## Testing
  `./deploy --env=local react`
  User tested manually and confirmed: app loads, demo flow (/product -> /cart
  -> /checkout-form -> submit_checkout -> /error) is intact and trace waterfall
  looks about right.
  ```
- **Prefix commit messages and PR titles with the project in brackets**, e.g.
  `[react]`, `[flask]`.
- **Merging to `master` auto-deploys to production** for every sub-project except
  those listed in `auto-deploy.exclude`. Treat a merge as a production deploy.

## Code conventions

- **Don't break TDA selectors.** In web projects, don't change HTML `id`s,
  `class`es, or other element selectors — the `_tda` test automation relies on
  them to drive the app.
- **Freeze dependencies.** Pin versions (in `package.json` use `~`, not `^`) and
  use `npm ci`, not `npm install`, unless you're intentionally upgrading — which is
  its own dedicated change.
- **Don't fake slowness with `pg_sleep()`** (or equivalent); use the "sleepy
  views" pattern already in the backends, ideally existing ones, see: 
  https://github.com/sentry-demos/empower/pull/223
- **Don't mix reformatting with logic changes.** If your editor auto-formats,
  reformatting should be its own separate PR so real changes stay reviewable.
- **Keep `README.md` in sync.** Update the top-level (and relevant per-project)
  `README.md` when a change warrants it — new major features, new/changed query
  parameters, changes to the `./deploy` workflow, etc.
- **Don't make willy-nilly changes to the deploy system.** The `./deploy` script
  and the utility scripts in `_bin/` it relies on are deliberately generic and
  already work across a dozen-plus apps. Change them only with a strong, general
  reason, and keep them generalizable — **absolutely no one-off hacks for a single
  project.**

## Infrastructure & data live in this repo

- **The demo Postgres schema and seed content are defined in code** under
  `_postgres/` (e.g. `_postgres/data/empowerplant.sql`). Change the demo data and
  schema there — don't hand-edit a live database.
- **DNS / domain mappings are defined in code** under `_dns/`. Services are
  exposed at short `*.empower-plant.com` hostnames.
- **When talking to the user, refer to services by their short
  `*.empower-plant.com` URLs** (e.g. `staging-flask.empower-plant.com`), not the
  long App Engine URLs that `gcloud` prints.

## Local development & testing

- **When a change is complete, always offer to test it before opening a PR.**
  Offer a local run first (`--env=local`); for more complex changes also offer a
  staging deploy (`./deploy --env=staging <project>` — it's fine to overwrite
  whatever is currently deployed in staging). Only once local testing (plus
  staging where warranted) has passed should you publish the PR, as a draft.
- **Apps must be run through the `./deploy` script, never directly** (`npm run`,
  etc.) — `deploy` populates `*.template` files and env/secrets they depend on.
  Read the top-level `README.md` (and any per-project `README`) first.
- **Run a project locally with `./deploy --env=local <project>`** (e.g.
  `./deploy --env=local react`). Multiple projects can be listed to wire them
  together (e.g. `./deploy --env=local react flask`).
- The production frontend is `empower-plant.com`; switch its backend with the
  `/?backend=<project dir>` query param. The demo org slug is `demo`.
- **For changes that need a full distributed trace to verify** (e.g. the flagship
  performance trace, usually the `/products` page), deploy **frontend and backend
  together** in the same environment so the trace stays connected in one org
  (local → the user's own Sentry org; staging → `team-se`). Default to the Flask
  backend unless there's a reason to use another, e.g.
  `./deploy --env=local react flask`.
- **Use Node 22** (`nvm use 22`). `package.json` engines require `node >=22 <23`;
  Node 20 fails `npm ci` with `EBADENGINE`.
- `./deploy` needs Google Cloud auth to fetch secrets. If it stops at
  `You are not authenticated with Google Cloud` (the account's token has expired),
  the fix is a browser sign-in — an agent can't complete it headless. Don't
  overthink it: run `gcloud auth login`, hand the user the auth URL it prints, and
  let them finish the browser flow. Keep the `gcloud auth login` process running
  until they're done so its `localhost` callback can complete.
- The React app is ready when the log shows
  `INFO  Accepting connections at http://localhost:3000`. Verifying demo behavior
  requires manual interaction in a browser, so **prompt the user to test once you
  see that line** instead of assuming success.
- **After the user tests manually, ask them for links to the Sentry
  events/artifacts** their testing generated (issues, traces, replays, profiles,
  etc.) — in their personal org for `--env=local`, or `team-se` for staging. Use
  them to confirm the change works and reference them in the PR's `## Testing`
  section.
