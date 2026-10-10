# AGENTS.md — Test Data Automation (`_tda`)

Guidance for AI coding agents adding or editing TDA tests. The parent
[`../AGENTS.md`](../AGENTS.md) covers the repo as a whole; this file is specifically
about how TDA tests really work — and why "the test passed" is almost never enough
evidence here.

## What TDA is

TDA runs end-to-end user journeys on a schedule to generate realistic errors and
transactions in `demo.sentry.io`:

- `desktop_web/` — Selenium against **Sauce Labs** browsers (`desktop_web_driver`).
- `mobile_native/` — Appium against **Sauce Labs** real devices/emulators
  (`android_flutter_driver`, `android_emu_driver`, `ios_sim_driver`, …).

The driver fixtures live in `conftest.py` and are **Sauce-only** — they connect to
`ondemand.us-west-1.saucelabs.com` and need `SAUCE_USERNAME` / `SAUCE_ACCESS_KEY`
(from `.sauce_credentials`).

## ⚠️ Read this before claiming a test passes

These two facts are why a green pytest run is misleading, and are the most common way
an agent "tests it wrong" here:

### 1. Tests are designed NOT to hard-fail

Almost every test wraps its whole body in:

```python
try:
    ...journey...
except Exception as err:
    sentry_sdk.capture_exception(err)
```

A missing element, a broken selector, or a journey that never happened is **swallowed**
— pytest still exits 0. So **exit code 0 ≠ the journey ran**. Verification means
confirming the *outcome*, not the return code:

- Open the **Sauce session** (the run prints `sauceLabsUrl`) and watch the video / read
  the Appium log — confirm each step actually located its element and advanced.
- Open the **Sentry links** printed at the end of the run (the `GENERATED errors` /
  discover links keyed on the `se` tag) and confirm the expected errors/transactions/
  traces actually landed.

Never report a TDA test as passing based on pytest output alone.

### 2. The real environment is Sauce Labs, not your local Appium

Running against a local Appium + UiAutomator2 server is convenient for selector
discovery but is **not** the prescribed verification — the fixtures don't even use it.
Verify the way production runs, per the README
([How to run locally to verify a new test works](./README.md)):

```
./deploy _tda --env=local -- ./run_local.sh mobile_native/android_flutter/test_x.py
./deploy _tda --env=local -- ./run_local.sh desktop_web/test_x.py
```

Then do the Sauce + Sentry confirmation from #1. "Ran it locally on my own Appium" is
not sufficient evidence for a PR.

### 3. Mobile fixtures install a RELEASED artifact, not your local build

The mobile driver fixtures download the app from a **GitHub Release**, so the test runs
against published binaries — not whatever is on your machine or in a sibling repo PR.
For example, `android_flutter_driver` is pinned:

```python
'appium:app': '.../sentry-demos/flutter/releases/download/1.0.0/flutter-android.apk'
```

Consequences you must respect:

- A test that drives a screen/feature **not present in that released build** cannot
  truly pass on Sauce — the element won't exist and (per #1) the failure is swallowed.
- Before such a test can legitimately go green, **both** must be true: (a) the app
  feature is shipped in a published release, and (b) the fixture's release/version is
  bumped to that release. Bumping the version is part of the work, not a follow-up.
- Do not merge or describe as "passing" a test whose journey isn't in the artifact the
  fixture actually installs. If you're adding the test ahead of the release, say so
  explicitly and note it will only verify once the release + version bump land.

## Conventions

- Test **files and functions must be prefixed `test_`** or pytest won't discover them.
  No registration needed beyond placing the file in the right directory.
- Find Appium selectors with the Appium Inspector connected to a live Sauce session;
  match the style of neighboring tests (`AppiumBy.ACCESSIBILITY_ID`,
  `AppiumBy.ANDROID_UIAUTOMATOR` with `description(...)`, etc.).
- Leave a short `time.sleep(...)` (or equivalent) before teardown so async
  transactions/errors flush to Sentry before the session quits.
- Tune `implicitly_wait` down around optional/conditional dialogs so you don't block the
  full 20 s when an element is legitimately absent (see
  `test_checkout_flutter_android.py`).
- The `se` tag (set per-fixture from `se_prefix`) is how a run's data is found in
  Sentry — keep it intact.

## Modes

- `config.yaml` → `mode: direct` — production: events ingest straight to
  `demo.sentry.io`.
- `config.local.yaml` → `mode: mock` — events captured by the local mini-relay as
  templates; used with `--env=local`.
