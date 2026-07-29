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

> 1–2 câu mô tả agent dùng để làm gì.

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL và tổng hợp thành digest."

**Link dùng thử (truy cập được trong showdown):**

> Dán public URL nếu người khác cần mở từ máy riêng; localhost cũng được nếu demo trực tiếp trên máy trình chiếu. Streamlit được khuyến nghị, nhưng nhóm có thể dùng bất kỳ framework nào.
>
> URL:

## A2. Tool agent có

> Liệt kê các tool agent đang dùng. Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin | không |
|  |  |  |
|  |  |  |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1.
2.
3.

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
|  |  |  |  |

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
| v3 | system_prompt.md | Explicitly instruct response_type=yes_no when user requests to send or post | case_accuracy | 0.95 | 1.00 | runs/v3_B_base_openrouter_20260729T103734905150.json |

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
|  |  |  |  |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
|  |  |  |  |  |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/PDF nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên |  |  |  |
| Optional built-in |  |  |  |
| Bonus: tool mới thứ 4 trở đi |  |  |  |

## B6. Reflection

- Which fixes belonged in `system_prompt.md`?
- Which fixes belonged in `tools.yaml`?
- Which failure needed manual review instead of automatic grading?
- What would you improve next?
