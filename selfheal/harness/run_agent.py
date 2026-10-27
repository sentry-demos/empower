"""Run headless Claude Code for one self-heal step and keep score.

Streams each step to stdout (so the audience can watch the Actions log), then writes
stats.json and sends one AI agent span, with a child span per tool call, to the
selfheal-harness Sentry project for the scorecard (Agent Tracing).

Usage:
    python selfheal/harness/run_agent.py --name fix-with-seer --prompt-file p.md \
        --out out/ --mcp-config mcp.json --allowed-tools "Read Edit ..." [--disallowed-tools ...]
"""
import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import sentry_sdk

MAX_PREVIEW = 300


def preview(value):
    text = value if isinstance(value, str) else json.dumps(value)
    text = " ".join(text.split())
    return text if len(text) <= MAX_PREVIEW else text[:MAX_PREVIEW] + "…"


def tool_result_text(content):
    if isinstance(content, list):
        return " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return str(content)


def now():
    return datetime.now(timezone.utc)


def run(args):
    cmd = [
        "claude", "-p", open(args.prompt_file).read(),
        "--output-format", "stream-json", "--verbose",
        "--model", args.model,
        "--max-turns", str(args.max_turns),
        "--permission-mode", "dontAsk",
        "--allowedTools", args.allowed_tools,
    ]
    if args.mcp_config:
        cmd += ["--mcp-config", args.mcp_config, "--strict-mcp-config"]
    if args.disallowed_tools:
        cmd += ["--disallowedTools", args.disallowed_tools]

    started = now()
    tools = {}  # tool_use id -> {name, input, start, end, error, result}
    timeline = []  # tool calls and the agent's notes, in order (for the PR's "how it was found")
    result = {}

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True, bufsize=1)
    for line in proc.stdout:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")

        if kind == "system" and event.get("subtype") == "init":
            servers = event.get("mcp_servers", [])
            listing = ", ".join(f"{s['name']}={s['status']}" for s in servers)
            print(f"▶ [{args.name}] model={event.get('model')} mcp: {listing or 'none'}", flush=True)
            # "pending" is normal for a stdio server that's still starting; only stop on a real failure
            failed = [s["name"] for s in servers if s.get("status") in ("failed", "needs-auth")]
            if args.mcp_config and failed:
                # Without Sentry the agent can only guess; stop before it spends tokens
                print(f"❌ MCP server(s) not connected: {', '.join(failed)}. Stopping.", flush=True)
                proc.kill()
                result = {"subtype": "mcp_failed", "is_error": True}
                break

        elif kind == "assistant":
            for block in event["message"].get("content", []):
                if block.get("type") == "text" and block["text"].strip():
                    print(f"💬 {block['text'].strip()}", flush=True)
                    timeline.append({"type": "note", "text": block["text"].strip()})
                elif block.get("type") == "tool_use":
                    tools[block["id"]] = {"name": block["name"], "input": block.get("input", {}),
                                          "start": now(), "end": None, "error": False, "result": ""}
                    timeline.append({"type": "tool", "call": tools[block["id"]]})
                    print(f"🔧 {block['name']} {preview(block.get('input', {}))}", flush=True)

        elif kind == "user":
            for block in event["message"].get("content", []):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    call = tools.get(block.get("tool_use_id"))
                    if call:
                        call["end"] = now()
                        call["error"] = bool(block.get("is_error"))
                        call["result"] = tool_result_text(block.get("content", ""))[:2000]
                    mark = "❌" if block.get("is_error") else "  ↳"
                    print(f"{mark} {preview(tool_result_text(block.get('content', '')))}", flush=True)

        elif kind == "result":
            result = event

    proc.wait()
    ended = now()

    usage = result.get("usage", {})
    input_tokens = (usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
                    + usage.get("cache_creation_input_tokens", 0))
    stats = {
        "name": args.name,
        "model": args.model,
        "ok": proc.returncode == 0 and result.get("subtype") == "success" and not result.get("is_error"),
        "stop_reason": result.get("subtype", "no_result"),
        "duration_s": round((ended - started).total_seconds(), 1),
        "turns": result.get("num_turns", 0),
        "input_tokens": input_tokens,
        "output_tokens": usage.get("output_tokens", 0),
        "cost_usd": round(result.get("total_cost_usd", 0.0), 4),
        "tool_calls": len(tools),
        "seer_calls": sum(1 for t in tools.values() if t["name"].endswith("analyze_issue_with_seer")),
    }
    print(f"■ [{args.name}] {json.dumps(stats)}", flush=True)

    send_agent_span(args, stats, tools, started, ended)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    with open(os.path.join(args.out, "timeline.json"), "w") as f:
        json.dump([timeline_entry(entry, started) for entry in timeline], f, indent=2)
    return stats


def timeline_entry(entry, started):
    if entry["type"] == "note":
        return entry
    call = entry["call"]
    return {
        "type": "tool",
        "name": call["name"],
        "input": call["input"],
        "at_s": round((call["start"] - started).total_seconds(), 1),
        "seconds": round(((call["end"] or call["start"]) - call["start"]).total_seconds(), 1),
        "error": call["error"],
        "result": call["result"],
    }


def send_agent_span(args, stats, tools, started, ended):
    dsn = os.environ.get("SELFHEAL_HARNESS_DSN")
    if not dsn:
        print("SELFHEAL_HARNESS_DSN not set, skipping scorecard span", flush=True)
        return
    sentry_sdk.init(dsn=dsn, traces_sample_rate=1.0, environment="selfheal",
                    release=os.environ.get("GITHUB_SHA"))
    sentry_sdk.set_tag("selfheal.variant", args.variant or args.name)
    sentry_sdk.set_tag("github.run_id", os.environ.get("GITHUB_RUN_ID", "local"))

    txn = sentry_sdk.start_transaction(op="gen_ai.invoke_agent", name=f"invoke_agent {args.name}",
                                       start_timestamp=started)
    txn.set_data("gen_ai.operation.name", "invoke_agent")
    txn.set_data("gen_ai.agent.name", args.name)
    txn.set_data("gen_ai.system", "anthropic")
    txn.set_data("gen_ai.request.model", args.model)
    txn.set_data("gen_ai.usage.input_tokens", stats["input_tokens"])
    txn.set_data("gen_ai.usage.output_tokens", stats["output_tokens"])
    txn.set_data("gen_ai.usage.total_tokens", stats["input_tokens"] + stats["output_tokens"])
    for key in ("turns", "cost_usd", "duration_s", "tool_calls", "seer_calls", "ok"):
        txn.set_data(f"selfheal.{key}", stats[key])

    for call in tools.values():
        span = txn.start_child(op="gen_ai.execute_tool", name=f"execute_tool {call['name']}",
                               start_timestamp=call["start"])
        span.set_data("gen_ai.tool.name", call["name"])
        span.set_data("gen_ai.tool.input", preview(call["input"]))
        if call["error"]:
            span.set_status("internal_error")
        span.finish(end_timestamp=call["end"] or ended)
    txn.set_status("ok" if stats["ok"] else "internal_error")
    txn.finish(end_timestamp=ended)
    sentry_sdk.flush(timeout=10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--variant", default="")
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--model", default=os.environ.get("SELFHEAL_MODEL") or "claude-opus-5-5")
    parser.add_argument("--max-turns", type=int, default=int(os.environ.get("SELFHEAL_MAX_TURNS") or "40"))
    parser.add_argument("--mcp-config", default="")
    parser.add_argument("--allowed-tools", required=True)
    parser.add_argument("--disallowed-tools", default="")
    stats = run(parser.parse_args())
    sys.exit(0 if stats["ok"] else 1)
