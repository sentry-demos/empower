"""With-Seer runs: get Seer's root cause before the coding agent starts, and hand it over.

The with-Seer agent doesn't explore Sentry itself. This script does the Sentry work up front,
over the plain Sentry API (the same endpoints the Sentry MCP server calls):

  1. The issue behind the alert: the one the alert names, or else the unresolved error issue
     with the most events in the last hour in SENTRY_PROJECT / SENTRY_ENVIRONMENT.
  2. Seer's root cause analysis for it. If Seer has already analyzed the issue (Seer's automatic
     runs on the project), that analysis is used as is; otherwise a run is started and polled
     until the root cause is in.
  3. The most recent failing cart from Sentry Logs, for the replay, and the impact numbers.

Writes OUT/handoff.json (everything above, plus each call for the PR's "How this fix was
found"), OUT/handoff.md (the part of the prompt the agent reads) and OUT/cart.json. Exits 1
if there's no root cause to hand over, so the agent never starts without one.

Usage:
    python selfheal/harness/seer_handoff.py --alert alert.json --out DIR
Needs SENTRY_MCP_TOKEN (read issues, events and logs; start Seer), SENTRY_ORG, SENTRY_PROJECT
and SENTRY_ENVIRONMENT. SENTRY_API_URL defaults to https://sentry.io/api/0.
"""
import argparse
import ast
import json
import os
import re
import sys
import time

import requests

API = os.environ.get("SENTRY_API_URL", "https://sentry.io/api/0").rstrip("/")
ORG = os.environ.get("SENTRY_ORG") or "demo"
PROJECT = os.environ.get("SENTRY_PROJECT") or "selfheal-flask"
ENVIRONMENT = os.environ.get("SENTRY_ENVIRONMENT") or "selfheal"
LOG_MESSAGE = "Failed to validate inventory"

SEER_TIMEOUT_S = int(os.environ.get("SELFHEAL_SEER_TIMEOUT_S") or 480)
SEER_POLL_S = 5
SEER_TERMINAL = ("completed", "error", "awaiting_user_input")

def sentry_token(org):
    """The org's Sentry token: SENTRY_MCP_TOKEN_TEAM_SE for team-se, else SENTRY_MCP_TOKEN."""
    return (os.environ.get("SENTRY_MCP_TOKEN_" + org.upper().replace("-", "_"))
            or os.environ["SENTRY_MCP_TOKEN"])


STARTED = time.time()
CALLS = []  # each Sentry call, for the PR's "How this fix was found"


def notice(title, message, level="notice"):
    """A GitHub Actions annotation: shows on the run page and through the checks API."""
    message = " ".join(str(message).split()).replace("%", "%25")
    print(f"::{level} title={title}::{message[:900]}", flush=True)


def sentry(method, path, layer, label, **kwargs):
    """One Sentry API call, recorded for the PR. Returns the JSON body."""
    at = time.time()
    response = requests.request(method, f"{API}{path}", timeout=30,
                                headers={"Authorization": f"Bearer {sentry_token(ORG)}"},
                                **kwargs)
    entry = {"layer": layer, "call": label, "at_s": round(at - STARTED, 1),
             "seconds": round(time.time() - at, 1), "status": response.status_code}
    CALLS.append(entry)
    if response.status_code >= 400:
        entry["returned"] = f"HTTP {response.status_code}: {response.text[:200]}"
        response.raise_for_status()
    return response.json()


# --- 1. The issue ---------------------------------------------------------------------------

def find_issue(alert):
    issue_id = str(alert.get("issue_id") or "").strip()
    if not issue_id:
        # Metric alerts don't name an issue: take the error issue firing hardest right now
        issues = sentry("GET", f"/organizations/{ORG}/issues/", "sentry", "Issue behind the alert", params={
            "query": f"is:unresolved issue.category:error project:{PROJECT}",
            "environment": ENVIRONMENT, "statsPeriod": "1h", "sort": "freq", "limit": 5,
        })
        if not issues:
            raise SystemExit(fail(f"No unresolved error issue in {PROJECT} / {ENVIRONMENT} in the last hour"))
        issue_id = issues[0]["id"]
        CALLS[-1]["returned"] = f"{issues[0]['shortId']}: {issues[0]['title']} (top of {len(issues)})"

    issue = sentry("GET", f"/organizations/{ORG}/issues/{issue_id}/", "sentry", "Issue details")
    CALLS[-1]["returned"] = (f"{issue['shortId']}: {issue.get('count')} events, {issue.get('userCount')} users,"
                             f" first seen {issue.get('firstSeen')}")
    return issue


