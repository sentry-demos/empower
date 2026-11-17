"""Check the telemetry agent's instrumentation, then open it as its own draft PR into the base.

Like open_pr.py for the fix, nothing is taken on the agent's word: the change must stay in the
telemetry paths (the agent and the browser), the tests must pass, the code must actually emit
every new metric the agent listed (sentry_sdk.metrics.<type>("<name>", ...) in Python,
Sentry.metrics.<type>('<name>', ...) in the browser), and no secret may leak. Then it posts
"Telemetry PR ready for review" with the new metrics in the alert's Slack thread.

Usage (repo root, after run_agent.py):
    python selfheal/harness/open_telemetry_pr.py --out DIR --fix-pr-url URL --fix-result result.json
Writes DIR/telemetry_verify.json. Needs GH_TOKEN.
"""
import argparse
import json
import os
import re
import sys

import dashboard_preview  # same directory: python puts the script's folder on sys.path
import issue_refs
import report
import telemetry_spec
import work
from open_pr import (BASE, changed_files, create_pr, last_line, leaked_secrets, run_command, sh, start_branch,
                     target_paths)

LABEL = "selfheal-telemetry"


def added_lines(paths):
    """The lines the agent added in the target's paths (tracked and new files)."""
    sh("git", "add", "--intent-to-add", "--", *paths, check=False)
    diff = sh("git", "diff", "--unified=0", "--", *paths, check=False).stdout
    return [line[1:] for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]


def emits(code, metric):
    """Whether the code calls metrics.<type>("<name>", ...): sentry_sdk.metrics in Python,
    Sentry.metrics in the browser. The name is the first argument, possibly on the next line."""
    quoted = re.compile(rf"[\"'`]{re.escape(metric['name'])}[\"'`]")
    return any(quoted.match(code[call.end():call.end() + 200].lstrip())
               for call in re.finditer(rf"metrics\.{metric['type']}\(", code))


def missing_metrics(lines, spec):
    """The new metrics the added code doesn't emit."""
    code = "\n".join(lines)
    return [m["name"] for m in spec["metrics"] if m["new"] and not emits(code, m)]


def verify(out):
    files, paths = changed_files(), target_paths()
    result = {"files_changed": files,
              "in_scope": bool(files) and all(f.startswith(tuple(paths)) for f in files)}
    tests = run_command(os.environ.get("TARGET_TESTS") or "python -m pytest flask/src/test -q")
    result["tests_passed"] = tests.returncode == 0
    result["tests_summary"] = last_line(tests)
    result["secrets_found"] = leaked_secrets(files)
    try:
        spec = telemetry_spec.load(out)
        result["spec_error"] = None
        result["missing_metrics"] = missing_metrics(added_lines(paths), spec)
    except telemetry_spec.SpecError as err:
        spec, result["spec_error"], result["missing_metrics"] = None, str(err), []
    return result, spec


def blockers(check):
    found = []
    if check["secrets_found"]:
        found.append(f"changed files contain secret values ({', '.join(check['secrets_found'])})")
    if not check["in_scope"]:
        found.append(f"changes are empty or outside {', '.join(target_paths())}")
    if not check["tests_passed"]:
        found.append("tests fail")
    if check["spec_error"]:
        found.append(f"telemetry.json: {check['spec_error']}")
    elif check["missing_metrics"]:
        found.append(f"the added code doesn't emit {', '.join(check['missing_metrics'])} via Sentry metrics")
    return found


def pr_text(out, spec, check, fix_pr_url, fix_result):
    short_id, issue_url = fix_result.get("issue_short_id", ""), fix_result.get("issue_url", "")
    new = [m for m in spec["metrics"] if m["new"]]
    new_names = ", ".join("`" + m["name"] + "`" for m in new)
    title = (f"[telemetry] {short_id or 'Alerted issue'}: instrument the critical flow"
             f" ({len(new)} application metric{'s' if len(new) != 1 else ''}, {len(spec['stages'])} stages)")
    message = f"Follows {fix_pr_url}\n\nSentry issue: {short_id} {issue_url}".strip()
    body_path = os.path.join(out, "pr_body.md")
    body = open(body_path).read() if os.path.exists(body_path) else spec.get("summary", "")
    body = f"_Telemetry follow-up to the self-heal fix in {fix_pr_url}._\n\n" + body.rstrip()
    work_section = work.render_from(out, "telemetry")
    if work_section:
        body += "\n\n" + work_section
    body = work.scrub(body)[:60000]
    settings = json.loads(os.environ.get("TARGET_TELEMETRY") or "{}")
    window = int(settings.get("window_seconds") or 300)
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    body += (
        "\n\n---\n"
        f"_Opened by the self-heal telemetry agent from "
        f"[run {run_id}]({os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{run_id})._"
        " The alert's Slack thread links a pre-filled Sentry monitor form for the proposed monitor and"
        " an unsaved dashboard preview with a row per stage.\n\n"
        "**Harness verification**\n"
        f"- Files: {', '.join(check['files_changed'])}\n"
        f"- Agent tests: passed ({check['tests_summary']}). Browser changes aren't run here.\n"
        f"- Emits every new metric ({new_names}): yes\n"
        f"- Proposed monitor: `{spec['monitor']['sentry_aggregate']}`, alerts when {telemetry_spec.describe(spec, window)}\n"
        + dashboard_section(spec, settings)
    )
    title, body = (issue_refs.neutralize(text, short_id, issue_url) for text in (title, body))
    issue_refs.check({"title": title, "commit": message, "body": body}, short_id, issue_url)
    return title, message, body


