from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env


SAFE_RATE_HEADERS = (
    "x-ratelimit-requests-limit",
    "x-ratelimit-requests-remaining",
    "x-ratelimit-requests-reset",
    "retry-after",
)


def response_summary(response: requests.Response) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "status": response.status_code,
        "url": response.url,
    }
    rate_headers = {
        name: response.headers[name]
        for name in SAFE_RATE_HEADERS
        if name in response.headers
    }
    if rate_headers:
        summary["rate_headers"] = rate_headers

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        summary["response_keys"] = sorted(payload.keys())
        for key in ("message", "error", "detail"):
            if payload.get(key):
                summary[key] = str(payload[key])[:500]
        items = payload.get("timeline") or payload.get("tweets")
        if isinstance(items, list):
            summary["item_count"] = len(items)
    elif response.text:
        summary["body_preview"] = response.text[:500]
    return summary


def call_endpoint(
    *,
    host: str,
    key: str,
    path: str,
    params: dict[str, Any],
) -> bool:
    response = requests.get(
        f"https://{host}{path}",
        params=params,
        headers={
            "x-rapidapi-key": key,
            "x-rapidapi-host": host,
        },
        timeout=30,
    )
    print(f"\n{path}")
    for name, value in response_summary(response).items():
        print(f"{name}: {value}")
    return response.ok


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check Twitter API45 without printing RAPIDAPI_KEY."
    )
    parser.add_argument(
        "--tool",
        choices=("all", "timeline", "search"),
        default="all",
    )
    parser.add_argument("--screenname", default="sama")
    parser.add_argument("--query", default="OpenAI")
    args = parser.parse_args()

    load_lab_env(ROOT)
    key = os.getenv("RAPIDAPI_KEY", "").strip()
    host = os.getenv(
        "RAPIDAPI_TWITTER_HOST",
        "twitter-api45.p.rapidapi.com",
    ).strip()

    if not key:
        raise SystemExit("Missing RAPIDAPI_KEY in starter_v0/.env")
    if not host:
        raise SystemExit("Missing RAPIDAPI_TWITTER_HOST in starter_v0/.env")

    print(f"host: {host}")
    print("api_key: loaded (value hidden)")

    checks: list[bool] = []
    if args.tool in ("all", "timeline"):
        checks.append(
            call_endpoint(
                host=host,
                key=key,
                path="/timeline.php",
                params={"screenname": args.screenname},
            )
        )
    if args.tool in ("all", "search"):
        checks.append(
            call_endpoint(
                host=host,
                key=key,
                path="/search.php",
                params={"query": args.query, "search_type": "Latest"},
            )
        )

    if not all(checks):
        raise SystemExit(1)
    print("\nPASS: all requested RapidAPI checks returned HTTP 2xx.")


if __name__ == "__main__":
    main()
