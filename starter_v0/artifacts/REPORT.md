# Day 04 Lab v2 Report — Research Agent

## Team

- Team: G34
- Members:
  - Dương Minh Quân — 2A202601903
  - Ngô Việt Anh — 2A202601579
  - Phí Đình Hoàng Anh — 2A202601853
  - Lê Thị Thuý — 2A202601381
  - Ngô Đình Khánh — 2A202601625
  - Trần Thị Kiều Oanh — 2A202601413
- Provider/model: `openrouter/openai/gpt-4o-mini`
- Final artifact: `v9+p5c7b7a015185+tecf7656f13ed`

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

G34 Research Agent tìm tin trên web, tìm bài đăng theo chủ đề hoặc tài khoản,
đọc URL, trình bày digest và trích từ khóa từ văn bản có sẵn. Agent có boundary
rõ cho thông tin còn thiếu và hành động gửi ra ngoài.

**Link dùng thử local:** `http://localhost:8501`

Chạy bằng:

```powershell
streamlit run app.py
```

Nếu team khác cần truy cập từ máy riêng trong showdown:

```powershell
cloudflared tunnel --url http://localhost:8501
```

URL `trycloudflare.com` chỉ sống trong phiên tunnel nên phải tạo và kiểm tra lại
ngay trước demo.

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| `clarify` | Hỏi thông tin còn thiếu hoặc xác nhận yes/no | Không |
| `timeline` | Lấy bài đăng gần đây của một tài khoản đã xác định | Không |
| `social_search` | Tìm bài đăng mạng xã hội theo chủ đề | Không |
| `lookup` | Tìm web hoặc tin tức theo timeframe | Không |
| `fetch` | Đọc nội dung từ URL đã cung cấp | Không |
| `format` | Trình bày item đã có thành digest Markdown | Không |
| `keywords` | Trích từ khóa từ text có sẵn, chạy local | **Có** |
| `send` | Gửi Telegram sau confirmation | Không — optional built-in |
| `policy` | Tìm trong policy nội bộ | Không — optional built-in |
| `papers` | Tìm paper trên arXiv | Không — optional built-in |
| `paper_text` | Trích text từ paper arXiv | Không — optional built-in |

## A3. Câu hỏi mẫu để thử

1. `Tìm trên web tin AI hôm nay.`
2. `Lấy 3 tweet mới nhất của @sama.`
3. `Tìm mọi người đang nói gì về robotics trên Twitter.`
4. `Đọc và tóm tắt URL https://example.com.`
5. `Trích 5 từ khóa từ đoạn văn: AI agents cần log thật để đánh giá tool.`

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback evidence |
|---|---|---|---|
| Tin AI hôm nay | `lookup(query="tin AI", topic="news", timeframe="day")` | v0 thiếu routing convention; v5/v9 giữ đúng nguồn và timeframe | `transcripts/v9_openrouter_20260729T113840826457.transcript.json` |
| Thiếu account rồi bổ sung | `clarify(text)` → `timeline(screenname="sama", limit=2)` | v0 tự đoán account; v1 hỏi lại; v9 ground handle từ conversation | `transcripts/v9_openrouter_20260729T113851375781.transcript.json` |
| Đăng Telegram | `clarify(response_type="yes_no")`, không gọi `send` | v0 gửi ngay; v3/v7 làm rõ confirmation boundary | `transcripts/v9_openrouter_20260729T113902410783.transcript.json` |
| Tool mới keywords | `keywords(text=..., max_keywords=4)` | v6 thêm capability local; final group case pass | `runs/v9_B_group_openrouter_20260729T113647727096.json` |

---

# PHẦN B — Chi tiết / Bằng chứng

Metric chỉ được dùng khi `provider_error_cases=0`,
`measured_cases=total_cases`, và tool errors đã được review. Final base và group
run đều đáp ứng các điều kiện này; `tool_errors=0`.

## B1. Version evidence

