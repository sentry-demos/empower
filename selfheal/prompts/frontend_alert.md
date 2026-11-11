**This alert is on a frontend issue** (project `{{FRONTEND_PROJECT}}`): a browser error such as
"Error: 500 - Internal Server Error" from a failed API call. Start from that issue, but its cause
is on the server, so don't change frontend code:

1. Open a recent event of the alert's issue and its trace (`trace` in the event's contexts). Its
   `backendType` tag, when present, names the backend that served the request.
2. In that trace, find the failing backend request (for example `POST /checkout` returning 500)
   and the error it raised in `{{SENTRY_PROJECT}}`. That backend error and its stack trace are
   what you diagnose from here on.
3. If the trace's failing request was served by a backend other than `{{SENTRY_PROJECT}}` (for
   example an Express or Ruby backend), or the trace has no `{{SENTRY_PROJECT}}` error, stop: say
   so in your final message and change no code. This run can only fix `{{SENTRY_PROJECT}}`.

In `result.json` and `pr_body.md`, `issue_short_id` and `issue_url` are the alert's frontend
issue. Name the backend issue you found through the trace too, and show the path: frontend
error → trace → backend error.
