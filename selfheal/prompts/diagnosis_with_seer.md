Use the Sentry MCP tools, with Seer.

a. Find the issue behind the alert: the most recent unresolved issue in `{{SENTRY_PROJECT}}`,
   environment `{{SENTRY_ENVIRONMENT}}`, that lines up with the alert's timing. If the alert names an issue,
   use that one.
b. Run `analyze_issue_with_seer` on it and read Seer's root cause analysis.
c. Open the file and lines Seer points to and confirm the cause in the code.
