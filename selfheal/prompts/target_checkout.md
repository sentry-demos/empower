This is the Flask backend (`flask/src/`); `/checkout` is in `flask/src/main.py`. The error message
may be misleading, so follow chained exceptions to the real one.

**Get the failing request.** Search Sentry Logs in `{{SENTRY_PROJECT}}` for the most recent
"Failed to validate inventory" log line, and save its cart to `{{OUT}}/cart.json`:

- If the log has a `cart_json` attribute, write that JSON unchanged.
- Otherwise the cart is in the message itself, as a Python dict:
  `Failed to validate inventory with cart: {'items': [...], 'quantities': {'4': 1}, 'total': 175}`.
  (It may also be in a `sentry.message.parameter.0` attribute.) Write just the `{...}` part,
  unchanged. `replay.py` accepts both JSON and that Python form.

If no such log line exists in the last 24 hours, skip the replay and say so in your report.

Put the regression test in `flask/src/test/test_checkout.py`.

**Impact** (in `result.json`): add `failed_checkouts`, `users_affected`, `first_seen` and
`lost_revenue_usd` to `impact`, all over the same window, e.g. the last 24 hours:
- `failed_checkouts`: "Failed to validate inventory" log lines (or issue events) in that window.
- `lost_revenue_usd`: the sum of `total` across those same carts.
- `users_affected`: distinct users in that window, or `null` if events carry no user.
- `first_seen`: when the failures in that window started.

`impact_short` example: "~$18,000 in failed orders · 34 failed checkouts in 24h".