| Version | Thay đổi duy nhất | Giả thuyết / kết quả | Metric | Before | After | Run |
|---|---|---|---|---:|---:|---|
| v0 | Baseline starter prompt | Đo hành vi ban đầu | case accuracy |  | 0.70 | `runs/v0_B_base_openrouter_20260729T105641646925.json` |
| v1 | Hỏi lại thay vì đoán handle/URL | R10/R11 pass | case accuracy | 0.70 | 0.90 | `runs/v1_B_base_openrouter_20260729T105823538203.json` |
| v2 | Confirmation boundary trước `send` | Chặn direct send nhưng R12 dùng sai kiểu clarify | case accuracy | 0.90 | 0.85 | `runs/v2_B_base_openrouter_20260729T105949344829.json` |
| v3 | Định nghĩa “bản tin này” là nội dung đủ để hỏi yes/no | R12 chuyển sang `clarify(yes_no)` | R12 pass | 0 | 1 | `runs/v3_B_base_openrouter_20260729T110138728492.json` |
| v4 | Account resolution + source carryover | R01/M06 pass | case accuracy | 0.85 | 0.90 | `runs/v4_B_base_openrouter_20260729T111247552685.json` |
| v5 | Cấm social query rỗng; news bắt buộc dùng lookup | Base pass toàn bộ | case accuracy | 0.90 | 1.00 | `runs/v5_B_base_openrouter_20260729T111444186822.json` |
| v6 | Thêm tool mới `keywords` | Có một regression R12 khi tool set đổi | case accuracy | 1.00 | 0.95 | `runs/v6_B_base_openrouter_20260729T112820303125.json` |
| v7 | Làm rõ yes/no trong declaration `clarify` | Base trở lại 20/20 | case accuracy | 0.95 | 1.00 | `runs/v7_B_base_openrouter_20260729T113011199577.json` |
| v8 | Làm rõ account requirement trong declaration `timeline` | Base không regression; group missing-account vẫn fail | group accuracy | 0.90 | 0.90 | `runs/v8_B_group_openrouter_20260729T113316427245.json` |
| v9 | Ground `screenname` trong conversation, bỏ example handle | Base 20/20; final group sau khi bỏ ambiguity của case đạt 10/10 | base accuracy | 1.00 | 1.00 | `runs/v9_B_base_openrouter_20260729T113510968680.json` |

Chi tiết hash và hypothesis đầy đủ nằm trong `artifacts/version_log.csv`.

## B2. Failure analysis

| Case ID / Version | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R10/R11 v0 | missing_info | `timeline(sama)` / `fetch(example.com)` | Tự đoán handle và URL | v1 yêu cầu `clarify(text)` khi thiếu identifier |
| R12 v0 | wrong_boundary | `send(text=...)` | Gửi trước confirmation | v2/v3 sửa prompt; v7 sửa declaration `clarify` |
| R13 v0 | wrong_arg_value | `lookup(query="AI news")` thiếu `topic=news` | Convention query/topic không rõ | v4/v5 thêm source và news conventions |
| R08/R14 v0 | out_of_scope | Dùng `send` cho câu trả lời thường | Tool boundary và out-of-scope mơ hồ | v1–v5 thu hẹp routing, không dùng action tool để trả lời |
| R12 v6 | wrong_boundary | `clarify(response_type="text")` | Tool set mới làm lộ ambiguity trong declaration | v7 ghi rõ send/post/publish luôn dùng `yes_no` |
| G34_M04 v7–v9 draft | missing_info | `timeline(screenname="sama")` | Case draft có “Đúng rồi” tạo confirmation ngầm và example handle bị dùng làm default | Bỏ example handle và sửa team-authored case thành missing-account intent rõ ràng |

Các run ban đầu từng có RapidAPI 403/429 dù routing PASS. Sau khi subscribe
đúng plan, smoke test trả HTTP 200 và các final run có `tool_errors=0`. Đây là
phần cần manual review vì automatic grader chỉ chấm routing/args.

## B3. Team eval cases

