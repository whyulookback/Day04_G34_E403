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


def _twitter241_search(query: str, search_type: str, limit: int) -> list[dict[str, Any]]:
    type_map = {"Latest": "Latest", "Top": "Top"}
    st = type_map.get(search_type, "Latest")
    data = _twitter_get("/search", {"query": query, "type": st})
    instructions = data.get("result", {}).get("timeline", {}).get("instructions", [])
    items = []
    for inst in instructions:
        for entry in inst.get("entries", []):
            tweet_results = entry.get("content", {}).get("itemContent", {}).get("tweet_results", {}).get("result", {})
            legacy = tweet_results.get("legacy", {}) or tweet_results.get("tweet", {}).get("legacy", {})
            text = (legacy.get("full_text") or "").strip()
            tweet_id = legacy.get("id_str") or ""
            user_results = tweet_results.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
            handle = user_results.get("screen_name") or ""
            if text and tweet_id:
                items.append({
                    "title": text.split("\n")[0][:120],
                    "summary": text,
                    "url": f"https://x.com/{handle}/status/{tweet_id}" if handle else f"https://x.com/i/status/{tweet_id}",
                    "source": f"@{handle}" if handle else "x.com",
                    "date": legacy.get("created_at"),
                    "metrics": {
                        "favorites": legacy.get("favorite_count"),
                        "retweets": legacy.get("retweet_count"),
                        "views": legacy.get("reply_count"),
                    },
                })
    return items[: int(limit or 5)]


def search_tweets(query: str = "", search_type: str = "Latest", limit: int = 5) -> dict[str, Any]:
    try:
        host = os.getenv("RAPIDAPI_TWITTER_HOST", "twitter-api45.p.rapidapi.com")
        if "twitter241" in host:
            items = _twitter241_search(query, search_type, limit)
        else:
            data = _twitter_get("/search.php", {"query": query, "search_type": search_type})
            items = _tweets_from(data, limit)
        return {"tool": "search_tweets", "query": query, "search_type": search_type, "items": items}
    except Exception as exc:
        return err("search_tweets", exc)


