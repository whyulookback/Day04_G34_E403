from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

# Ensure starter_v0 directory is in path
ROOT = Path(__file__).parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from env_loader import load_lab_env
from providers import make_provider
from tools import TOOL_FUNCTIONS, load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop

# Load environment
load_lab_env(ROOT)
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

# Page configuration
st.set_page_config(
    page_title="Research Agent - Day 04 Lab (Team G34)",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for rich aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #64748b;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    .tool-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        background-color: #e0e7ff;
        color: #3730a3;
        margin-right: 0.4rem;
    }
    .version-card {
        padding: 1rem;
        border-radius: 8px;
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.title("⚙️ Agent Configuration")
    provider_name = st.selectbox("Model Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
    version_name = st.selectbox("Artifact Version", ["v4", "v3", "v2", "v1", "v0"], index=0)
    max_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=5, value=3)
    
    st.divider()
    
    # Load artifact hashes
    sys_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    tools_yaml_path = ARTIFACTS_DIR / "tools.yaml"
    
    if sys_prompt_path.exists() and tools_yaml_path.exists():
        version_info = build_artifact_version(version_name, sys_prompt_path, tools_yaml_path)
        st.markdown(f"**Artifact Version:** `{version_info.artifact_version}`")
        st.caption(f"Prompt Hash: `{version_info.prompt_hash[:12]}...`")
        st.caption(f"Tools Hash: `{version_info.tools_hash[:12]}...`")
    
    st.divider()
    st.markdown("### 🛠️ Registered Tools")
    try:
        declarations = load_tool_declarations(tools_yaml_path)
        for t in declarations:
            st.markdown(f"- `<span class='tool-badge'>{t['name']}</span>` {t.get('description', '')}", unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading tools: {e}")

# Header
st.markdown("<div class='main-header'>🔍 Research & Analytics Agent</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Team G34 — Autonomous Research Agent with Tool Tracing</div>", unsafe_allow_html=True)

# Initialize Session State for Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []
if "transcript_history" not in st.session_state:
    st.session_state.transcript_history = []

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # If assistant message has tool trace events, render them cleanly
        if "tool_events" in msg and msg["tool_events"]:
            with st.expander("🔧 Tool Execution Trace", expanded=False):
                for idx, event in enumerate(msg["tool_events"], 1):
                    tool_name = event.get("tool")
                    args = event.get("args")
                    res = event.get("result")
                    err = res.get("error") if isinstance(res, dict) else None
                    
                    st.markdown(f"**Round {idx}: Calling `{tool_name}`**")
                    st.json(args, expanded=False)
                    if err:
                        st.error(f"Error: {err}")
                    st.json(res, expanded=False)

# User Chat Input
if prompt := st.chat_input("Hỏi gì đó (ví dụ: 'Tìm tin AI hôm nay', 'Thời tiết Hà Nội', 'Tỷ giá 100 USD sang VND')..."):
    # Add user message to state & display
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process Agent Loop
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.status("Agent is thinking and selecting tools...", expanded=True)
        
        try:
            # Initialize provider and system prompt
            provider = make_provider(provider_name)
            system_prompt = sys_prompt_path.read_text(encoding="utf-8")
            declarations = load_tool_declarations(tools_yaml_path)
            openai_tools = to_openai_tools(declarations)
            
            # Prepare conversation messages
            convo_messages = [{"role": "system", "content": system_prompt}]
            for m in st.session_state.messages:
                convo_messages.append({"role": m["role"], "content": m["content"]})
            
            # Execute agent tool loop
            loop_result = run_model_tool_loop(
                provider=provider,
                messages=convo_messages,
                tools=openai_tools,
                model=None,
                max_tool_rounds=max_rounds
            )
            
            status_placeholder.update(label="Response generated successfully!", state="complete", expanded=False)
            
            assistant_text = loop_result.get("assistant_text", "")
            tool_events = loop_result.get("tool_events", [])
            
            # Render response
            message_placeholder.markdown(assistant_text)
            
            # Render tool trace
            if tool_events:
                with st.expander("🔧 Tool Execution Trace", expanded=True):
                    for idx, event in enumerate(tool_events, 1):
                        tool_name = event.get("tool")
                        args = event.get("args")
                        res = event.get("result")
                        err = res.get("error") if isinstance(res, dict) else None
                        
                        st.markdown(f"**Step {idx}: Executed `{tool_name}`**")
                        st.json(args, expanded=False)
                        if err:
                            st.error(f"Execution Error: {err}")
                        else:
                            st.success(f"Result OK")
                        st.json(res, expanded=False)
            
            # Save assistant message to state
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_text,
                "tool_events": tool_events
            })
            
            # Save transcript JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            transcript_path = TRANSCRIPTS_DIR / f"{version_name}_live_{timestamp}.transcript.json"
            transcript_data = {
                "timestamp": datetime.now().isoformat(),
                "version": version_name,
                "provider": provider_name,
                "prompt": prompt,
                "response": assistant_text,
                "tool_events": tool_events,
                "rounds": loop_result.get("rounds", [])
            }
            transcript_path.write_text(json.dumps(transcript_data, ensure_ascii=False, indent=2), encoding="utf-8")
            
        except Exception as exc:
            status_placeholder.update(label="Execution Failed", state="error", expanded=True)
            st.error(f"Error during agent execution: {exc}")