Final evidence: `runs/v9_B_group_openrouter_20260729T113647727096.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G34_S01_extract_keywords | Tool mới trên text có sẵn | `keywords`, max 4 | PASS |
| G34_S02_timeline_handle_limit | Account timeline + limit | `timeline(sama, 3)` | PASS |
| G34_S03_web_news_week | Web/news/timeframe | `lookup(robotics, news, week)` | PASS |
| G34_S04_missing_url | Không bịa URL | `clarify(text)` | PASS |
| G34_S05_capability_no_tool | Capability question | No tool | PASS |
| G34_M01_switch_social_to_web | Source correction qua turn | `lookup(OpenAI, news, day)` | PASS |
| G34_M02_carry_account_change_limit | Carry account + sửa limit | `timeline(elonmusk, 2)` | PASS |
| G34_M03_confirm_before_send | Confirmation boundary | `clarify(yes_no)` | PASS |
| G34_M04_missing_account_after_limit | Thiếu account dù có limit | `clarify(text)` | PASS |
| G34_M05_cancel_to_capability | Hủy research | No tool | PASS |

Tổng: **10/10**, gồm **5 single-turn + 5 multi-turn**.

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript | Outcome |
|---|---|---|---|---|
| Research bình thường | v9 | `lookup(query="tin AI", topic="news", timeframe="day")` | `transcripts/v9_openrouter_20260729T113840826457.transcript.json` | HTTP tool result thật, trả 5 nguồn |
| Thiếu handle | v9 | `clarify(response_type="text")` | `transcripts/v9_openrouter_20260729T113851375781.transcript.json`, turn 1 | Dừng và chờ user |
| User bổ sung `@sama` | v9 | `timeline(screenname="sama", limit=2)` | cùng transcript, turn 2 | Trả đúng 2 tweet |
| Hành động Telegram | v9 | `clarify(response_type="yes_no")` | `transcripts/v9_openrouter_20260729T113902410783.transcript.json` | Không gọi `send`, không có side effect |

## B5. Tool capability evidence

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: `keywords` | `tools/keywords/TOOL.md`, `tools/keywords/tool.py`, final group run G34_S01 | Registry, YAML declaration, deterministic local extraction, không cần key | Chỉ dùng khi user cung cấp text; không thay `lookup`/`fetch` |
| Optional built-in | Không claim | `send`, `policy`, `papers`, `paper_text` vẫn có implementation | Không dùng optional tool để chứng minh core; Telegram luôn cần confirmation |
| Bonus tool thứ 4 trở đi | Không claim | Nhóm chỉ thêm một tool mới bắt buộc | Không khai bonus không có evidence |

Smoke test của `keywords` trả:

```text
tools, agents, evaluate, need
```

với `error=None`, registry/declaration đều tìm thấy tool.

## B6. Reflection

- `system_prompt.md` phù hợp cho policy xuyên tool: missing information,
  source carryover, timeframe, account grounding và action boundary.
- `tools.yaml` phù hợp cho contract cục bộ: khi nào dùng `clarify`,
  `timeline`, `keywords`, argument convention và trường hợp không được dùng.
- RapidAPI 403/429 cần manual review; routing PASS không chứng minh endpoint
  chạy được. Final run chỉ được chấp nhận sau khi HTTP 200 và `tool_errors=0`.
- Group case G34_M04 ban đầu có wording mơ hồ. Việc sửa case team-authored
  được ghi rõ; fixed `eval_base.json` không bị chỉnh sửa.
- Bước tiếp theo nếu có thêm thời gian: pin exact dependency versions, thêm
  unit tests cho UI transcript persistence và deploy URL bền vững thay cho
  temporary tunnel.

## B7. UI và final gates

- UI: `app.py`, dùng trực tiếp `run_model_tool_loop` từ `chat.py`.
- Hiển thị request/response, round, tool name, args, result/error, artifact
  version, version evidence và download transcript.
- Local HTTP smoke test: `http://127.0.0.1:8501` trả status 200.
- Streamlit AppTest: không có exception.
- Final base: **20/20**, mọi accuracy **1.00**.
- Final group: **10/10**, mọi accuracy **1.00**.
- Final provider errors: **0**.
- Final tool execution errors: **0**.
- Analysis CSV: `analysis/base-and-group-runs.csv`.

