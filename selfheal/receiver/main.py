"""Sentry alert webhook -> GitHub Actions self-heal run.

Sentry's internal integration ("Alert Rule Action" on) POSTs here when an alert
fires. Several Sentry orgs can point their integration at this one receiver: each org's
client secret is configured (SENTRY_CLIENT_SECRET for the default org, and
SENTRY_CLIENT_SECRET_<ORG> for others, e.g. SENTRY_CLIENT_SECRET_TEAM_SE), and the secret
that verifies a delivery tells us which org sent it.

We act only on the move to critical (metric alert) or a triggered issue alert, skip
repeats, pick the alert's target from targets.json (by org and project), then create a
selfheal/run/<id> branch: one commit on top of that target's base branch adding
.selfheal/alert.json. The push starts the runner workflow from that branch (no
repository_dispatch, so nothing has to live on master).

Repeats are detected statelessly from GitHub itself: if a run branch exists or a runner is
queued or running, the alert is acknowledged and dropped. Open agent PRs don't count (they're
left open for demos) unless SKIP_WHILE_AGENT_PR_OPEN=true.
"""
import hashlib
import hmac
import json
import logging
import os
import re
import time

import requests
from flask import Flask, jsonify, request

GITHUB_API = "https://api.github.com"

DEFAULT_ORG = os.environ.get("DEFAULT_SENTRY_ORG", "demo")
# strip(): secrets pasted into `gcloud secrets create --data-file=-` often keep a trailing newline
SENTRY_CLIENT_SECRET = os.environ.get("SENTRY_CLIENT_SECRET", "").strip()


def client_secrets():
    """org slug -> client secret: SENTRY_CLIENT_SECRET is the default org's, and
    SENTRY_CLIENT_SECRET_TEAM_SE is team-se's (suffix lowercased, _ -> -)."""
    secrets = {DEFAULT_ORG: SENTRY_CLIENT_SECRET} if SENTRY_CLIENT_SECRET else {}
    for name, value in os.environ.items():
        if name.startswith("SENTRY_CLIENT_SECRET_") and value.strip():
            secrets[name.removeprefix("SENTRY_CLIENT_SECRET_").lower().replace("_", "-")] = value.strip()
    return secrets


# Bundled next to main.py by deploy.sh (a copy of selfheal/targets.json)
TARGETS_FILE = os.environ.get("TARGETS_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "targets.json"))
# GitHub auth: a GitHub App (org-owned; preferred) or, as a fallback, a token
GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID", "").strip()
GITHUB_APP_PRIVATE_KEY = os.environ.get("GITHUB_APP_PRIVATE_KEY", "").strip()
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.environ.get("GITHUB_REPO", "sentry-demos/empower")
RUNNER_WORKFLOW = os.environ.get("RUNNER_WORKFLOW", "selfheal-runner.yml")
BASE_BRANCH = os.environ.get("BASE_BRANCH", "selfheal/base")
AGENT_PR_LABEL = os.environ.get("AGENT_PR_LABEL", "selfheal-agent")
RUN_BRANCH_PREFIX = "selfheal/run/"
SKIP_WHILE_AGENT_PR_OPEN = os.environ.get("SKIP_WHILE_AGENT_PR_OPEN", "false").lower() == "true"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("selfheal-receiver")

app = Flask(__name__)


def verify_org(body: bytes, signature: str):
    """The org whose client secret signed this delivery, or None if none did."""
    if not signature:
        return None
    for org, secret in client_secrets().items():
        expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
        if hmac.compare_digest(expected, signature):
            return org
    return None


def valid_signature(body: bytes, signature: str) -> bool:
    return verify_org(body, signature) is not None


def load_targets():
    # The deployed copy next to main.py, or selfheal/targets.json when run from the repo
    repo_copy = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "targets.json")
    for path in (TARGETS_FILE, repo_copy):
        try:
            with open(path) as f:
                return {name: t for name, t in json.load(f).items() if not name.startswith("_")}
        except (OSError, json.JSONDecodeError):
            continue
    log.error("no targets.json found; every alert will be ignored")
    return {}


def pick_target(org, project=None):
    """(name, target) for an alert from this org: project match first, then the org's first
    target. (None, None) if the org has no target."""
    targets = load_targets()
    in_org = [name for name, t in targets.items() if t.get("org") == org]
    for name in in_org:
        if project and project in targets[name].get("projects", []):
            return name, targets[name]
    return (in_org[0], targets[in_org[0]]) if in_org else (None, None)


def org_from_url(url: str):
    """Org slug from a Sentry URL: https://sentry.io/organizations/<org>/... or https://<org>.sentry.io/..."""
    match = re.search(r"/organizations/([^/]+)/", url or "") or re.match(r"https://([^./]+)\.sentry\.io/", url or "")
    return match.group(1) if match else None


