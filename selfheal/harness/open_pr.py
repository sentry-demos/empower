"""Check an agent's fix independently, then open a draft PR from the working tree.

The agent ran the tests and the replay itself; we don't take its word for it. This
re-runs both, refuses changes outside flask/, and records the outcome in verify.json
for the scorecard. A PR is opened only if the change is in scope and the tests pass, so
the reviewer and the human see the verification results either way in the PR body.

Usage (repo root, after run_agent.py):
    python selfheal/harness/open_pr.py --variant with-seer --out DIR
Needs GH_TOKEN (the bot's token, not GITHUB_TOKEN, so PR workflows trigger).
"""
import argparse
import json
import os
import subprocess
import sys

BASE = os.environ.get("BASE_BRANCH", "selfheal/base")
HARNESS = os.path.dirname(os.path.abspath(__file__))


def sh(*cmd, cwd=None, check=True):
    print("$", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=cwd, check=check, text=True, capture_output=True)


def changed_files():
    out = sh("git", "status", "--porcelain").stdout
    return [line[3:].strip() for line in out.splitlines() if line.strip()]


def verify(out):
    files = changed_files()
    result = {"files_changed": files,
              "in_scope": bool(files) and all(f.startswith("flask/") for f in files)}

    tests = sh(sys.executable, "-m", "pytest", "flask/src/test", "-q", check=False)
    result["tests_passed"] = tests.returncode == 0
    result["tests_summary"] = (tests.stdout.strip().splitlines() or [""])[-1]

    cart = os.path.join(out, "cart.json")
    if os.path.exists(cart):
        replay = sh(sys.executable, os.path.join(HARNESS, "replay.py"), cart, check=False)
        lines = replay.stdout.strip().splitlines()
        result["replay_status"] = json.loads(lines[-1])["status"] if lines else None
    else:
        result["replay_status"] = None  # agent never pulled the cart from Sentry Logs

    result["ok"] = result["in_scope"] and result["tests_passed"] and result["replay_status"] == 200
    return result


def open_pr(variant, out, check):
    with open(os.path.join(out, "result.json")) as f:
        agent = json.load(f)
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    branch = f"selfheal/fix-{variant}-{run_id}"
    title = f"[{variant}] Fix {agent.get('issue_short_id', 'checkout failure')}: {agent.get('fix_summary', '')}".strip()

    body_path = os.path.join(out, "pr_body.md")
    body = open(body_path).read() if os.path.exists(body_path) else agent.get("root_cause", "")
    body += (
        "\n\n---\n"
        f"_Opened by the self-heal agent ({variant}) from "
        f"[run {run_id}]({os.environ.get('GITHUB_SERVER_URL', '')}/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{run_id})._\n\n"
        "**Harness verification**\n"
        f"- Files: {', '.join(check['files_changed'])}\n"
        f"- pytest: {'passed' if check['tests_passed'] else 'FAILED'} ({check['tests_summary']})\n"
        f"- Replay of the production cart: HTTP {check['replay_status']}\n"
    )
    with open(body_path, "w") as f:
        f.write(body)

    sh("git", "checkout", "-b", branch)
    sh("git", "add", "--", "flask/")
    sh("git", "commit", "-m", title, "-m", f"Fixes {agent.get('issue_short_id', '')}".strip())
    sh("git", "push", "origin", branch)
    for label in ("selfheal-agent", f"selfheal:{variant}"):
        sh("gh", "label", "create", label, "--force", "--color", "6C5FC7")
    pr = sh("gh", "pr", "create", "--draft", "--base", BASE, "--head", branch, "--title", title,
            "--body-file", body_path, "--label", "selfheal-agent", "--label", f"selfheal:{variant}")
    return pr.stdout.strip().splitlines()[-1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    check = verify(args.out)
    print(f"verify: {json.dumps(check)}", flush=True)

    if check["in_scope"] and check["tests_passed"] and os.path.exists(os.path.join(args.out, "result.json")):
        check["pr_url"] = open_pr(args.variant, args.out, check)
        print(f"Draft PR: {check['pr_url']}", flush=True)
    else:
        check["pr_url"] = None
        print("Not opening a PR: change is out of scope, tests fail, or the agent wrote no result.json", flush=True)

    with open(os.path.join(args.out, "verify.json"), "w") as f:
        json.dump(check, f, indent=2)
    sys.exit(0 if check["pr_url"] else 1)


if __name__ == "__main__":
    main()
