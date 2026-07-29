# Tool: `news`

Lấy tin tức mới nhất theo chủ đề (công nghệ, kinh doanh, thể thao...) từ RSS feed.

## Input

- `topic` (string): chủ đề tin tức muốn đọc. Mặc định: `general`.
- `source` (string): nguồn tin — `vnexpress` (mặc định), `bbc`, `tuoitre`.
- `max_results` (int): số lượng bài tối đa. Mặc định: 5.

## Output

`dict` với các keys:
- `items`: list các dict có `title`, `url`, `summary`, `source`, `date`.
- `error`: `None` nếu thành công.
- `message`: thông báo lỗi nếu có.

## Implementation

Dùng `requests` + `xml.etree.ElementTree` để parse RSS feed công khai. Không cần API key.

## Smoke test

```bash
python -c "from pathlib import Path; from env_loader import load_lab_env; load_lab_env(Path.cwd()); from tools import TOOL_FUNCTIONS as T; r=T['news']('công nghệ', max_results=2); items=r.get('items') or []; print({'error':r.get('error'), 'item_count':len(items), 'first_title':items[0].get('title') if items else None})"
```