def parse_alert(resource: str, payload: dict):
    """Return the alert to act on, or None if this delivery should be ignored."""
    action = payload.get("action")
    data = payload.get("data") or {}

    if resource == "metric_alert":
        if action != "critical":
            return None
        rule = (data.get("metric_alert") or {}).get("alert_rule") or {}
        return {
            "kind": "metric_alert",
            "title": data.get("description_title") or rule.get("name") or "Metric alert",
            "description": data.get("description_text", ""),
            "url": data.get("web_url", ""),
            "issue_id": "",
        }

    if resource == "event_alert":
        if action != "triggered":
            return None
        event = data.get("event") or {}
        return {
            "kind": "event_alert",
            "title": event.get("title") or data.get("triggered_rule") or "Issue alert",
            "description": data.get("triggered_rule", ""),
            "url": event.get("web_url", ""),
            "issue_id": str(event.get("issue_id", "")),
            "project_id": str(event.get("project", "")),
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


def already_handling() -> str:
    """Why a new run would be a repeat, or "" if none is in flight."""
    # The runner deletes its run branch when it finishes, so one existing means a run is pending
    refs = github("GET", f"/repos/{GITHUB_REPO}/git/matching-refs/heads/{RUN_BRANCH_PREFIX}").json()
    if refs:
        return f"run branch {refs[0]['ref'].removeprefix('refs/heads/')} exists"

    for status in ("queued", "in_progress"):
        runs = github("GET", f"/repos/{GITHUB_REPO}/actions/workflows/{RUNNER_WORKFLOW}/runs",
                      params={"status": status, "per_page": 1}).json()
        if runs.get("total_count"):
            return f"runner already {status}"

    # Agent PRs are left open for demos, so they don't block new runs unless asked to
    if SKIP_WHILE_AGENT_PR_OPEN:
        pulls = github("GET", f"/repos/{GITHUB_REPO}/pulls",
                       params={"state": "open", "base": BASE_BRANCH, "per_page": 100}).json()
        for pr in pulls:
            if any(label["name"] == AGENT_PR_LABEL for label in pr.get("labels", [])):
                return f"agent PR #{pr['number']} is still open"
    return ""


def create_run_branch(alert: dict, base: str = BASE_BRANCH) -> str:
    """Commit .selfheal/alert.json on top of the target's base branch as a new run branch.
    Building the commit before the ref means the branch appears with one push event."""
    repo = f"/repos/{GITHUB_REPO}/git"
    base_sha = github("GET", f"{repo}/ref/heads/{base}").json()["object"]["sha"]
    base_tree = github("GET", f"{repo}/commits/{base_sha}").json()["tree"]["sha"]
    tree = github("POST", f"{repo}/trees", json={
        "base_tree": base_tree,
        "tree": [{"path": ".selfheal/alert.json", "mode": "100644", "type": "blob",
                  "content": json.dumps(alert, indent=2) + "\n"}],
    }).json()["sha"]
    commit = github("POST", f"{repo}/commits", json={
        "message": f"Self-heal run: {alert['title']}", "tree": tree, "parents": [base_sha],
    }).json()["sha"]
    branch = f"{RUN_BRANCH_PREFIX}{time.strftime('%Y%m%d-%H%M%S', time.gmtime())}"
    github("POST", f"{repo}/refs", json={"ref": f"refs/heads/{branch}", "sha": commit})
    return branch


@app.post("/sentry")
def sentry_webhook():
    body = request.get_data()
    org = verify_org(body, request.headers.get("Sentry-Hook-Signature", ""))
    if org is None:
        log.warning("rejected delivery with bad signature (no configured org's client secret matches)")
        return jsonify(error="invalid signature"), 401

    resource = request.headers.get("Sentry-Hook-Resource", "")
    payload = json.loads(body or b"{}")
    alert = parse_alert(resource, payload)
    if alert is None:
        # Shape only (no values), so an unexpected payload format can be recognized from the logs
        log.info("ignored %s delivery from %s: action=%s data keys=%s", resource or "unknown", org,
                 payload.get("action"), sorted((payload.get("data") or {}).keys()))
        return jsonify(status="ignored"), 200

    url_org = org_from_url(alert.get("url"))
    if url_org and url_org != org:
        log.warning("delivery signed by %s links to org %s; using %s", org, url_org, org)
    target_name, target = pick_target(org, alert.get("project_slug"))
    if not target:
        log.info("ignored alert '%s' from %s: no target for this org in targets.json", alert["title"], org)
        return jsonify(status="ignored", reason=f"no target for org {org}"), 200
    alert.update(org=org, target=target_name)

    reason = already_handling()
    if reason:
        log.info("skipped repeat alert '%s': %s", alert["title"], reason)
        return jsonify(status="skipped", reason=reason), 200

    branch = create_run_branch(alert, target["base"])
    log.info("created %s on %s for '%s' (%s, target %s)", branch, target["base"], alert["title"], org, target_name)
    return jsonify(status="dispatched", branch=branch, alert=alert), 202


@app.get("/healthz")
def healthz():
    return "ok"
