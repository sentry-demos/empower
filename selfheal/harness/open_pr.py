"""Check an agent's fix independently, then open a draft PR from the working tree.

The agent ran the tests and the replay itself; we don't take its word for it. This
re-runs both, refuses changes outside flask/, and records the outcome in verify.json
for the scorecard. A PR is opened only if the change is in scope and the tests pass, so
the reviewer and the human see the verification results either way in the PR body.

Usage (repo root, after run_agent.py):
    python selfheal/harness/open_pr.py --variant with-seer --out DIR
Needs GH_TOKEN. With the Actions GITHUB_TOKEN, opening the PR triggers no other workflows,
so this also posts the `pytest` commit status on the PR head (the required check) itself.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys

import work  # same directory: python puts the script's folder on sys.path

BASE = os.environ.get("BASE_BRANCH", "selfheal/base")  # the target's base, set by target.py
HARNESS = os.path.dirname(os.path.abspath(__file__))


def sh(*cmd, cwd=None, check=True):
    print("$", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=True)


def changed_files():
    out = sh("git", "status", "--porcelain").stdout
    return [line[3:].strip() for line in out.splitlines() if line.strip()]


def target_paths():
    return [p for p in (os.environ.get("TARGET_PATHS") or "flask/").split(",") if p]


def run_command(command):
    """Run one of the target's commands (tests, check) the way the agent did, from the repo root."""
    args = shlex.split(command)
    if args and args[0] == "python":
        args[0] = sys.executable  # the job's Python, with the target's dependencies
    return sh(*args, check=False)


def last_line(proc):
    return (proc.stdout.strip().splitlines() or proc.stderr.strip().splitlines() or [""])[-1]


def verify(out):
    files = changed_files()
    paths = target_paths()
    result = {"files_changed": files,
              "in_scope": bool(files) and all(f.startswith(tuple(paths)) for f in files)}

    tests = run_command(os.environ.get("TARGET_TESTS") or "python -m pytest flask/src/test -q")
    result["tests_passed"] = tests.returncode == 0
    result["tests_summary"] = last_line(tests)

    result["replay_status"] = None
    cart = os.path.join(out, "cart.json")
    if (os.environ.get("TARGET_REPLAY") or "true") == "true" and os.path.exists(cart):
        replay = sh(sys.executable, os.path.join(HARNESS, "replay.py"), cart, check=False)
        lines = replay.stdout.strip().splitlines()
        result["replay_status"] = json.loads(lines[-1])["status"] if lines else None

    # The target's own proof the problem is gone (e.g. the token budget), if it has one
    result["check_passed"] = None
    if os.environ.get("TARGET_CHECK"):
        checked = run_command(os.environ["TARGET_CHECK"])
        result["check_passed"] = checked.returncode == 0
        result["check_summary"] = last_line(checked)[:500]
    result["check_label"] = os.environ.get("TARGET_CHECK_LABEL", "")

    result["secrets_found"] = leaked_secrets(files)
    result["ok"] = (result["in_scope"] and result["tests_passed"] and result["check_passed"] is not False
                    and result["replay_status"] in (None, 200) and not result["secrets_found"])
    return result


