"""News RSS tool — fetch news from public RSS feeds."""

from __future__ import annotations

from typing import Any

import requests
import xml.etree.ElementTree as ET


RSS_FEEDS = {
    "vnexpress": {
        "general": "https://vnexpress.net/rss/tin-moi-nhat.rss",
        "công nghệ": "https://vnexpress.net/rss/so-hoa.rss",
        "kinh doanh": "https://vnexpress.net/rss/kinh-doanh.rss",
        "thể thao": "https://vnexpress.net/rss/the-thao.rss",
        "giải trí": "https://vnexpress.net/rss/giai-tri.rss",
    },
    "tuoitre": {
        "general": "https://tuoitre.vn/rss/tin-moi-nhat.rss",
        "công nghệ": "https://tuoitre.vn/rss/cong-nghe.rss",
        "kinh doanh": "https://tuoitre.vn/rss/kinh-doanh.rss",
    },
    "bbc": {
        "general": "https://feeds.bbci.co.uk/news/rss.xml",
        "technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "business": "https://feeds.bbci.co.uk/news/business/rss.xml",
    },
}

DEFAULT_TIMEOUT = 15


def parse_rss(url: str, max_results: int) -> list[dict[str, str]]:
    resp = requests.get(url, timeout=DEFAULT_TIMEOUT)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    items: list[dict[str, str]] = []
    for entry in root.iter("item"):
        title = entry.findtext("title", "")
        link = entry.findtext("link", "")
        desc = entry.findtext("description", "")
        pubdate = entry.findtext("pubDate", "")
        items.append({
            "title": title,
            "url": link or "",
            "summary": desc[:300] if desc else "",
            "date": pubdate,
        })
        if len(items) >= max_results:
            break
    return items


def get_news(
    topic: str = "general",
    source: str = "vnexpress",
    max_results: int = 5,
) -> dict[str, Any]:
    """Fetch latest news by topic from public RSS feeds."""
    try:
        source_feeds = RSS_FEEDS.get(source)
        if not source_feeds:
            return {"items": [], "error": "unknown_source", "message": f"Nguồn '{source}' không hỗ trợ. Các nguồn: {', '.join(RSS_FEEDS.keys())}"}

        topic_key = topic.lower()
        url = source_feeds.get(topic_key) or source_feeds.get("general")
        if not url:
            return {"items": [], "error": "unknown_topic", "message": f"Chủ đề '{topic}' không có ở nguồn '{source}'."}

        items = parse_rss(url, max_results)
        return {"items": items, "error": None, "message": f"Found {len(items)} articles"}
    except requests.RequestException as exc:
        return {"items": [], "error": "request_failed", "message": str(exc)}
    except ET.ParseError as exc:
        return {"items": [], "error": "parse_error", "message": str(exc)}