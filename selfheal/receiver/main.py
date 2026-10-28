"""Sentry alert webhook -> GitHub Actions self-heal run.

Sentry's internal integration ("Alert Rule Action" on) POSTs here when an alert
fires. We verify the signature, act only on the move to critical (metric alert) or
a triggered issue alert, skip repeats, then create a selfheal/run/<id> branch: one
commit on top of selfheal/base adding .selfheal/alert.json. The push starts the runner
workflow from that branch (no repository_dispatch, so nothing has to live on master),
and the runner runs the version the alert names (see variant_for), or both side by side.

Picking a version: an issue alert's event tag se=selfheal-with-seer / se=selfheal-without-seer,
or "with-seer" / "without-seer" in the alert rule's name. The two versions are independent: a
with-Seer run in flight doesn't hold back a without-Seer alert, and the other way round.

Repeats are detected statelessly from GitHub itself: if a run branch exists or a runner is
queued or running, the alert is acknowledged and dropped. Open agent PRs don't count (they're
left open for demos) unless SKIP_WHILE_AGENT_PR_OPEN=true.
"""
import hashlib
import hmac
import json
import logging
import os
import time

import requests
from flask import Flask, jsonify, request

GITHUB_API = "https://api.github.com"

# strip(): secrets pasted into `gcloud secrets create --data-file=-` often keep a trailing newline
SENTRY_CLIENT_SECRET = os.environ.get("SENTRY_CLIENT_SECRET", "").strip()
# GitHub auth: a GitHub App (org-owned; preferred) or, as a fallback, a token
GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID", "").strip()
GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY", "").strip()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.environ.get("GITHUB_REPO", "sentry-demos/empower")
RUNNER_WORKFLOW = os.environ.get("RUNNER_WORKFLOW", "selfheal-runner.yml")
BASE_BRANCH = os.environ.get("BASE_BRANCH", "selfheal/base")
AGENT_PR_LABEL = os.environ.get("AGENT_PR_LABEL", "selfheal-agent")
RUN_BRANCH_PREFIX = "selfheal/run/"
VARIANTS = ("without-seer", "with-seer")
SKIP_WHILE_AGENT_PR_OPEN = os.environ.get("SKIP_WHILE_AGENT_PR_OPEN", "false").lower() == "true"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("selfheal-receiver")

app = Flask(__name__)


