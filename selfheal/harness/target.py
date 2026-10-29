"""Resolve the self-heal target for an alert (see selfheal/targets.json).

    python selfheal/harness/target.py --alert alert.json --github-env
        Appends the target's settings to $GITHUB_ENV for the rest of the job: SELFHEAL_TARGET,
        BASE_BRANCH, SENTRY_ORG, SENTRY_PROJECT, SENTRY_ENVIRONMENT, TARGET_PATHS,
        TARGET_INSTALL, TARGET_TESTS, TARGET_CHECK, TARGET_CHECK_LABEL, TARGET_REPLAY,
        TARGET_PROMPT, SELFHEAL_SLACK_ALERT_MATCH (unless set), and the target's test_env.

The alert says which target it is for ("target", set by the receiver). Older alert files
without one fall back to the first target for their org, then to "checkout".
"""
import argparse
import json
import os
import shlex

TARGETS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "targets.json")
DEFAULT_TARGET = "checkout"


def load_targets(path=TARGETS_FILE):
    with open(path) as f:
        return {name: t for name, t in json.load(f).items() if not name.startswith("_")}


def pick(targets, org=None, project=None):
    """Target name for an alert from this org/project: project match first, then org."""
    in_org = [name for name, t in targets.items() if t["org"] == org]
    for name in in_org:
        if project and project in targets[name].get("projects", []):
            return name
    return in_org[0] if in_org else None


def resolve(alert, targets):
    name = alert.get("target") or pick(targets, alert.get("org"), alert.get("project")) or DEFAULT_TARGET
    return name, targets[name]


def env_lines(name, target, alert):
    # Repo variables (SELFHEAL_VAR_*) stay as overrides for the checkout target, so demo works
    # as before; other targets use targets.json only
    checkout = name == DEFAULT_TARGET
    def setting(var, value):
        return (os.environ.get(f"SELFHEAL_VAR_{var}") or value) if checkout else value
    lines = {
        "SELFHEAL_TARGET": name,
        "BASE_BRANCH": target["base"],
        "SENTRY_ORG": alert.get("org") or setting("SENTRY_ORG", target["org"]),
        "SENTRY_PROJECT": alert.get("project_slug") or setting("SENTRY_PROJECT", target["project"]),
        "SENTRY_ENVIRONMENT": setting("SENTRY_ENVIRONMENT", target.get("environment", "")),
        "TARGET_PATHS": ",".join(target["paths"]),
        "TARGET_INSTALL": target["install"],
        "TARGET_TESTS": target["tests"],
        "TARGET_CHECK": target.get("check", ""),
        "TARGET_CHECK_LABEL": target.get("check_label", ""),
        "TARGET_REPLAY": "true" if target.get("replay") else "false",
        "TARGET_PROMPT": target["prompt"],
    }
    lines["SELFHEAL_SLACK_ALERT_MATCH"] = setting("SLACK_ALERT_MATCH", target.get("slack_match", ""))
    lines.update(target.get("test_env", {}))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alert", required=True)
    parser.add_argument("--github-env", action="store_true", help="append to $GITHUB_ENV")
    parser.add_argument("--shell", action="store_true", help='print `export K=V` lines for eval "$(...)"')
    args = parser.parse_args()
    with open(args.alert) as f:
        alert = json.load(f)
    name, target = resolve(alert, load_targets())
    lines = env_lines(name, target, alert)
    text = "".join(f"{k}={v}\n" for k, v in lines.items())
    if args.github_env:
        with open(os.environ["GITHUB_ENV"], "a") as f:
            f.write(text)
    if args.shell:
        print("".join(f"export {k}={shlex.quote(v)}\n" for k, v in lines.items()), end="")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
