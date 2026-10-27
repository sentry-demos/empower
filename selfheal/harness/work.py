"""Render the "How this fix was found" section of an agent PR from timeline.json.

Splits the run into the three layers a customer cares about:
  1. Sentry telemetry: what the agent pulled from Sentry through the MCP (issues, stack traces,
     traces, logs), i.e. data Sentry already had.
  2. Seer: Sentry's AI root-cause analysis (with-Seer runs only).
  3. Agent: Claude Code's own work on the code (read, edit, test, replay).

Inputs and results are shortened and scrubbed (emails, IPs, tokens, known secret values),
because the PR lives in a public repo.
"""
import json
import os
import re

REPO_ROOT_PREFIXES = ("/home/runner/work/empower/empower/",)
RUN_OUTPUT_RE = re.compile(r"/home/runner/work/_temp/selfheal/[^/]+/")
SCRUB_PATTERNS = [
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "<email>"),
    (re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b"), "<ip>"),
    (re.compile(r"\b(?:sntry[su]_|sk-|xox[abp]-|ghs_|ghp_|github_pat_)[\w-]+"), "<redacted>"),
]


def scrub(text):
    text = str(text)
    for name in ("SENTRY_MCP_TOKEN", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_API_KEY"):
        value = os.environ.get(name, "")
        if len(value) >= 8:
            text = text.replace(value, "<redacted>")
    for pattern, replacement in SCRUB_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def short_path(path):
    path = str(path)
    for prefix in REPO_ROOT_PREFIXES:
        if path.startswith(prefix):
            return path[len(prefix):]
    return RUN_OUTPUT_RE.sub("(run output)/", path)


def cell(text, limit):
    """One table cell: scrubbed, single line, pipes escaped, truncated."""
    text = " ".join(scrub(text).split()).replace("|", "\\|")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def result_summary(result, error):
    """First meaningful line of a tool result, skipping markdown headings and boilerplate."""
    if error:
        return "error: " + cell(result, 150)
    lines = [line.strip() for line in str(result).splitlines() if line.strip()]
    for line in lines:
        # Skip markdown headings and the MCP's presentation hints; they aren't the result
        if not line.startswith("#") and "suggested presentation" not in line.lower():
            return cell(line, 150)
    return cell(lines[0].lstrip("#"), 150) if lines else ""


def mcp_args(tool_input):
    args = {k: v for k, v in tool_input.items() if k not in ("organizationSlug", "regionUrl")}
    return cell(", ".join(f"{k}={json.dumps(v) if not isinstance(v, str) else v}" for k, v in args.items()), 140)


def agent_step(name, tool_input, result, error):
    """(step, detail) for a Claude Code tool call."""
    if name == "Read":
        return "Read code", f"`{short_path(tool_input.get('file_path', ''))}`"
    if name in ("Edit", "Write"):
        path = short_path(tool_input.get("file_path", ""))
        if path.startswith("(run output)/"):
            return "Wrote output", f"`{path}`"
        return ("Edited code" if name == "Edit" else "Wrote file"), f"`{path}`"
    if name in ("Grep", "Glob"):
        return "Searched code", f"`{cell(tool_input.get('pattern', ''), 80)}`"
    if name == "Bash":
        command = short_path(tool_input.get("command", ""))
        outcome = "failed" if error else "passed"
        kind = "Replayed failing request" if "replay.py" in command else "Ran tests"
        last = cell((str(result).strip().splitlines() or [""])[-1], 100)
        return f"{kind}: {outcome}", f"`{cell(command, 80)}` → {last}"
    return name, cell(json.dumps(tool_input), 100)


def render(timeline, stats, variant):
    mcp = [t for t in timeline if t["type"] == "tool" and t["name"].startswith("mcp__sentry__")
           and not t["name"].endswith("analyze_issue_with_seer")]
    seer = [t for t in timeline if t["type"] == "tool" and t["name"].endswith("analyze_issue_with_seer")]
    agent = [t for t in timeline if t["type"] == "tool" and not t["name"].startswith(("mcp__", "ToolSearch"))]
    notes = [t["text"] for t in timeline if t["type"] == "note"]

    lines = [
        "## How this fix was found",
        "",
        "| Layer | What it is | Used in this run |",
        "|---|---|---|",
        f"| **Sentry telemetry** (MCP) | Data Sentry already had: issues, stack traces, traces, logs | {len(mcp)} calls |",
        f"| **Seer** | Sentry's AI root-cause analysis on that telemetry | "
        + (f"{len(seer)} call{'s' if len(seer) != 1 else ''}" if seer else "not used" + (" (without-Seer run)" if variant == "without-seer" else "")) + " |",
        f"| **Agent** (Claude Code) | Reads the code, changes it, runs tests, replays the failing request | {len(agent)} steps |",
        "",
    ]
    if stats:
        lines += [f"{stats.get('duration_s')}s · {stats.get('turns')} turns · "
                  f"{stats.get('input_tokens', 0) + stats.get('output_tokens', 0):,} tokens · "
                  f"${stats.get('cost_usd', 0):.2f} · model `{stats.get('model')}`", ""]

    lines += ["### 1. Sentry telemetry (MCP)", ""]
    if mcp:
        lines += ["| At | Tool | Asked for | Returned |", "|---|---|---|---|"]
        lines += [f"| {t['at_s']}s | `{t['name'].removeprefix('mcp__sentry__')}` | {mcp_args(t['input'])} | "
                  f"{result_summary(t['result'], t['error'])} |" for t in mcp]
    else:
        lines.append("No Sentry calls.")

    lines += ["", "### 2. Seer", ""]
    if seer:
        lines += ["| At | Call | Returned |", "|---|---|---|"]
        lines += [f"| {t['at_s']}s | `analyze_issue_with_seer` {mcp_args(t['input'])} | "
                  f"{result_summary(t['result'], t['error'])} |" for t in seer]
    elif variant == "without-seer":
        lines.append("Not used: this run had Seer turned off and diagnosed from the raw telemetry above.")
    else:
        lines.append("Not called.")

    lines += ["", "### 3. Agent (Claude Code)", "", "| At | Step | Detail |", "|---|---|---|"]
    for t in agent:
        step, detail = agent_step(t["name"], t["input"], t["result"], t["error"])
        lines.append(f"| {t['at_s']}s | {step} | {detail} |")

    if notes:
        lines += ["", "<details><summary>Agent's notes, in order</summary>", ""]
        lines += [f"{i}. {cell(note, 400)}" for i, note in enumerate(notes, 1)]
        lines += ["", "</details>"]
    return "\n".join(lines) + "\n"


def render_from(out, variant):
    try:
        with open(os.path.join(out, "timeline.json")) as f:
            timeline = json.load(f)
    except (OSError, json.JSONDecodeError):
        return ""
    try:
        with open(os.path.join(out, "stats.json")) as f:
            stats = json.load(f)
    except (OSError, json.JSONDecodeError):
        stats = {}
    return render(timeline, stats, variant)