# --- 2. Seer's root cause -------------------------------------------------------------------

def artifacts(autofix):
    """Latest data per artifact key across the run's blocks (as the Sentry MCP reads them)."""
    found = {}
    for block in autofix.get("blocks") or []:
        for artifact in block.get("artifacts") or []:
            if artifact.get("data"):
                found[artifact["key"]] = artifact["data"]
    return found


def root_cause_text(state):
    """Seer's root cause as markdown, or "" if it isn't in yet."""
    autofix = state.get("autofix") or {}
    found = artifacts(autofix)
    cause = found.get("root_cause") or {}
    if not cause and autofix.get("status") not in SEER_TERMINAL:
        return ""
    sections = []
    if cause.get("one_line_description"):
        sections.append(cause["one_line_description"])
    if cause.get("five_whys"):
        sections.append("\n".join(f"{i}. {why}" for i, why in enumerate(cause["five_whys"], 1)))
    if cause.get("reproduction_steps"):
        sections.append("\n".join(f"- {step}" for step in cause["reproduction_steps"]))
    solution = found.get("solution") or {}
    if solution.get("one_line_summary"):
        sections.append("**Seer's suggested fix:** " + solution["one_line_summary"])
        sections += [f"- **{s.get('title', '')}**: {s.get('description', '')}" for s in solution.get("steps") or []]
    if sections:
        return "\n\n".join(sections)
    # Older run formats: Seer's own markdown rendering of the run
    return ((state.get("formatted") or {}).get("content") or "").strip()


def seer_root_cause(issue):
    path = f"/organizations/{ORG}/issues/{issue['id']}/autofix/"
    state = sentry("GET", path, "seer", "Seer analysis", params={"llmFormat": "markdown"})
    autofix = state.get("autofix")
    reused = bool(autofix)
    if autofix:
        CALLS[-1]["returned"] = f"existing analysis, run {autofix.get('run_id')} ({autofix.get('status')})"
    else:
        CALLS[-1]["returned"] = "no analysis yet"
        started = sentry("POST", path, "seer", "Start Seer analysis", json={"instruction": ""})
        CALLS[-1]["returned"] = f"started run {started.get('run_id')}"

    deadline = time.time() + SEER_TIMEOUT_S
    polls = 0
    text = root_cause_text(state)
    while not text and time.time() < deadline:
        time.sleep(SEER_POLL_S)
        state = requests.get(f"{API}{path}", params={"llmFormat": "markdown"}, timeout=30,
                             headers={"Authorization": f"Bearer {sentry_token(ORG)}"}).json()
        polls += 1
        text = root_cause_text(state)
    autofix = state.get("autofix") or {}
    if polls:
        CALLS.append({"layer": "seer", "call": "Wait for Seer's root cause", "at_s": round(time.time() - STARTED, 1),
                      "seconds": polls * SEER_POLL_S, "status": 200,
                      "returned": f"{autofix.get('status')} after {polls} checks"})
    if not text:
        raise SystemExit(fail(f"Seer gave no root cause for {issue['shortId']} within {SEER_TIMEOUT_S}s"
                              f" (status {autofix.get('status')})"))
    return {"run_id": autofix.get("run_id"), "status": autofix.get("status"), "reused": reused,
            "root_cause": text, "seconds": round(sum(c["seconds"] for c in CALLS if c["layer"] == "seer"), 1)}


# --- 3. The failing cart and the impact -----------------------------------------------------

def parse_cart(row):
    """(cart text as logged, total) from a log row: the cart_json attribute, or the Python dict
    in the message (production). The text is kept unchanged; replay.py takes either form."""
    raw = row.get("cart_json")
    if raw:
        try:
            return raw, json.loads(raw).get("total")
        except (ValueError, AttributeError):
            pass
    match = re.search(r"\{.*\}", row.get("message") or "")
    if not match:
        return None, None
    try:
        return match.group(0), ast.literal_eval(match.group(0)).get("total")
    except (ValueError, SyntaxError, AttributeError):
        return match.group(0), None


