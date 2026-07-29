from __future__ import annotations

import re
from collections import Counter
from typing import Any


WORD_RE = re.compile(r"[^\W\d_][\w'-]*", flags=re.UNICODE)

STOPWORDS = {
    # Vietnamese
    "ai", "bị", "bởi", "các", "cái", "cho", "chỉ", "có", "của", "đã",
    "đang", "để", "đến", "được", "gì", "giúp", "hãy", "khi", "không",
    "là", "lại", "mà", "một", "này", "những", "như", "nhiều", "ở",
    "ra", "rằng", "sau", "sẽ", "theo", "thì", "trên", "trong", "từ",
    "và", "về", "với",
    # English
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "have", "in", "is", "it", "of", "on", "or", "that", "the",
    "this", "to", "was", "were", "will", "with",
}


def extract_keywords(
    text: str = "",
    max_keywords: int = 8,
    min_length: int = 3,
) -> dict[str, Any]:
    clean_text = (text or "").strip()
    if not clean_text:
        return {
            "tool": "extract_keywords",
            "error": "missing_text",
            "message": "Provide non-empty text to extract keywords.",
            "keywords": [],
            "keyword_text": "",
            "token_count": 0,
        }

    limit = max(1, min(int(max_keywords or 8), 20))
    minimum = max(2, min(int(min_length or 3), 12))
    tokens = [
        token.lower().strip("-'")
        for token in WORD_RE.findall(clean_text)
    ]
    candidates = [
        token
        for token in tokens
        if len(token) >= minimum and token not in STOPWORDS
    ]

    counts = Counter(candidates)
    first_index: dict[str, int] = {}
    for index, token in enumerate(candidates):
        first_index.setdefault(token, index)

    ranked = sorted(
        counts,
        key=lambda token: (-counts[token], first_index[token], token),
    )[:limit]
    keywords = [
        {"term": token, "count": counts[token]}
        for token in ranked
    ]
    return {
        "tool": "extract_keywords",
        "keywords": keywords,
        "keyword_text": ", ".join(item["term"] for item in keywords),
        "token_count": len(tokens),
    }

