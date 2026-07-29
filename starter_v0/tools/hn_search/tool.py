from __future__ import annotations

from typing import Any
import requests

from tools._shared import TIMEOUT, err


def search_hackernews(query: str = "", limit: int = 5) -> dict[str, Any]:
    """Search developer stories and discussions on HackerNews via Algolia Search API."""
    try:
        if not query:
            return err("hn_search", "Missing required argument 'query'")

        url = "https://hn.algolia.com/api/v1/search"
        params = {"query": query, "hitsPerPage": int(limit or 5)}
        response = requests.get(url, params=params, timeout=TIMEOUT)
        response.raise_for_status()

        data = response.json()
        raw_hits = data.get("hits", [])

        items = []
        for hit in raw_hits:
            title = hit.get("title") or hit.get("story_title") or ""
            hit_url = hit.get("url") or hit.get("story_url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            author = hit.get("author") or ""
            points = hit.get("points") or 0
            comments = hit.get("num_comments") or 0
            date = hit.get("created_at")

            if title:
                items.append({
                    "title": title[:120],
                    "summary": f"Points: {points} | Comments: {comments} | By: {author}",
                    "url": hit_url,
                    "source": "HackerNews",
                    "date": date,
                    "metrics": {"points": points, "comments": comments},
                })

        return {
            "tool": "hn_search",
            "query": query,
            "items": items[: int(limit or 5)],
        }
    except Exception as exc:
        return err("hn_search", exc)
