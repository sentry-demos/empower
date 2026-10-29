"""Verification for the context-snowball target: is search_policies' output small now?

Calls the real search_policies tool (no LLM, no network) for a few customer questions and
counts the tokens it returns, the way they'd land in the next gen_ai.chat call. Passes when
every answer is under the budget and the return-policy question still gets its answer
("30 days"), so returning nothing doesn't count as a fix.

Usage (from the repo root): python selfheal/harness/checks/policy_tokens.py [--budget 4000]
Exits 0 when it passes. Prints a JSON summary either way.
"""
import argparse
import asyncio
import json
import os
import sys

AGENT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "agent")
QUESTIONS = ["return policy", "What is your return policy?", "shipping to Canada"]
# The alert fires above 20,000 input tokens; a normal turn is ~0.5-2k
DEFAULT_BUDGET = 4000

# The agent app reads these at import; test values are enough, nothing calls out
for name, value in {"OPENROUTER_API_KEY": "selfheal-check", "API_HOST": "127.0.0.1",
                    "PORT": "8093", "API_RELOAD": "false", "MAX_TOKENS": "1000",
                    "AGENT_SENTRY_ENVIRONMENT": "selfheal-check"}.items():
    os.environ.setdefault(name, value)


def count_tokens(text):
    import tiktoken
    return len(tiktoken.get_encoding("o200k_base").encode(text))


async def measure():
    sys.path.insert(0, os.path.abspath(AGENT_DIR))
    from agents import RunContextWrapper
    from app.session import ChatSession
    from app.tools.shop import search_policies

    results = []
    for question in QUESTIONS:
        context = RunContextWrapper(ChatSession(f"selfheal-check-{len(results)}"))
        output = await search_policies.on_invoke_tool(context, json.dumps({"query": question}))
        results.append({"question": question, "tokens": count_tokens(str(output)),
                        "bytes": len(str(output)), "has_return_answer": "30 days" in str(output)})
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--budget", type=int, default=int(os.environ.get("POLICY_TOKEN_BUDGET") or DEFAULT_BUDGET))
    args = parser.parse_args()

    results = asyncio.run(measure())
    over = [r for r in results if r["tokens"] > args.budget]
    answered = next(r for r in results if r["question"] == "return policy")["has_return_answer"]
    ok = not over and answered
    print(json.dumps({"ok": ok, "budget": args.budget, "results": results}))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
