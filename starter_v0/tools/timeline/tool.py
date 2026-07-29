from __future__ import annotations

import os
from typing import Any

import requests

from tools._shared import TIMEOUT, err


def _twitter_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    key = os.getenv("RAPIDAPI_KEY")
    host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
    if not key:
        raise RuntimeError("Missing RAPIDAPI_KEY env var")
    response = requests.get(
        f"https://{host}{path}",
        params=params,
        headers={"x-rapidapi-key": key, "x-rapidapi-host": host},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _tweet_item(raw: dict[str, Any]) -> dict[str, Any]:
    handle = raw.get("screen_name") or (raw.get("author") or {}).get("screen_name") or ""
    tweet_id = raw.get("tweet_id") or raw.get("id") or ""
    text = (raw.get("text") or "").strip()
    return {
        "title": text.split("\n")[0][:120],
        "summary": text,
        "url": f"https://x.com/{handle}/status/{tweet_id}" if handle and tweet_id else "",
        "source": f"@{handle}" if handle else "x.com",
        "date": raw.get("created_at"),
        "metrics": {"favorites": raw.get("favorites"), "retweets": raw.get("retweets"), "views": raw.get("views")},
    }


def _twitter241_timeline(screenname: str, limit: int) -> list[dict[str, Any]]:
    host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter241.p.rapidapi.com")
    u_data = _twitter_get("/user", {"username": screenname})
    rest_id = u_data.get("result", {}).get("data", {}).get("user", {}).get("result", {}).get("rest_id")
    if not rest_id:
        return []
    tw_data = _twitter_get("/user-tweets", {"user": rest_id})
    instructions = tw_data.get("result", {}).get("timeline", {}).get("instructions", [])
    items = []
    for inst in instructions:
        for entry in inst.get("entries", []):
            tweet_results = entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {})
            legacy = tweet_results.get("legacy", {}) or tweet_results.get("tweet", {}).get("legacy", {})
            text = (legacy.get("full_text") or "").strip()
            tweet_id = legacy.get("id_str") or ""
            if text and tweet_id:
                items.append({
                    "title": text.split("\n")[0][:120],
                    "summary": text,
                    "url": f"https://x.com/{screenname}/status/{tweet_id}",
                    "source": f"@{screenname}",
                    "date": legacy.get("created_at"),
                    "metrics": {
                        "favorites": legacy.get("favorite_count"),
                        "retweets": legacy.get("retweet_count"),
                        "views": legacy.get("reply_count"),
                    },
                })
    return items[: int(limit or 5)]


def get_user_tweets(screenname: str = "", limit: int = 5) -> dict[str, Any]:
    try:
        host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
        if "twitter241" in host:
            items = _twitter241_timeline(screenname, limit)
        else:
            data = _twitter_get("/timeline.php", {"screenname": screenname})
            items = _tweets_from(data, limit)
        return {"tool": "get_user_tweets", "screenname": screenname, "items": items}
    except Exception as exc:
        return err("get_user_tweets", exc)


