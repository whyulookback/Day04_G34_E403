---
name: hn_search
track: core
kind: live_api
provider: Algolia HackerNews API
requires_env: []
inputs: [query, limit]
outputs: [items]
side_effect: false
---
# hn_search

Searches developer discussions, technology stories, and startup news on HackerNews.
Use when the user specifically asks about discussions or stories on HackerNews or developer community trends.
Do NOT use for general web search or social media tweets.

Inputs:
- `query` (string, required): Search query keywords.
- `limit` (integer, optional, default: 5): Maximum number of items to return.

Outputs:
- `items`: List of HackerNews stories with title, url, points, comments, and author.