def failing_carts(issue, out):
    params = {"dataset": "logs", "project": issue["project"]["id"], "environment": ENVIRONMENT,
              "query": f'"{LOG_MESSAGE}"', "field": ["timestamp", "message", "cart_json"],
              "sort": "-timestamp", "per_page": 100, "statsPeriod": "24h", "referrer": "selfheal.handoff"}
    try:
        rows = sentry("GET", f"/organizations/{ORG}/events/", "sentry", "Failing carts (Logs)", params=params)
    except requests.HTTPError:
        # Production logs have no cart_json attribute; ask again without it
        params["field"] = ["timestamp", "message"]
        rows = sentry("GET", f"/organizations/{ORG}/events/", "sentry", "Failing carts (Logs)", params=params)
    rows = rows.get("data") or []
    carts = [(row, *parse_cart(row)) for row in rows]
    carts = [c for c in carts if c[1]]
    CALLS[-1]["returned"] = f"{len(rows)} log lines, {len(carts)} with a cart"
    if not carts:
        return {"saved": False, "window": None, "lost_revenue_usd": None, "log_lines": len(rows)}

    with open(os.path.join(out, "cart.json"), "w") as f:
        f.write(carts[0][1] + "\n")  # newest first
    totals = [c[2] for c in carts if isinstance(c[2], (int, float))]
    return {"saved": True, "log_lines": len(rows), "carts": len(carts),
            "lost_revenue_usd": sum(totals) if totals else None,
            "window": [carts[-1][0].get("timestamp"), carts[0][0].get("timestamp")],
            "latest": carts[0][0].get("timestamp")}


# --- Output ---------------------------------------------------------------------------------

def handoff_md(issue, seer, logs, out):
    impact = {
        "failed_checkouts": int(issue["count"]) if str(issue.get("count", "")).isdigit() else None,
        "users_affected": issue.get("userCount"),
        "first_seen": issue.get("firstSeen"),
        "lost_revenue_usd": logs["lost_revenue_usd"],
    }
    window = logs.get("window")
    report = {"issue_short_id": issue["shortId"], "issue_url": issue.get("permalink", ""), "impact": impact}
    cart_line = (f"The most recent failing request (logged {logs['latest']}) is saved at `{out}/cart.json`."
                 if logs["saved"] else
                 "No failing request was found in Sentry Logs in the last 24 hours, so there's no cart to "
                 "replay. Skip the replay and say so in your report.")
    revenue_note = (f"`lost_revenue_usd` is the sum of `total` across {logs['carts']} failed carts logged"
                    f" between {window[0]} and {window[1]} UTC." if logs.get("window") else
                    "`lost_revenue_usd` is unknown (no carts in Sentry Logs).")
    return impact, "\n".join([
        f"**Issue:** [{issue['shortId']}]({issue.get('permalink', '')}) — {issue.get('title', '')}",
        f"**Seer run:** {seer['run_id']} ({seer['status']}"
        + (", Seer's earlier automatic analysis" if seer["reused"] else ", started for this alert") + ")",
        "",
        "<seer_root_cause>",
        seer["root_cause"],
        "</seer_root_cause>",
        "",
        cart_line,
        "",
        "Copy these into `result.json` unchanged:",
        "",
        "```json",
        json.dumps(report, indent=2),
        "```",
        "",
        revenue_note,
    ])


def fail(message):
    notice("Seer handoff failed", message, level="error")
    return 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--alert", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)
    with open(args.alert) as f:
        alert = json.load(f)

    try:
        issue = find_issue(alert)
        seer = seer_root_cause(issue)
        logs = failing_carts(issue, out)
    except requests.RequestException as err:
        last = CALLS[-1] if CALLS else {}
        return fail(f"{last.get('call', 'Sentry call')}: {err}")

    impact, markdown = handoff_md(issue, seer, logs, out)
    handoff = {"issue": {"id": issue["id"], "short_id": issue["shortId"], "url": issue.get("permalink"),
                         "title": issue.get("title")},
               "seer": seer, "logs": logs, "impact": impact, "calls": CALLS,
               "seconds": round(time.time() - STARTED, 1)}
    with open(os.path.join(out, "handoff.json"), "w") as f:
        json.dump(handoff, f, indent=2)
    with open(os.path.join(out, "handoff.md"), "w") as f:
        f.write(markdown + "\n")

    print(markdown, flush=True)
    first_line = seer["root_cause"].splitlines()[0]
    notice("Seer handoff", f"{issue['shortId']} · Seer run {seer['run_id']} ({seer['status']},"
           f" {'reused' if seer['reused'] else 'new'}) · {handoff['seconds']}s · cart"
           f" {'saved' if logs['saved'] else 'not found'} · root cause: {first_line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