def secret_values():
    """Known secrets the agent's run had access to: the Sentry token(s) and the model key."""
    names = ["SENTRY_MCP_TOKEN", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"]
    names += [n for n in os.environ if n.startswith("SENTRY_MCP_TOKEN_")]
    return {name: os.environ.get(name, "") for name in names}


def leaked_secrets(files):
    """Names of known secrets whose values appear in a changed file. The repo is public,
    so a PR must never carry the Sentry token or the model key, whatever the agent wrote."""
    secrets = secret_values()
    found = []
    for path in files:
        if not os.path.isfile(path):
            continue
        with open(path, errors="ignore") as f:
            text = f.read()
        found += [name for name, value in secrets.items() if len(value) >= 8 and value in text]
    return sorted(set(found))


def open_pr(variant, out, check):
    with open(os.path.join(out, "result.json")) as f:
        agent = json.load(f)
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    branch = f"selfheal/fix-{variant}-{run_id}"
    title = f"[{variant}] Fix {agent.get('issue_short_id', 'the alerted issue')}: {agent.get('fix_summary', '')}".strip()

    body_path = os.path.join(out, "pr_body.md")
    body = open(body_path).read() if os.path.exists(body_path) else agent.get("root_cause", "")
    # Show the work: which Sentry telemetry, Seer and agent steps led to this fix
    work_section = work.render_from(out, variant)
    if work_section:
        body = body.rstrip() + "\n\n" + work_section
    # Public repo: scrub emails, IPs and tokens from everything the agent wrote, too
    body = work.scrub(body)[:60000]  # GitHub caps PR bodies at 65,536 characters
    body += (
        "\n\n---\n"
        f"_Opened by the self-heal agent ({variant}) from "
        f"[run {run_id}]({os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{run_id})._\n\n"
        "**Harness verification**\n"
        f"- Files: {', '.join(check['files_changed'])}\n"
        f"- Tests: {'passed' if check['tests_passed'] else 'FAILED'} ({check['tests_summary']})\n"
    )
    if check.get("replay_status") is not None:
        body += f"- Replay of the failing production request: HTTP {check['replay_status']}\n"
    if check.get("check_passed") is not None:
        label = check.get("check_label") or "Target check"
        body += f"- {label[:1].upper() + label[1:]}: {'passed' if check['check_passed'] else 'FAILED'}\n"
        body += f"  ```\n  {work.scrub(check.get('check_summary', ''))}\n  ```\n"
    with open(body_path, "w") as f:
        f.write(body)

    sh("git", "checkout", "-b", branch)
    sh("git", "add", "--", *target_paths())
    sh("git", "commit", "-m", title, "-m", f"Fixes {agent.get('issue_short_id', '')}".strip())
    sh("git", "push", "origin", branch)
    for label in ("selfheal-agent", f"selfheal:{variant}"):
        sh("gh", "label", "create", label, "--force", "--color", "6C5FC7")
    pr = sh("gh", "pr", "create", "--draft", "--base", BASE, "--head", branch, "--title", title,
            "--body-file", body_path, "--label", "selfheal-agent", "--label", f"selfheal:{variant}")

    head = sh("git", "rev-parse", "HEAD").stdout.strip()
    sh("gh", "api", f"repos/{os.environ['GITHUB_REPOSITORY']}/statuses/{head}",
       "-f", "state=" + ("success" if check["tests_passed"] else "failure"),
       "-f", "context=pytest", "-f", f"description={check['tests_summary'][:140]}",
       "-f", f"target_url={os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ['GITHUB_REPOSITORY']}/actions/runs/{run_id}")
    check["branch"] = branch
    return pr.stdout.strip().splitlines()[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    check = verify(args.out)
    print(f"verify: {json.dumps(check)}", flush=True)

    blockers = []
    if check["secrets_found"]:
        blockers.append(f"changed files contain secret values ({', '.join(check['secrets_found'])})")
    if not check["in_scope"]:
        blockers.append(f"changes are empty or outside {', '.join(target_paths())}")
    if not check["tests_passed"]:
        blockers.append("tests fail")
    if check.get("check_passed") is False:
        blockers.append(f"the target check failed ({check.get('check_label') or os.environ.get('TARGET_CHECK')})")
    if not os.path.exists(os.path.join(args.out, "result.json")):
        blockers.append("the agent wrote no result.json")

    if blockers:
        check["pr_url"] = None
        print(f"Not opening a PR: {'; '.join(blockers)}", flush=True)
    else:
        check["pr_url"] = open_pr(args.variant, args.out, check)
        print(f"Draft PR: {check['pr_url']}", flush=True)

    with open(os.path.join(args.out, "verify.json"), "w") as f:
        json.dump(check, f, indent=2)
    sys.exit(0 if check["pr_url"] else 1)


if __name__ == "__main__":
    main()
