# Guidelines for AI agents working in `empower`

`empower` ("Empower Plant") is Sentry's multi-framework demo app. Its main
purpose is to **generate realistic data in Sentry** (errors, logs, traces, spans,
replays, etc.) for demos — this makes it distinct from a reference or example
application. **Most of the app code is never seen by customers**, so for the
majority of changes the priority is reliably producing the intended demo data,
not code elegance.

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

## Git / PR workflow

- **Branch off the latest `origin/master`**, not off whatever branch happens to be
  checked out. Local/feature branches often carry unrelated, unmerged commits that
  would otherwise leak into your PR.
- **Keep each PR to a single focused change.** Before pushing, confirm scope by 
  running git diff and git log.
  - If cleanup is needed, rebase onto `origin/master` rather than merging.

## Local development & testing

- **Run a project locally with `./deploy --env=local <project>`** (e.g.
  `./deploy --env=local react`). Multiple projects can be listed to wire them
  together (e.g. `./deploy --env=local react flask`).
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
