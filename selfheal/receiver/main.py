"""Sentry alert webhook -> GitHub Actions self-heal run.

Sentry's internal integration ("Alert Rule Action" on) POSTs here when an alert
fires. We verify the signature, act only on the move to critical (metric alert) or
a triggered issue alert, skip repeats, then fire a repository_dispatch so the
runner workflow starts both versions (with / without Seer) on the same alert.

Repeats are detected statelessly from GitHub itself: if a runner is already queued
or running, or an agent PR is still open, the alert is acknowledged and dropped.
"""
import hashlib
import hmac
import json
import logging
import os

import requests
from flask import Flask, jsonify, request

GITHUB_API = "https://api.github.com"

SENTRY_CLIENT_SECRET = os.environ.get("SENTRY_CLIENT_SECRET", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "sentry-demos/empower")
RUNNER_WORKFLOW = os.environ.get("RUNNER_WORKFLOW", "selfheal-runner.yml")
BASE_BRANCH = os.environ.get("BASE_BRANCH", "selfheal/base")
AGENT_PR_LABEL = os.environ.get("AGENT_PR_LABEL", "selfheal-agent")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("selfheal-receiver")

app = Flask(__name__)


def valid_signature(body: bytes, signature: str) -> bool:
    if not SENTRY_CLIENT_SECRET or not signature:
        return False
    expected = hmac.new(SENTRY_CLIENT_SECRET.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


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
        }

    return None


def github(method, path, **kwargs):
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    response = requests.request(method, f"{GITHUB_API}{path}", headers=headers, timeout=15, **kwargs)
    response.raise_for_status()
    return response


def already_handling() -> str:
    """Why a new run would be a repeat, or "" if none is in flight."""
    for status in ("queued", "in_progress"):
        runs = github("GET", f"/repos/{GITHUB_REPO}/actions/workflows/{RUNNER_WORKFLOW}/runs",
                      params={"status": status, "per_page": 1}).json()
        if runs.get("total_count"):
            return f"runner already {status}"

    pulls = github("GET", f"/repos/{GITHUB_REPO}/pulls",
                   params={"state": "open", "base": BASE_BRANCH, "per_page": 100}).json()
    for pr in pulls:
        if any(label["name"] == AGENT_PR_LABEL for label in pr.get("labels", [])):
            return f"agent PR #{pr['number']} is still open"
    return ""


@app.post("/sentry")
def sentry_webhook():
    body = request.get_data()
    if not valid_signature(body, request.headers.get("Sentry-Hook-Signature", "")):
        log.warning("rejected delivery with bad signature")
        return jsonify(error="invalid signature"), 401

    resource = request.headers.get("Sentry-Hook-Resource", "")
    alert = parse_alert(resource, json.loads(body or b"{}"))
    if alert is None:
        log.info("ignored %s delivery", resource or "unknown")
        return jsonify(status="ignored"), 200

    reason = already_handling()
    if reason:
        log.info("skipped repeat alert '%s': %s", alert["title"], reason)
        return jsonify(status="skipped", reason=reason), 200

    github("POST", f"/repos/{GITHUB_REPO}/dispatches",
           json={"event_type": "selfheal-alert", "client_payload": alert})
    log.info("dispatched runner for '%s'", alert["title"])
    return jsonify(status="dispatched", alert=alert), 202


@app.get("/healthz")
def healthz():
    return "ok"