def valid_signature(body: bytes, signature: str) -> bool:
    if not SENTRY_CLIENT_SECRET or not signature:
        return False
    expected = hmac.new(SENTRY_CLIENT_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def variant_for(*texts) -> str:
    """The agent version named in any of the texts (se tag, rule name, title), or "" for the
    runner's default. Same rule as selfheal/harness/plan.py."""
    for text in texts:
        text = str(text or "").lower()
        for variant in VARIANTS:
            if variant in text:
                return variant
    return ""


def event_tag(event: dict, key: str) -> str:
    """A tag's value from an event payload, where tags are [key, value] pairs or dicts."""
    for tag in event.get("tags") or []:
        if isinstance(tag, (list, tuple)) and len(tag) == 2 and tag[0] == key:
            return str(tag[1])
        if isinstance(tag, dict) and tag.get("key") == key:
            return str(tag.get("value", ""))
    return ""


def parse_alert(resource: str, payload: dict):
    """Return the alert to act on, or None if this delivery should be ignored."""
    action = payload.get("action")
    data = payload.get("data") or {}

    if resource == "metric_alert":
        if action != "critical":
            return None
        rule = (data.get("metric_alert") or {}).get("alert_rule") or {}
        title = data.get("description_title") or rule.get("name") or "Metric alert"
        return {
            "kind": "metric_alert",
            "title": title,
            "description": data.get("description_text", ""),
            "url": data.get("web_url", ""),
            "issue_id": "",
            "rule": rule.get("name", ""),
            "se": "",
            "variant": variant_for(rule.get("name"), title),
        }

    if resource == "event_alert":
        if action != "triggered":
            return None
        event = data.get("event") or {}
        se = event_tag(event, "se")
        return {
            "kind": "event_alert",
            "title": event.get("title") or data.get("triggered_rule") or "Issue alert",
            "description": data.get("triggered_rule", ""),
            "url": event.get("web_url", ""),
            "issue_id": str(event.get("issue_id", "")),
            "rule": data.get("triggered_rule", ""),
            "se": se,
            "variant": variant_for(se, data.get("triggered_rule")),
        }

    return None


GITHUB_HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
_app_token = {"value": "", "expires_at": 0.0}


def app_jwt() -> str:
    """Short-lived JWT that authenticates as the GitHub App itself."""
    import jwt  # PyJWT; only needed for app auth

    now = int(time.time())
    # iat in the past allows for clock drift; GitHub caps exp at 10 minutes
    return jwt.encode({"iat": now - 60, "exp": now + 540, "iss": GITHUB_APP_ID},
                      GITHUB_APP_PRIVATE_KEY, algorithm="RS256")


def github_token() -> str:
    """An installation token for the app on GITHUB_REPO, cached until shortly before it expires
    (they last an hour). Falls back to GITHUB_TOKEN when no app is configured."""
    if not (GITHUB_APP_ID and GITHUB_APP_PRIVATE_KEY):
        return GITHUB_TOKEN
    if _app_token["value"] and time.time() < _app_token["expires_at"] - 300:
        return _app_token["value"]

    headers = {**GITHUB_HEADERS, "Authorization": f"Bearer {app_jwt()}"}
    installation = requests.get(f"{GITHUB_API}/repos/{GITHUB_REPO}/installation", headers=headers, timeout=15)
    installation.raise_for_status()
    created = requests.post(f"{GITHUB_API}/app/installations/{installation.json()['id']}/access_tokens",
                            headers=headers, timeout=15)
    created.raise_for_status()
    _app_token["value"] = created.json()["token"]
    _app_token["expires_at"] = time.time() + 3600
    return _app_token["value"]


def github(method, path, **kwargs):
    headers = {**GITHUB_HEADERS, "Authorization": f"Bearer {github_token()}"}
    response = requests.request(method, f"{GITHUB_API}{path}", headers=headers, timeout=15, **kwargs)
    response.raise_for_status()
    return response


def branch_variant(branch: str) -> str:
    """The version a run branch is for: selfheal/run/<variant>/<id>, or "" (both) for
    selfheal/run/<id>."""
    rest = branch.removeprefix("refs/heads/").removeprefix(RUN_BRANCH_PREFIX)
    first = rest.split("/", 1)[0]
    return first if first in VARIANTS and "/" in rest else ""


def overlaps(variant: str, other: str) -> bool:
    """Whether a run for `other` is a repeat for `variant`. A run with no version runs both."""
    return not variant or not other or variant == other


def already_handling(variant: str = "") -> str:
    """Why a new run for this version would be a repeat, or "" if none is in flight."""
    # The runner deletes its run branch when it finishes, so one existing means a run is pending
    refs = github("GET", f"/repos/{GITHUB_REPO}/git/matching-refs/heads/{RUN_BRANCH_PREFIX}").json()
    for ref in refs:
        if overlaps(variant, branch_variant(ref["ref"])):
            return f"run branch {ref['ref'].removeprefix('refs/heads/')} exists"

    for status in ("queued", "in_progress"):
        runs = github("GET", f"/repos/{GITHUB_REPO}/actions/workflows/{RUNNER_WORKFLOW}/runs",
                      params={"status": status, "per_page": 20}).json()
        for run in runs.get("workflow_runs") or []:
            if overlaps(variant, branch_variant(run.get("head_branch", ""))):
                return f"runner already {status} ({run.get('head_branch')})"

    # Agent PRs are left open for demos, so they don't block new runs unless asked to
    if SKIP_WHILE_AGENT_PR_OPEN:
        pulls = github("GET", f"/repos/{GITHUB_REPO}/pulls",
                       params={"state": "open", "base": BASE_BRANCH, "per_page": 100}).json()
        for pr in pulls:
            labels = {label["name"] for label in pr.get("labels", [])}
            if AGENT_PR_LABEL in labels and (not variant or f"selfheal:{variant}" in labels):
                return f"agent PR #{pr['number']} is still open"
    return ""


def create_run_branch(alert: dict) -> str:
    """Commit .selfheal/alert.json on top of the base branch as a new run branch.
    Building the commit before the ref means the branch appears with one push event."""
    repo = f"/repos/{GITHUB_REPO}/git"
    base_sha = github("GET", f"{repo}/ref/heads/{BASE_BRANCH}").json()["object"]["sha"]
    base_tree = github("GET", f"{repo}/commits/{base_sha}").json()["tree"]["sha"]
    tree = github("POST", f"{repo}/trees", json={
        "base_tree": base_tree,
        "tree": [{"path": ".selfheal/alert.json", "mode": "100644", "type": "blob",
                  "content": json.dumps(alert, indent=2) + "\n"}],
    }).json()["sha"]
    commit = github("POST", f"{repo}/commits", json={
        "message": f"Self-heal run: {alert['title']}", "tree": tree, "parents": [base_sha],
    }).json()["sha"]
    # The version goes in the branch name, so repeats can be checked per version
    version = f"{alert['variant']}/" if alert.get("variant") in VARIANTS else ""
    branch = f"{RUN_BRANCH_PREFIX}{version}{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    github("POST", f"{repo}/refs", json={"ref": f"refs/heads/{branch}", "sha": commit})
    return branch


@app.post("/sentry")
def sentry_webhook():
    body = request.get_data()
    if not valid_signature(body, request.headers.get("Sentry-Hook-Signature", "")):
        log.warning("rejected delivery with bad signature")
        return jsonify(error="invalid signature"), 401

    resource = request.headers.get("Sentry-Hook-Resource", "")
    payload = json.loads(body or b"{}")
    alert = parse_alert(resource, payload)
    if alert is None:
        # Shape only (no values), so an unexpected payload format can be recognized from the logs
        log.info("ignored %s delivery: action=%s data keys=%s", resource or "unknown",
                 payload.get("action"), sorted((payload.get("data") or {}).keys()))
        return jsonify(status="ignored"), 200

    reason = already_handling(alert.get("variant", ""))
    if reason:
        log.info("skipped repeat alert '%s': %s", alert["title"], reason)
        return jsonify(status="skipped", reason=reason), 200

    branch = create_run_branch(alert)
    log.info("created %s for '%s' (version: %s)", branch, alert["title"], alert.get("variant") or "default")
    return jsonify(status="dispatched", branch=branch, alert=alert), 202


@app.get("/healthz")
def healthz():
    return "ok"
