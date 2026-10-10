# AGENTS.md — Empower Plant

Guidance for AI coding agents working in this repo. Read this before making changes,
and read [`_tda/AGENTS.md`](./_tda/AGENTS.md) before touching anything under `_tda/`.

## What this repo is

Empower Plant is a multi-language/framework **demo** app whose real product is the
**Sentry data it generates**. The instrumentation (Sentry SDK setup, traces, errors,
replay, profiling, distributed tracing) is not incidental — it *is* the thing being
demoed. A change that "works" but quietly alters what shows up in Sentry for the normal
demo is a regression, even if the app still renders.

- **Frontends:** `react` (primary/default), `angular`, `vue`, `next`.
- **Backends:** `flask` (default), `flask-otlp`, `express`, `go`, `laravel`,
  `ruby-on-rails`, `spring-boot`, `spring-boot-otlp`, `aspnetcore`.
- A frontend picks its backend at runtime via `?backend=` (defaults to `flask`).
- Demo behavior is driven by stackable URL query params (`?backend=`, `?se=`,
  `?crash=`, `?rageclick=`, `?userFeedback=`, …) — see the root [README.md](./README.md).
  When adding behavior keyed on the URL, mirror the existing param patterns in
  `react/src/index.js`.

## Running locally

The `./deploy` script is the entry point. `--env=local` runs each project's
`run_local.sh` instead of deploying to GCP:

```
./deploy --env=local flask                 # backend, prod-like
./deploy --env=local react -- npm start    # react hot-reload server
./deploy --env=local react flask laravel   # wires multiple together automatically
```

First local run creates `local.env` from `.local.env.base`; fill in personal DSNs etc.

## The golden rule: do not regress the default demo flow

The path that runs every day — a normal browser pageload with **no special query
params** — is the most important one, and it is exactly what the TDA suite exercises in
production. Any change to a frontend, and **especially any change to Sentry
instrumentation**, must be shown to leave that default flow unchanged.

When you change instrumentation (init, integrations, trace propagation, sampling,
tags, fingerprinting, replay/profiling), do **all** of the following and state the
result explicitly in the PR description — do not assert "should be fine from the code":

1. **Exercise the default flow** (no params): load the app, navigate, trigger the
   checkout error, and confirm pageload/navigation transactions, errors, Session
   Replay, profiling, and backend trace propagation still behave as before.
2. **Exercise the new behavior** you added (e.g. with its query param / entry point).
3. **Confirm the new behavior is inert when not triggered** — if it's gated on a param
   or condition, prove the no-param case early-returns and changes nothing.

A reviewer asking "did you test that this doesn't regress the normal flow?" means this
step was skipped. Bake the answer into the PR up front.

## Test data automation

Anything under `_tda/` (the scheduled Sauce Labs / Appium / Selenium journeys that
keep demo.sentry.io populated) has its own rules and its own failure modes — a passing
pytest run there does **not** mean the journey worked. Read
[`_tda/AGENTS.md`](./_tda/AGENTS.md) before adding or editing tests.
