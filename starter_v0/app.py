from __future__ import annotations

import sys
import json
from pathlib import Path
import streamlit as st

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools, TOOL_FUNCTIONS
from chat import run_model_tool_loop

ROOT = Path(__file__).parent
load_lab_env(ROOT)

# Page configuration
st.set_page_config(
    page_title="AI Research Agent — Day 04 Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E88E5; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #555; margin-bottom: 1.5rem; }
    .stChatMessage { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Title & Description
st.markdown("<div class='main-header'>🔬 AI Research Agent UI</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Interactive Demonstration & Multi-Version Tool Trace Dashboard</div>", unsafe_allow_html=True)

# Sidebar — Configuration
st.sidebar.title("⚙️ System Configuration")
provider_name = st.sidebar.selectbox("Provider", ["openrouter", "openai", "gemini", "anthropic"], index=0)

version_choice = st.sidebar.selectbox("Artifact Version", ["v3 (Latest: 95% Acc)", "v2 (90% Acc)", "v1 (65% Acc)", "v0 (75% Baseline)"], index=0)
ver_code = version_choice.split()[0]

# Version metrics metadata map
VER_METRICS = {
    "v0": {"accuracy": "75%", "routing": "80%", "multiturn": "100%", "hash": "eb1c8179815b"},
    "v1": {"accuracy": "65%", "routing": "80%", "multiturn": "83%", "hash": "b349f381a54f"},
    "v2": {"accuracy": "90%", "routing": "95%", "multiturn": "83%", "hash": "214ce7ce30fb"},
    "v3": {"accuracy": "95%", "routing": "95%", "multiturn": "100%", "hash": "4a006df55ad6"},
}

m_info = VER_METRICS[ver_code]
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Version Benchmark")
col_s1, col_s2 = st.sidebar.columns(2)
col_s1.metric("Case Accuracy", m_info["accuracy"])
col_s2.metric("Routing Acc", m_info["routing"])
st.sidebar.caption(f"Prompt Hash: `{m_info['hash']}`")

# System Prompt & Tools loader
@st.cache_resource
def get_agent_resources():
    sys_prompt = (ROOT / "artifacts" / "system_prompt.md").read_text(encoding="utf-8")
    tools_decl = to_openai_tools(load_tool_declarations(ROOT / "artifacts" / "tools.yaml"))
    return sys_prompt, tools_decl

sys_prompt, tools_decl = get_agent_resources()

# Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "tool_traces" not in st.session_state:
    st.session_state.tool_traces = []

# Scenario presets
st.subheader("💡 Demo Scenarios")
sc_cols = st.columns(3)
preset_clicked = None
if sc_cols[0].button("1️⃣ HackerNews Research"):
    preset_clicked = "Tìm kiếm các bài thảo luận hot nhất về LLM trên HackerNews"
if sc_cols[1].button("2️⃣ Missing Info -> Clarify"):
    preset_clicked = "Cho tôi xem 5 bài đăng mới nhất"
if sc_cols[2].button("3️⃣ Sensitive Telegram Action"):
    preset_clicked = "Gửi tin nhắn 'Báo cáo Lab Day 04 đã hoàn tất' qua Telegram giúp mình"

# Display Chat History
st.subheader("💬 Interactive Agent Conversation")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# User Input Box
user_input = st.chat_input("Nhập câu hỏi hoặc yêu cầu cho Research Agent...")
if preset_clicked:
    user_input = preset_clicked

if user_input:
    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Call Model Provider & Execute Tools using run_model_tool_loop from chat.py
    with st.chat_message("assistant"):
        with st.spinner("Agent running tool loop & synthesizing response..."):
            try:
                provider = make_provider(provider_name)
                formatted_messages = [{"role": "system", "content": sys_prompt}] + [
                    {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
                ]

                # Reuse run_model_tool_loop from chat.py
                result_dict = run_model_tool_loop(
                    provider=provider,
                    messages=formatted_messages,
                    tools=tools_decl,
                    model=None,
                    max_tool_rounds=3,
                )

                final_text = result_dict.get("assistant_text", "")
                events = result_dict.get("tool_events", [])

                # If clarify tool was called, extract question text if assistant_text is empty
                if not final_text and events:
                    for ev in events:
                        if ev.get("tool") == "clarify":
                            final_text = ev.get("args", {}).get("question") or "Vui lòng cung cấp thêm thông tin chi tiết."
                            break
                        elif "result" in ev and "items" in ev["result"]:
                            items = ev["result"].get("items") or []
                            if items:
                                items_summary = "\n".join([f"- **{it.get('title')}**: {it.get('summary', '')[:100]} ({it.get('url', '')})" for it in items[:5]])
                                final_text = f"### Kết quả tìm kiếm ({ev['tool']}):\n{items_summary}"
                            else:
                                final_text = f"Đã thực thi `{ev['tool']}` thành công nhưng không tìm thấy dữ liệu phù hợp."

                if not final_text:
                    final_text = "Đã hoàn thành xử lý yêu cầu."

                st.write(final_text)
                st.session_state.messages.append({"role": "assistant", "content": final_text})

                # Save tool events to traces
                for ev in events:
                    st.session_state.tool_traces.append({
                        "tool": ev.get("tool"),
                        "args": ev.get("args"),
                        "status": "SUCCESS" if not ev.get("result", {}).get("error") else "ERROR",
                        "result": ev.get("result"),
                    })

            except Exception as e:
                st.error(f"Execution Error: {e}")

# Tool Traces & Transparency Panel
st.markdown("---")
st.subheader("🔍 Real-time Tool Call Trace & Transparency Logs")
if st.session_state.tool_traces:
    for idx, trace in enumerate(reversed(st.session_state.tool_traces)):
        with st.expander(f"Event #{len(st.session_state.tool_traces) - idx}: Tool `{trace['tool']}` [{trace['status']}]"):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Arguments:**")
                st.json(trace["args"])
            with c2:
                st.markdown("**Execution Output:**")
                st.json(trace["result"])
else:
    st.info("Chưa có tool nào được gọi trong phiên hội thoại này.")

# Footer & Control buttons
st.sidebar.markdown("---")
if st.sidebar.button("🧹 Clear Chat History"):
    st.session_state.messages = []
    st.session_state.tool_traces = []
    st.rerun()
