Use the Sentry MCP tools. Seer is not available in this run; diagnose it yourself.

a. Find the issue behind the alert: the most recent unresolved issue in `{{SENTRY_PROJECT}}`{{ENVIRONMENT_INLINE}}
   that lines up with the alert's timing. If the alert names an issue,
   use that one.
b. Read the issue details: the full stack trace including chained exceptions, tags, and the
   trace for a recent event.
c. Read the code in the stack trace and work out the root cause yourself.
