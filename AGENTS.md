# Guidelines for AI agents working in `empower`

`empower` ("Empower Plant") is Sentry's multi-framework demo application. Its
purpose is to **demonstrate Sentry SDK instrumentation**, so the instrumentation
code *is* the product. Keep that in mind for every change.

## Sentry demo philosophy

- **Never resolve or close Sentry issues from this repo.** The errors it produces
  are intentional demo data that must keep firing. Do not put `Fixes <PROJECT-ID>`
  (e.g. `Fixes FRONTEND-REACT-715`) in commits or PRs, and do not otherwise mark
  demo issues resolved.
- **Keep standard Sentry SDK calls explicit and visible at the call site.** The
  demo's value is showing how the real SDK API is used, e.g.
  `Sentry.captureException(...)`, `Sentry.startSpan(...)`. Don't hide these inside
  wrappers or abstractions. A helper may *prepare* context (scope, tags, captured
  location, etc.), but the actual SDK call should stay where a reader can see it.
- **Prefer the simplest instrumentation that demonstrates the feature.** Avoid
  unnecessary wrapping/indirection; favor the plain SDK usage a customer would
  recognize.

## Git / PR workflow

- **Branch off the latest `origin/master`**, not off whatever branch happens to be
  checked out. Local/feature branches often carry unrelated, unmerged commits that
  would otherwise leak into your PR.
- **Keep each PR to a single focused change.** Before pushing, confirm scope:
  - `git log --oneline origin/master..HEAD` shows only your commit(s)
  - `git diff --stat origin/master..HEAD` shows only your files
  - If cleanup is needed, rebase onto `origin/master` rather than merging.
- Don't push branches or open/modify PRs unless asked.

## Local development & testing

- **Run a project locally with `./deploy --env=local <project>`** (e.g.
  `./deploy --env=local react`). Multiple projects can be listed to wire them
  together (e.g. `./deploy --env=local react flask`).
- **Use Node 22** (`nvm use 22`). `package.json` engines require `node >=22 <23`;
  Node 20 fails `npm ci` with `EBADENGINE`.
- `./deploy` needs Google Cloud auth (`gcloud auth login`) to fetch secrets and is
  interactive.
- The React app is ready when the log shows
  `INFO  Accepting connections at http://localhost:3000`. Verifying demo behavior
  requires manual interaction in a browser, so **prompt the user to test once you
  see that line** instead of assuming success.
