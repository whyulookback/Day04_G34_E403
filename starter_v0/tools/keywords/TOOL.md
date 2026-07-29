---
name: keywords
track: core
kind: local_formatter
requires_env: []
inputs: [text, max_keywords, min_length]
outputs: [keywords, keyword_text, token_count]
side_effect: false
---
# keywords

Extracts a deterministic, frequency-ranked keyword list from text already
provided by the user. Use it for query planning, tagging, or summarizing themes.
It does not search the web, fetch URLs, or infer keywords from missing text.

