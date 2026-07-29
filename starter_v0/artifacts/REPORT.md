# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Team

- Team:G34
- Members:
    - Dương Minh Quân - 2A202601903
    - Ngô Việt Anh - 2A202601579
    - Phí Đình Hoàng Anh - 2A202601853
    - Lê Thị Thuý - 2A202601381
    - Ngô Đình Khánh - 2A202601625
    - Trần Thị Kiều Oanh - 2A202601413
- Provider/model: openrouter/openai/gpt-4o-mini

---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

Research & Analytics Agent của nhóm G34: Đa năng trong việc tìm kiếm tin tức đa nguồn (Web, Twitter), tra cứu thời tiết, quy đổi tỷ giá ngoại tệ, theo dõi giá tiền mã hóa Crypto real-time, đọc nội dung URL và hỏi lại khi thiếu thông tin hoặc xin xác nhận trước khi thực hiện hành động nhạy cảm.

**Link dùng thử (truy cập được trong showdown):**

> Streamlit UI chạy tại địa chỉ local và có thể truy cập qua Cloudflare Tunnel:
>
> URL: `http://localhost:8501`

## A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại người dùng khi thiếu thông tin hoặc xin xác nhận trước khi hành động | Không |
| timeline | Lấy các bài đăng gần đây của một tài khoản Twitter cụ thể (ví dụ handle="sama") | Không |
| social_search | Tìm kiếm các bài đăng trên mạng xã hội Twitter theo từ khóa hoặc chủ đề | Không |
| lookup | Tra cứu thông tin và tin tức thời sự trên internet | Không |
| fetch | Đọc và trích xuất nội dung từ một địa chỉ URL | Không |
| format | Trình bày dữ liệu đã thu thập thành bản tổng hợp markdown digest | Không |
| send | Gửi văn bản lên kênh Telegram (bắt buộc phải xin xác nhận từ người dùng trước) | Không |
| weather_forecast | Tra cứu thời tiết hiện tại và dự báo thời tiết cho một vị trí/thành phố | **Có (Mới 1)** |
| currency_convert | Quy đổi tỷ giá ngoại tệ real-time giữa hai đồng tiền bất kỳ (USD, VND, EUR...) | **Có (Mới 2)** |
| crypto_price | Tra cứu giá các loại tiền mã hóa (Bitcoin, Ethereum, Solana...) real-time | **Có (Mới 3)** |

## A3. Câu hỏi mẫu để thử

1. "Tìm giúp mình tin tức AI mới nhất hôm nay trên web và mạng xã hội Twitter."
2. "Xem giúp mình thời tiết ở Hà Nội hôm nay thế nào?"
3. "Quy đổi giúp mình 100 USD sang đồng VND."
4. "Cho mình xem giá Bitcoin hiện tại theo USD."
5. "Đăng bản tin tổng hợp này lên Telegram giúp mình." *(Agent sẽ hỏi xin xác nhận Yes/No trước)*

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Yêu cầu thiếu handle: "Xem bài đăng mới nhất" | `clarify` (args: `response_type="text"`) | v0 tự bịa tài khoản `sama` → v1+v4 phát hiện thiếu handle và gọi `clarify` để hỏi người dùng | `runs/v4_B_base_openrouter_20260729T111729366000.json` |
| Hành động nhạy cảm: "Đăng bản tin này lên Telegram" | `clarify` (args: `response_type="yes_no"`) | v0 tự gửi ngay không chờ → v3+v4 bắt buộc xin xác nhận yes/no trước khi gọi `send` | `runs/v4_B_base_openrouter_20260729T111729366000.json` |
| Tra cứu đa năng: "Thời tiết ở Hà Nội và tỷ giá 100 USD sang VND" | `weather_forecast`, `currency_convert` | Tích hợp thành công 3 tool mới do nhóm tự phát triển với API real-time | `scratch/smoke_test_custom_tools.py` |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline | Baseline run to establish initial performance benchmark | case_accuracy | 0.0 | 0.65 | runs/v0_B_base_openrouter_20260729T101023034591.json |
| v1 | system_prompt.md | Instruct prompt on clarify rules, confirm before send, and out-of-scope handling | tool_routing_accuracy | 0.70 | 0.90 | runs/v1_B_base_openrouter_20260729T102352970001.json |
| v2 | tools.yaml | Require response_type in clarify schema and instruct explicit parameter conventions | case_accuracy | 0.65 | 0.95 | runs/v2_B_base_openrouter_20260729T102912146152.json |
| v3 | system_prompt.md | Explicitly instruct response_type=yes_no for action confirmation requests (including Vietnamese action verbs like "Đăng...", "Gửi...") | case_accuracy | 0.95 | 1.00 | runs/v3_B_base_openrouter_20260729T111226232576.json |
| v4 | system_prompt.md | Explicitly instruct clarify response_type=text for missing info on Vietnamese queries like "Xem bài đăng mới nhất" | case_accuracy | 0.95 | 1.00 | runs/v4_B_base_openrouter_20260729T111729366000.json |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R03_web_news_routing | wrong_arg_value | lookup | Redundant words in query ("AI news" instead of "AI") | Clarify in system prompt to keep search queries clean |
| R08_out_of_scope | out_of_scope | send | Called tool on out of scope query | Instruct prompt to return no tool when query is out of scope |
| R10_missing_handle | missing_info | timeline | Guessed handle instead of asking user | Instruct prompt to call `clarify` when handle is missing |
| R11_missing_url | missing_info | fetch | Guessed URL instead of asking user | Instruct prompt to call `clarify` when URL is missing |
| R12_confirm_before_send | wrong_boundary | send | Executed send without confirmation | Require `clarify` (yes_no) confirmation before send |
| R13_parallel_web_and_tweets | wrong_tool | lookup, timeline | Used timeline instead of social_search for topic tweets | Instruct prompt to use `social_search` for topic search |
| R14_out_of_scope_coding | out_of_scope | send | Called tool on out of scope coding question | Instruct prompt to refrain from calling tools for out of scope tasks |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

