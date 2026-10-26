"""Render the prompt and MCP config for one self-heal run.

Usage:
    python selfheal/harness/prepare.py fix --variant with-seer|without-seer --alert alert.json --out DIR
    python selfheal/harness/prepare.py review --out DIR

Writes DIR/prompt.md and, for fix runs, DIR/mcp.json. The MCP config holds the Sentry
token, so DIR must stay out of git and out of uploaded artifacts.
"""
import argparse
import json
import os

PROMPTS = os.path.join(os.path.dirname(__file__), "..", "prompts")
VARIANTS = ("with-seer", "without-seer")


def read_prompt(name):
    with open(os.path.join(PROMPTS, name)) as f:
        return f.read()


def render(template, **values):
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def mcp_config(variant):
    """Remote Sentry MCP, authenticated with a user token so no browser sign-in is needed.
    The without-Seer run turns Seer off server-side; run_agent.py also denies the tool."""
    url = os.environ.get("SENTRY_MCP_URL", "https://mcp.sentry.dev/mcp")
    if variant == "without-seer":
        url += ("&" if "?" in url else "?") + "disable-skills=seer"
    header = os.environ.get("SENTRY_MCP_AUTH_HEADER", "Authorization")
    prefix = os.environ.get("SENTRY_MCP_AUTH_PREFIX", "Bearer ")
    token = os.environ["SENTRY_MCP_TOKEN"]
    return {"mcpServers": {"sentry": {"type": "http", "url": url, "headers": {header: prefix + token}}}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["fix", "review"])
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--alert", help="JSON file with the alert from the webhook")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    out = os.path.abspath(args.out)

    if args.mode == "fix":
        with open(args.alert) as f:
            alert = json.dumps(json.load(f), indent=2)
        diagnosis = read_prompt(f"diagnosis_{args.variant.replace('-', '_')}.md")
        prompt = render(read_prompt("diagnose_fix.md"), ALERT=alert, DIAGNOSIS=diagnosis.strip(),
                        OUT=out, SENTRY_ORG=os.environ.get("SENTRY_ORG", "demo"))
        with open(os.path.join(out, "mcp.json"), "w") as f:
            json.dump(mcp_config(args.variant), f)
    else:
        prompt = render(read_prompt("reviewer.md"), OUT=out)

    with open(os.path.join(out, "prompt.md"), "w") as f:
        f.write(prompt)


if __name__ == "__main__":
    main()
