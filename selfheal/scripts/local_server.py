"""Run flask-selfheal on your machine, reporting to a real Sentry project, with no shared infra.

The database, Redis and Statsig are stubbed (inventory always has stock), so nothing touches
the shared GCP project. Errors, logs (with cart_json), traces and the revenue metric go to the
DSN you pass, tagged environment=selfheal and release=flask-selfheal@<current commit>.

    FLASK_DSN=<flask-selfheal DSN> python selfheal/scripts/local_server.py [--port 8080]
    SELFHEAL_FLASK_URL=http://localhost:8080 python selfheal/scripts/drive.py live

Restart it after pulling a merged fix: that's the local stand-in for selfheal-deploy.
"""
import argparse
import json
import os
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

FLASK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "flask")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    if not os.environ.get("FLASK_DSN"):
        sys.exit("Set FLASK_DSN to your flask-selfheal project's DSN")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=FLASK_DIR).stdout.strip()
    os.environ["FLASK_RELEASE"] = f"flask-selfheal@{sha}"
    os.environ["FLASK_ENVIRONMENT"] = "selfheal"
    # db.py builds a Cloud SQL engine outside "local"; it's lazy and never connects here
    os.environ.setdefault("DB_CLOUD_SQL_CONNECTION_NAME", "local:stub:stub")

    sys.path.insert(0, os.path.abspath(FLASK_DIR))
    from src.test import conftest  # noqa: F401  (stub env vars, Statsig; imports the app)
    from src import main as flask_main

    def get_inventory(cart):
        return [SimpleNamespace(id=int(pid), productid=int(pid), count=1000)
                for pid in cart["quantities"]]

    patches = [
        patch.object(flask_main, "get_inventory", side_effect=get_inventory),
        patch.object(flask_main, "decrement_inventory"),
        patch.object(flask_main, "evaluate_statsig_flags"),
    ]
    for p in patches:
        p.start()

    print(json.dumps({"release": os.environ["FLASK_RELEASE"], "environment": "selfheal",
                      "url": f"http://localhost:{args.port}"}), flush=True)
    from werkzeug.serving import run_simple
    run_simple("0.0.0.0", args.port, flask_main.app, threaded=True)


if __name__ == "__main__":
    main()
