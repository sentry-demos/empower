# AGENTS.md (self-heal branches)

This branch runs the self-healing demo (see `selfheal/README.md`). Agents working here diagnose
and fix production issues reported by Sentry. Your prompt names the Sentry org and project, the
folders you may change, and the commands you may run.

## Scope

- Change files only under the folders your prompt names: `flask/` for the checkout target (the
  Flask backend; `/checkout` is in `flask/src/main.py`), `agent/` for the shopping-agent target.
- Don't touch `selfheal/`, `.github/`, `*.env`, or other apps.
- Fix the root cause with the smallest correct change. Don't wrap, swallow, or reword exceptions
  to make an error go away, don't add broad `try/except`, and don't special-case demo inputs.
- Fixes must be real. Some code here fails on purpose for demos, and its tests may pin the bug
  down. Where a test asserts the bug, change it to assert the correct behaviour.

## Tests

Run from the repo root, using the command your prompt gives:

- Flask: `python -m pytest flask/src/test`. `src/test/conftest.py` stubs Statsig, Postgres and
  Redis; use its `client` and `inventory` fixtures and `make_order()` helper, and put checkout
  regression tests in `src/test/test_checkout.py`.
- Agent: `python -m pytest agent/tests` (the job sets `PYTHONPATH=agent` and test settings).

Every fix needs a regression test that fails before the fix and passes after it.

## Proving the fix

- Checkout: the checkout error log line carries the failing cart, as the `cart_json` attribute or
  as a Python dict in the message. Save it to a file and replay it against your working tree:
  `python selfheal/harness/replay.py path/to/cart.json` (exit code 0 means HTTP 200).
- Shopping agent: `python selfheal/harness/checks/policy_tokens.py` measures the policy tool's
  output in tokens; it must pass.

## Conventions

- Reference the Sentry issue short ID as `Fixes <SHORT-ID>` in the PR body.