def dashboard_section(spec, settings):
    """The stages and the dashboard JSON, so the dashboard can be imported if the preview fails."""
    rows = "\n".join(f"| {n} | {s['name']} | `{s['span_query']}` | `{s['metric_aggregate']}({s['metric']})` |"
                     f" `{s['error_query'] or '-'}` |" for n, s in enumerate(spec["stages"], 1))
    dashboard = dashboard_preview.build_dashboard(spec, settings)
    return ("\n**Dashboard: one row per stage** (throughput · metric · p95 latency · errors)\n\n"
            "| # | Stage | Spans | Metric | Errors |\n|---|---|---|---|---|\n" + rows + "\n\n"
            "<details><summary>Dashboard JSON (for Sentry's dashboards API or import)</summary>\n\n"
            f"```json\n{json.dumps(dashboard, indent=2)}\n```\n</details>\n")


def slack_text(pr_url, spec):
    """Shaped like "PR ready for review"."""
    number = pr_url.rstrip("/").rsplit("/", 1)[-1]
    names = ", ".join("`" + m["name"] + "`" for m in spec["metrics"] if m["new"])
    return (f"*Telemetry PR ready for review* · <{pr_url}|PR #{number}>\n\n"
            f"• New application metrics along the chatbot flow: {names}")


def close_earlier(prefix, keep_url):
    """Earlier telemetry PRs for the same alert and issue: only the latest stays open."""
    listed = sh("gh", "pr", "list", "--base", BASE, "--label", LABEL, "--state", "open",
                "--json", "number,headRefName,url", check=False)
    for pr in json.loads(listed.stdout or "[]") if listed.returncode == 0 else []:
        if pr["headRefName"].startswith(prefix) and pr["url"] != keep_url:
            sh("gh", "pr", "close", str(pr["number"]), "--delete-branch",
               "--comment", f"Superseded by a newer telemetry PR: {keep_url}", check=False)


def open_telemetry_pr(out, spec, check, fix_pr_url, fix_result):
    title, message, body = pr_text(out, spec, check, fix_pr_url, fix_result)
    body_path = os.path.join(out, "telemetry_pr_body.md")
    with open(body_path, "w") as f:
        f.write(body)
    key = os.environ.get("SELFHEAL_RUN_KEY") or "manual"
    prefix = f"selfheal/telemetry-{key}-"
    branch = prefix + os.environ.get("GITHUB_RUN_ID", "local")
    start_branch(branch)  # from the base, so the run's .selfheal/alert.json stays out of the PR
    sh("git", "add", "--", *target_paths())
    sh("git", "commit", "-m", title, "-m", message)
    sh("git", "push", "origin", branch)
    sh("gh", "label", "create", LABEL, "--force", "--color", "6C5FC7", check=False)
    url = create_pr(branch, title, body_path, (LABEL,))
    close_earlier(prefix, url)
    check["branch"] = branch
    return url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--fix-pr-url", required=True)
    parser.add_argument("--fix-result", required=True, help="The fix agent's result.json (issue ID and link)")
    args = parser.parse_args()
    fix_result = report.load(args.fix_result)
    alert = report.load(os.path.join(args.out, "alert.json"))

    check, spec = verify(args.out)
    print(f"verify: {json.dumps(check)}", flush=True)
    found = blockers(check)
    check["pr_url"] = None
    if found:
        print(f"::warning title=No telemetry PR::{'; '.join(found)}", flush=True)
    else:
        check["pr_url"] = open_telemetry_pr(args.out, spec, check, args.fix_pr_url, fix_result)
        print(f"Telemetry PR: {check['pr_url']}", flush=True)
        report.post_status(slack_text(check["pr_url"], spec), alert)
    with open(os.path.join(args.out, "telemetry_verify.json"), "w") as f:
        json.dump(check, f, indent=2)
    sys.exit(0 if check["pr_url"] else 1)


if __name__ == "__main__":
    main()