This section is for the mandatory team-authored eval set. Optional built-ins do
not belong here.

File template để trống có chủ đích; nhóm phải tự thiết kế đủ 10 case.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_weather_forecast | Single-turn: Tra cứu thời tiết tại Hanoi | `weather_forecast(location="Hanoi")` | **PASS** |
| G02_currency_convert | Single-turn: Quy đổi 100 USD sang VND | `currency_convert(from="USD", to="VND", amount=100)` | **PASS** |
| G03_crypto_price | Single-turn: Xem giá Bitcoin hiện tại theo USD | `crypto_price(symbol="bitcoin", currency="usd")` | **PASS** |
| G04_missing_url_clarify | Single-turn: Nhận biết thiếu URL bài viết | `clarify(response_type="text")` | **PASS** |
| G05_confirm_send | Single-turn: Yêu cầu xin xác nhận trước khi đăng Telegram | `clarify(response_type="yes_no")` | **PASS** |
| G06_multi_weather_followup | Multi-turn: Chuyển đổi ngữ cảnh địa điểm sang Tokyo | `weather_forecast(location="Tokyo")` | **PASS** |
| G07_multi_currency_change_amount | Multi-turn: Kế thừa USD/VND và đổi số tiền sang 500 | `currency_convert(from="USD", to="VND", amount=500)` | **PASS** |
| G08_multi_crypto_switch | Multi-turn: Chuyển đổi coin từ bitcoin sang ethereum | `crypto_price(symbol="ethereum")` | **PASS** |
| G09_multi_clarify_then_search | Multi-turn: Lượt 1 thiếu handle, lượt 2 bổ sung handle | `timeline(screenname="sama")` | **PASS** |
| G10_multi_out_of_scope_reset | Multi-turn: Lượt 2 yêu cầu viết code C++ ngoài phạm vi | `no_tool` (Refuse) | **PASS** |

## B4. Live chat evidence

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Tra cứu đa nguồn & Tin tức | v4 | `lookup(query="AI", topic="news")` | `runs/v4_B_base_openrouter_20260729T111729366000.json` | Agent lấy tin tức thời sự chuẩn xác |
| Yêu cầu thiếu handle ("Xem bài đăng") | v4 | `clarify(question="...", response_type="text")` | `runs/v4_B_base_openrouter_20260729T111729366000.json` | Agent không đoán mò mà gọi clarify hỏi handle |
| Xác nhận trước khi đăng Telegram | v4 | `clarify(question="...", response_type="yes_no")` | `runs/v4_B_base_openrouter_20260729T111729366000.json` | Agent dừng lại hỏi xin xác nhận Yes/No |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới 1 | `tools/weather_forecast/TOOL.md` | Geocoding & dự báo thời tiết real-time qua Open-Meteo API | Xử lý địa điểm không tồn tại |
| Must-have: tool mới 2 | `tools/currency_convert/TOOL.md` | Quy đổi tỷ giá ngoại tệ real-time qua ExchangeRate Open API | Kiểm tra mã đồng tiền hợp lệ |
| Bonus: tool mới 3 | `tools/crypto_price/TOOL.md` | Tra cứu giá tiền mã hóa real-time qua CoinGecko API | Xử lý coin ID không tồn tại |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**: Các quy tắc định hướng tư duy agent (không tự đoán handle/URL khi thiếu, bắt buộc gọi `clarify` với `response_type="yes_no"` xin xác nhận trước khi đăng bài, từ chối không gọi tool với câu hỏi coding ngoài phạm vi).
- **Which fixes belonged in `tools.yaml`?**: Việc khai báo tham số `required: [question, response_type]` bắt buộc trong schema của `clarify` và mô tả tham số `topic="news"` trong schema của `lookup`.
- **Which failure needed manual review instead of automatic grading?**: Các lỗi liên quan đến chất lượng nội dung câu hỏi trong `clarify` (Agent hỏi lại có lịch sự và đúng trọng tâm hay không) và tính thời sự của kết quả tìm kiếm web.
- **What would you improve next?**: Tích hợp caching cho các lượt tra cứu API thời tiết/tỷ giá để tối ưu chi phí và tăng tốc độ phản hồi cho UI Streamlit.
