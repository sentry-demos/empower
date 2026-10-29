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


def mcp_token(org):
    """The Sentry token for this org: SENTRY_MCP_TOKEN_TEAM_SE for team-se, falling back to
    SENTRY_MCP_TOKEN (the default org's). Integration tokens only work in their own org."""
    key = "SENTRY_MCP_TOKEN_" + org.upper().replace("-", "_")
    token = os.environ.get(key) or os.environ.get("SENTRY_MCP_TOKEN")
    if not token:
        raise SystemExit(f"No Sentry token for org {org}: set {key} (or SENTRY_MCP_TOKEN)")
    return token


def bash_commands(tests, check, replay):
    """The Bash commands the agent may run, as prompt lines and as allow rules."""
    lines = [f"  - `{tests}` (you may add `-x` or a test path)"]
    rules = ["Bash(python -m pytest:*)"]
    if replay:
        lines.append("  - `python selfheal/harness/replay.py <path to cart.json>`")
        rules.append("Bash(python selfheal/harness/replay.py:*)")
    if check:
        lines.append(f"  - `{check}`")
        rules.append(f"Bash({check}:*)")
    return "\n".join(lines), " ".join(rules)


def mcp_config(variant):
    """Sentry's MCP server run locally over stdio with an API token. The hosted MCP
    (mcp.sentry.dev) only takes OAuth sign-ins and rejects API tokens.

    The without-Seer run starts the server with Seer disabled; run_agent.py also
    denies the tool. The server's search tools translate natural language with an
    LLM, so they get the same model key Claude Code uses (see selfheal-claude)."""
    args = ["-y", SENTRY_MCP_PACKAGE]
    if variant == "without-seer":
        args.append("--disable-skills=seer")
    env = {"SENTRY_ACCESS_TOKEN": mcp_token(os.environ.get("SENTRY_ORG") or "demo")}
    if os.environ.get("SELFHEAL_MODEL_PROVIDER", "openrouter") == "openrouter":
        env.update(EMBEDDED_AGENT_PROVIDER="openrouter", OPENROUTER_API_KEY=os.environ.get("ANTHROPIC_AUTH_TOKEN", ""))
    else:
        env.update(EMBEDDED_AGENT_PROVIDER="anthropic", ANTHROPIC_API_KEY=os.environ.get("ANTHROPIC_API_KEY", ""))
    return {"mcpServers": {"sentry": {"type": "stdio", "command": "npx", "args": args, "env": env}}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["fix", "review", "allowed-bash"])
    parser.add_argument("--variant", choices=VARIANTS)
    parser.add_argument("--alert", help="JSON file with the alert from the webhook")
    parser.add_argument("--out", help="Output dir (fix and review modes)")
    parser.add_argument("--mcp-out", help="Where to write the MCP config (fix mode)")
    args = parser.parse_args()
    if args.mode == "allowed-bash":
        # The --allowedTools Bash rules matching the commands the prompt lists
        _, rules = bash_commands(os.environ.get("TARGET_TESTS") or "python -m pytest flask/src/test -q",
                                 os.environ.get("TARGET_CHECK", ""),
                                 (os.environ.get("TARGET_REPLAY") or "true") == "true")
        print(rules)
        return
    os.makedirs(args.out, exist_ok=True)
    out = os.path.abspath(args.out)

    if args.mode == "fix":
        with open(args.alert) as f:
            alert = json.dumps(json.load(f), indent=2)
        diagnosis = read_prompt(f"diagnosis_{args.variant.replace('-', '_')}.md")
        # The target's settings, from target.py (defaults are the checkout target's)
        tests = os.environ.get("TARGET_TESTS") or "python -m pytest flask/src/test -q"
        check = os.environ.get("TARGET_CHECK", "")
        replay = (os.environ.get("TARGET_REPLAY") or "true") == "true"
        environment = os.environ.get("SENTRY_ENVIRONMENT", "")
        commands, _ = bash_commands(tests, check, replay)
        verify = []
        if replay:
            verify.append("- Run `python selfheal/harness/replay.py " + out + "/cart.json`. It must return 200.")
        if check:
            verify.append(f"- Run `{check}`. It must pass.")
        # DIAGNOSIS and TARGET go in first: they use the placeholders filled after them
        prompt = render(read_prompt("diagnose_fix.md"),
                        DIAGNOSIS=diagnosis.strip(),
                        TARGET=read_prompt(os.environ.get("TARGET_PROMPT") or "target_checkout.md").strip(),
                        ALERT=alert, OUT=out, TESTS=tests, CHECK=check, BASH_COMMANDS=commands,
                        VERIFY_STEP="\n".join(verify),
                        PATHS=", ".join(f"`{p}`" for p in (os.environ.get("TARGET_PATHS") or "flask/").split(",")),
                        ENVIRONMENT_NOTE=f" Environment: `{environment}`." if environment else "",
                        ENVIRONMENT_INLINE=f", environment `{environment}`," if environment else "",
                        SENTRY_ORG=os.environ.get("SENTRY_ORG") or "demo",
                        SENTRY_PROJECT=os.environ.get("SENTRY_PROJECT") or "backend-flask")
        os.makedirs(os.path.dirname(os.path.abspath(args.mcp_out)), exist_ok=True)
        with open(args.mcp_out, "w") as f:
            json.dump(mcp_config(args.variant), f)
        os.chmod(args.mcp_out, 0o600)
    else:
        prompt = render(read_prompt("reviewer.md"), OUT=out,
                        TESTS=os.environ.get("TARGET_TESTS") or "python -m pytest flask/src/test -q",
                        PATHS=", ".join(f"`{p}`" for p in (os.environ.get("TARGET_PATHS") or "flask/").split(",")))

    with open(os.path.join(out, "prompt.md"), "w") as f:
        f.write(prompt)


if __name__ == "__main__":
    main()
