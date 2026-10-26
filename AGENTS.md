# AGENTS.md (selfheal/base)

This branch runs the self-healing demo (see `selfheal/README.md`). Agents working here
are diagnosing and fixing production issues in the Flask backend, reported by Sentry.

## Scope

- Production code lives in `flask/src/`. `/checkout` is in `flask/src/main.py`.
- Only change files under `flask/`. Don't touch `selfheal/`, `.github/`, `*.env`, or other apps.
- Keep the fix minimal: fix the root cause. Don't wrap, swallow, or reword exceptions to make
  an error go away, and don't add broad `try/except`.

## Tests

Run from the repo root:

```
python -m pytest flask/src/test
```

`src/test/conftest.py` stubs Statsig, Postgres and Redis. Use its `client` and `inventory`
fixtures and `make_order()` helper. Every fix needs a regression test in
`src/test/test_checkout.py` that fails before the fix and passes after it.

## Replaying a production request

The checkout error log line carries the failing cart: as the `cart_json` attribute on this
branch, or as a Python dict in the message on production (master). Save it to a file, in either
form, and replay it against your working tree (from the repo root):

```
python selfheal/harness/replay.py path/to/cart.json
```

Exit code 0 means HTTP 200.

## Conventions

- Sentry project and environment: as given in your prompt. The test app is `selfheal-flask` /
  `selfheal`; production is `backend-flask` / `production`.
- Reference the Sentry issue short ID as `Fixes <SHORT-ID>` in the PR body so the issue resolves
  when the release deploys.
