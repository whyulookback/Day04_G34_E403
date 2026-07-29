"""Streamlit UI for Research Agent — reuses run_model_tool_loop from chat.py."""

from __future__ import annotations

import json
import time as time_module
from datetime import datetime
from pathlib import Path

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, write_transcript, artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def init_session_state() -> None:
    """Initialise (or reset) all session-level state."""
    if "initialised" not in st.session_state:
        st.session_state.initialised = True
        st.session_state.messages: list[dict] = []  # {"role", "content", "details"}
        st.session_state.turn_count = 0
        st.session_state.transcript_id = None
        st.session_state.transcript_path = None
        st.session_state.transcript = None


def make_provider_for_ui(provider_name: str) -> object:
    """Instantiate a provider; st.error on failure."""
    try:
        return make_provider(provider_name)
    except ValueError as exc:
        st.error(f"Provider error: {exc}")
        st.stop()


def run_one_turn(provider, messages, tools, model, max_tool_rounds):
    """Run a single user turn and return the result dict."""
    return run_model_tool_loop(
        provider=provider,
        messages=messages,
        tools=tools,
        model=model,
        max_tool_rounds=max_tool_rounds,
    )


def render_tool_call(call: dict, result: dict | None = None) -> str:
    """Return a human-readable summary of one tool call."""
    args_str = json.dumps(call.get("args", {}), ensure_ascii=False, indent=2)
    text = f"**{call.get('name', '?')}**  \n```json\n{args_str}\n```"
    if result is not None:
        err = result.get("error")
        if err:
            text += f"\n❌ Error: `{err}`"
        else:
            text += "\n✅ Done"
    return text


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Research Agent — G34",
    page_icon="🔍",
    layout="wide",
)

init_session_state()

# ---------------------------------------------------------------------------
# Sidebar — config & controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## ⚙️ Config")

    provider_name = st.selectbox(
        "Provider",
        ["openrouter", "openai", "anthropic", "gemini"],
        index=0,
        key="provider_name",
    )

    model_override = st.text_input(
        "Model (optional, leave blank for default)",
        placeholder="e.g. openai/gpt-4o-mini",
        key="model_override",
    )

    version_label = st.text_input(
        "Version label",
        value="v0",
        key="version_label",
        help="Artifact version shown in transcript header",
    )

    max_tool_rounds = st.slider(
        "Max tool rounds per turn",
        min_value=1,
        max_value=10,
        value=4,
        key="max_tool_rounds",
    )

    history_window = st.slider(
        "History window (user/assistant pairs)",
        min_value=0,
        max_value=10,
        value=5,
        key="history_window",
    )

    st.markdown("---")
    st.markdown("### 🧰 Available tools")
    tool_decls = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    for t in tool_decls:
        st.markdown(f"- `{t['name']}` — {t.get('description', '')}")
    st.markdown("---")

    if st.button("🔄 New conversation", type="primary", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.caption(f"Team G34 · Day 04 Lab")

# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------
st.title("🔍 Research Agent")
st.caption(
    "Re-uses the same agent loop as `chat.py`. "
    "Each assistant response shows tool calls (name + args + result/error) in expandable details."
)

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("details"):
            with st.expander("🔧 Tool calls", expanded=False):
                st.markdown(msg["details"])

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
if prompt := st.chat_input("Ask something..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Build provider + tools
    try:
        provider = make_provider_for_ui(provider_name)
    except SystemExit:
        st.stop()

    tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
    openai_tools = to_openai_tools(tool_declarations)
    selected_model = (
        model_override.strip()
        or getattr(provider, "default_model", None)
        or None
    )
    artifact_version = build_artifact_version(
        version_label,
        ARTIFACTS_DIR / "system_prompt.md",
        ARTIFACTS_DIR / "tools.yaml",
    )

    # Build message list (same as chat.py)
    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
    from chat import trim_history

    history_pairs: list[dict[str, str]] = []
    for m in st.session_state.messages[:-1]:  # all except current user input
        if m["role"] in ("user", "assistant"):
            history_pairs.append({"role": m["role"], "content": m["content"]})
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(history_pairs, history_window),
        {"role": "user", "content": prompt},
    ]

    # Run
    with st.chat_message("assistant"):
        with st.spinner("Thinking and calling tools..."):
            start = time_module.time()
            result = run_one_turn(provider, messages, openai_tools, selected_model, max_tool_rounds)
            elapsed = time_module.time() - start

        assistant_text = result.get("assistant_text", "")
        rounds = result.get("rounds", [])
        tool_events = result.get("tool_events", [])
        status = result.get("status", "unknown")

        # Display assistant answer
        st.markdown(assistant_text)

        # Build tool-call details block
        details_lines = []
        for rnd in rounds:
            rn = rnd.get("round", "?")
            calls = rnd.get("tool_calls", [])
            results = rnd.get("tool_results", [])
            if calls:
                details_lines.append(f"### Round {rn}")
                for i, call in enumerate(calls):
                    res = results[i] if i < len(results) else None
                    details_lines.append(render_tool_call(call, res))
                details_lines.append("")

        tool_details = "\n\n".join(details_lines) if details_lines else "_No tool calls_"

        # Show tool details in expander
        with st.expander(f"🔧 Tool calls · {len(tool_events)} call(s) · ⏱ {elapsed:.1f}s", expanded=bool(tool_events)):
            st.markdown(tool_details)

        # Show status
        if status == "waiting_for_user":
            st.info(f"💬 Agent is waiting for more info: _{assistant_text}_")
        elif status == "max_tool_rounds":
            st.warning(f"⚠️ Reached max {max_tool_rounds} tool rounds — response may be incomplete.")

        # Save to session state
        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_text,
            "details": tool_details,
        })

        # Save transcript (same format as chat.py)
        timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
        transcript_id = f"{version_label}_{provider_name}_{timestamp}"
        transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
        turn_record = {
            "turn_index": st.session_state.turn_count + 1,
            "started_at": datetime.now().isoformat(timespec="seconds"),
            "ended_at": datetime.now().isoformat(timespec="seconds"),
            "user": prompt,
            "status": status,
            "assistant_text": assistant_text,
            "rounds": rounds,
            "tool_events": tool_events,
        }
        transcript = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": selected_model,
            "source": "streamlit_ui",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "turns": [turn_record],
        }
        write_transcript(transcript_path, transcript)
        st.session_state.transcript_id = transcript_id
        st.session_state.transcript_path = transcript_path
        st.session_state.turn_count += 1

        st.caption(f"Transcript: `{transcript_path.name}`")