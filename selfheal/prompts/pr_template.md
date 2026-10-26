## Sentry issue

[<SHORT-ID>](<issue url>) — <issue title>

## Root cause

<What is wrong, the file and line, and why it produced this error.>

## Fix

<What changed and why it addresses the root cause rather than the symptom.>

## Verification

- Regression test: `<test name>` fails before the fix, passes after.
- `pytest src/test`: <result>
- Replay of the failing production cart from Sentry Logs: <HTTP status>

Fixes <SHORT-ID>
