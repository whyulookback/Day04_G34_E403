from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


TRANSCRIPTS_DIR = ROOT / "transcripts"
RUNS_DIR = ROOT / "runs"
DEFAULT_VERSION = "v9"


def new_transcript(
    *,
    version: str,
    provider_name: str,
    model: str | None,
    history_window: int,
    max_tool_rounds: int,
) -> tuple[dict[str, Any], Path]:
    artifact = build_artifact_version(
        version,
        ARTIFACTS_DIR / "system_prompt.md",
        ARTIFACTS_DIR / "tools.yaml",
    )
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(
        [safe_slug(version), safe_slug(provider_name), timestamp]
    )
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(ARTIFACTS_DIR / "system_prompt.md"),
        "tools": str(ARTIFACTS_DIR / "tools.yaml"),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(path, transcript)
    return transcript, path


def run_metrics() -> list[dict[str, Any]]:
    latest: dict[str, tuple[float, dict[str, Any]]] = {}
    for path in RUNS_DIR.glob("*_B_base_*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            version = str(payload.get("version", ""))
            generated = path.stat().st_mtime
            if version and (version not in latest or generated > latest[version][0]):
                latest[version] = (generated, payload)
        except (OSError, ValueError):
            continue
    rows = []
    for version in sorted(latest, key=lambda value: int(value[1:]) if value[1:].isdigit() else 999):
        payload = latest[version][1]
        summary = payload.get("summary", {})
        rows.append(
            {
                "version": version,
                "case_accuracy": summary.get("case_accuracy"),
                "routing": summary.get("tool_routing_accuracy"),
                "arguments": summary.get("argument_accuracy"),
                "multiturn": summary.get("multiturn_accuracy"),
                "provider_errors": summary.get("provider_error_cases"),
                "artifact": payload.get("artifact_version"),
            }
        )
    return rows


def render_trace(turn: dict[str, Any]) -> None:
    label = f"Turn {turn['turn_index']} · {turn.get('status', 'unknown')}"
    with st.expander(label, expanded=turn["turn_index"] == len(st.session_state.transcript["turns"])):
        for round_record in turn.get("rounds", []):
            st.markdown(f"**Round {round_record.get('round')}**")
            if round_record.get("assistant_text"):
                st.caption(round_record["assistant_text"])
            calls = round_record.get("tool_calls") or []
            results = round_record.get("tool_results") or []
            if not calls:
                st.write("No tool call.")
            for index, call in enumerate(calls):
                result = results[index] if index < len(results) else None
                st.code(
                    json.dumps(
                        {
                            "tool": call.get("name"),
                            "args": call.get("args", {}),
                            "result": result,
                        },
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    ),
                    language="json",
                )
        if turn.get("error"):
            st.error(turn["error"])


st.set_page_config(
    page_title="G34 Research Agent",
    page_icon="🔎",
    layout="wide",
)
load_lab_env(ROOT)

st.title("🔎 G34 Research Agent")
st.caption("Live research, full tool trace, artifact identity, and transcript evidence.")

with st.sidebar:
    st.header("Runtime")
    provider_name = st.selectbox(
        "Provider",
        ("openrouter", "openai", "anthropic", "gemini"),
        index=0,
    )
    version = st.text_input("Artifact version", value=DEFAULT_VERSION).strip() or DEFAULT_VERSION
    model_override = st.text_input("Model override (optional)").strip() or None
    history_window = st.slider("History window", 1, 10, 5)
    max_tool_rounds = st.slider("Max tool rounds", 1, 6, 4)
    config_signature = (
        provider_name,
        version,
        model_override,
        history_window,
        max_tool_rounds,
    )

    if st.button("New transcript", width="stretch"):
        for key in ("transcript", "transcript_path", "history", "config_signature"):
            st.session_state.pop(key, None)
        st.rerun()

system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
openai_tools = to_openai_tools(declarations)
artifact = build_artifact_version(
    version,
    ARTIFACTS_DIR / "system_prompt.md",
    ARTIFACTS_DIR / "tools.yaml",
)

if (
    "transcript" not in st.session_state
    or st.session_state.get("config_signature") != config_signature
):
    provider_for_metadata = make_provider(provider_name)
    selected_model = model_override or getattr(provider_for_metadata, "default_model", None)
    transcript, transcript_path = new_transcript(
        version=version,
        provider_name=provider_name,
        model=selected_model,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    st.session_state.transcript = transcript
    st.session_state.transcript_path = transcript_path
    st.session_state.history = []
    st.session_state.config_signature = config_signature

with st.sidebar:
    st.header("Artifact")
    st.code(artifact.artifact_version)
    st.caption(f"{len(declarations)} declared tools")
    st.caption(f"Transcript: {st.session_state.transcript_path.name}")
    transcript_json = json.dumps(
        st.session_state.transcript,
        ensure_ascii=False,
        indent=2,
        default=str,
    )
    st.download_button(
        "Download transcript",
        data=transcript_json,
        file_name=st.session_state.transcript_path.name,
        mime="application/json",
        width="stretch",
    )

tab_chat, tab_trace, tab_evidence, tab_tools = st.tabs(
    ["Chat", "Tool trace", "Version evidence", "Tools"]
)

with tab_chat:
    for turn in st.session_state.transcript["turns"]:
        with st.chat_message("user"):
            st.write(turn["user"])
        with st.chat_message("assistant"):
            if turn.get("error"):
                st.error(turn["error"])
            else:
                st.write(turn.get("assistant_text") or "")

    user_text = st.chat_input("Ask for web news, tweets, URL reading, or keyword extraction…")
    if user_text:
        turn_index = len(st.session_state.transcript["turns"]) + 1
        with st.chat_message("user"):
            st.write(user_text)
        turn_record: dict[str, Any] = {
            "turn_index": turn_index,
            "started_at": now_iso(),
            "user": user_text,
            "status": "started",
            "assistant_text": None,
            "rounds": [],
            "tool_events": [],
        }
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, history_window),
            {"role": "user", "content": user_text},
        ]
        with st.chat_message("assistant"):
            with st.spinner("Running agent and tools…"):
                try:
                    provider = make_provider(provider_name)
                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages,
                        tools=openai_tools,
                        model=model_override,
                        max_tool_rounds=max_tool_rounds,
                    )
                    turn_record.update(result)
                    assistant_text = result["assistant_text"]
                    st.write(assistant_text)
                    st.session_state.history.extend(
                        [
                            {"role": "user", "content": user_text},
                            {"role": "assistant", "content": assistant_text},
                        ]
                    )
                except Exception as exc:
                    turn_record.update(
                        {
                            "status": "provider_error",
                            "error": f"{type(exc).__name__}: {exc}",
                        }
                    )
                    st.error(turn_record["error"])
        turn_record["ended_at"] = now_iso()
        st.session_state.transcript["turns"].append(turn_record)
        write_transcript(
            st.session_state.transcript_path,
            st.session_state.transcript,
        )

with tab_trace:
    if not st.session_state.transcript["turns"]:
        st.info("Run a chat turn to see round-by-round tool evidence.")
    for turn in st.session_state.transcript["turns"]:
        render_trace(turn)

with tab_evidence:
    rows = run_metrics()
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)
    else:
        st.info("No base run JSON files found.")

with tab_tools:
    st.dataframe(
        [
            {
                "name": declaration["name"],
                "description": declaration.get("description", ""),
            }
            for declaration in declarations
        ],
        width="stretch",
        hide_index=True,
    )
