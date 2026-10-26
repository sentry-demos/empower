"""Send a steady stream of purchases to flask-selfheal so revenue has a baseline to drop from.

    python selfheal/scripts/drive.py baseline   # healthy revenue (start ~15 min before the demo)
    python selfheal/scripts/drive.py live       # real checkouts: 500 while the bug is deployed

Both modes send the exact request the shopping agent's purchase tool and CheckoutForm.jsx
send. `baseline` sets validate_inventory="false", which skips the broken validation path so
revenue flows; `live` sends "true", like real shoppers. Switching baseline -> live is what
"breaks production" on cue. Keep `live` running after the fix merges: once the release
deploys, the same traffic succeeds, revenue recovers and the alert resolves.

Env: SELFHEAL_FLASK_URL (e.g. https://flask-selfheal-dot-<project>.appspot.com).
"""
import argparse
import json
import os
import random
import sys
import time

import requests

# Fallback catalogue if /products is unavailable. ids match the products table.
CATALOGUE = [
    {"id": 3, "title": "Plant Mood", "price": 155},
    {"id": 4, "title": "Botana Voice", "price": 175},
    {"id": 5, "title": "Plant Stroller", "price": 295},
    {"id": 6, "title": "Plant Nodes", "price": 35},
]


def load_catalogue(base_url):
    try:
        products = requests.get(f"{base_url}/products", timeout=60).json()
        return [{"id": p["id"], "title": p["title"], "price": p["price"]} for p in products] or CATALOGUE
    except (requests.RequestException, ValueError, KeyError, TypeError):
        return CATALOGUE


def random_cart(catalogue):
    items = random.sample(catalogue, k=random.randint(1, min(3, len(catalogue))))
    quantities = {str(item["id"]): random.randint(1, 2) for item in items}
    total = sum(item["price"] * quantities[str(item["id"])] for item in items)
    return {"items": items, "quantities": quantities, "total": total}


def purchase(base_url, cart, validate):
    order = {
        "cart": cart,
        "form": {"email": f"shopper{random.randint(1, 9999)}@example.com"},
        "validate_inventory": "true" if validate else "false",  # string, see agent checkout.py
    }
    headers = {"se": "selfheal", "customerType": random.choice(["small-plan", "medium-plan", "large-plan"])}
    response = requests.post(f"{base_url}/checkout", params={"v2": "true"}, json=order,
                             headers=headers, timeout=30)
    return response.status_code


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["baseline", "live"])
    parser.add_argument("--per-minute", type=float, default=6)
    parser.add_argument("--minutes", type=float, default=0, help="0 = run until Ctrl+C")
    parser.add_argument("--url", default=os.environ.get("SELFHEAL_FLASK_URL"))
    args = parser.parse_args()
    if not args.url:
        sys.exit("Set SELFHEAL_FLASK_URL or pass --url")

    base_url = args.url.rstrip("/")
    catalogue = load_catalogue(base_url)
    deadline = time.time() + args.minutes * 60 if args.minutes else None
    counts = {}

    print(f"Driving {args.mode} purchases at {args.per_minute}/min to {base_url} (Ctrl+C to stop)")
    while deadline is None or time.time() < deadline:
        cart = random_cart(catalogue)
        try:
            status = purchase(base_url, cart, validate=args.mode == "live")
        except requests.RequestException as err:
            status = type(err).__name__
        counts[status] = counts.get(status, 0) + 1
        print(f"{time.strftime('%H:%M:%S')} ${cart['total']:>4} -> {status}   totals: {json.dumps(counts)}", flush=True)
        # Poisson-ish spacing so it looks like real traffic
        time.sleep(random.expovariate(args.per_minute / 60))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
