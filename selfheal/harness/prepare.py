"""Render the prompt and MCP config for one self-heal run.

Usage:
    python selfheal/harness/prepare.py fix --variant with-seer|without-seer --alert alert.json \
        --out DIR --mcp-out SECRETS_DIR/mcp.json
    python selfheal/harness/prepare.py review --out DIR

Writes DIR/prompt.md and, for fix runs, the MCP config. That config holds the Sentry token
and the model key, so it goes to its own directory (which run_agent.py stops the agent from
reading), outside git and out of uploaded artifacts.
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


SENTRY_MCP_PACKAGE = os.environ.get("SENTRY_MCP_PACKAGE", "@sentry/mcp-server@0.42.0")


def mcp_config(variant):
    """Sentry's MCP server run locally over stdio with an API token. The hosted MCP
    (mcp.sentry.dev) only takes OAuth sign-ins and rejects API tokens.

    The without-Seer run starts the server with Seer disabled; run_agent.py also
    denies the tool. The server's search tools translate natural language with an
    LLM, so they get the same model key Claude Code uses (see selfheal-claude)."""
    args = ["-y", SENTRY_MCP_PACKAGE]
    if variant == "without-seer":
        args.append("--disable-skills=seer")
    env = {"SENTRY_ACCESS_TOKEN": os.environ["SENTRY_MCP_TOKEN"]}
    if os.environ.get("SELFHEAL_MODEL_PROVIDER", "openrouter") == "openrouter":
        env.update(EMBEDDED_AGENT_PROVIDER="openrouter", OPENROUTER_API_KEY=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    else:
        env.update(EMBEDDED_AGENT_PROVIDER="anthropic", ANTHROPIC_API_KEY=os.environ.get("ANTHROPIC_API_KEY", ""))
    return {"mcpServers": {"sentry": {"type": "stdio", "command": "npx", "args": args, "env": env}}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["fix", "review"])
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--alert", help="JSON file with the alert from the webhook")
    parser.add_argument("--out", required=True)
    parser.add_argument("--mcp-out", help="Where to write the MCP config (fix mode)")
    args = parser.parse_args()
    os.makedirs(args.out, exist_ok=True)
    out = os.path.abspath(args.out)

    if args.mode == "fix":
        with open(args.alert) as f:
            alert = json.dumps(json.load(f), indent=2)
        diagnosis = read_prompt(f"diagnosis_{args.variant.replace('-', '_')}.md")
        prompt = render(read_prompt("diagnose_fix.md"), ALERT=alert, DIAGNOSIS=diagnosis.strip(),
                        OUT=out, SENTRY_ORG=os.environ.get("SENTRY_ORG", "demo"))
        os.makedirs(os.path.dirname(os.path.abspath(args.mcp_out)), exist_ok=True)
        with open(args.mcp_out, "w") as f:
            json.dump(mcp_config(args.variant), f)
        os.chmod(args.mcp_out, 0o600)
    else:
        prompt = render(read_prompt("reviewer.md"), OUT=out)

    with open(os.path.join(out, "prompt.md"), "w") as f:
        f.write(prompt)


if __name__ == "__main__":
    main()
