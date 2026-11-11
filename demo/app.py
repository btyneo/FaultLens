# demo/app.py
import base64
import html
import json
import sys
from datetime import datetime
from pathlib import Path

# make the project root importable (streamlit runs this file from inside demo/)
DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR.parent))

import altair as alt
import pandas as pd
import streamlit as st

from data.graph import sensor_to_subsystem
from run_pipeline import run_stages

LOGO = DEMO_DIR / "assets" / "logo.png"
CSS = DEMO_DIR / "style.css"
BLUE, AMBER = "#23508A", "#FF9500"

EXAMPLES = {
    "April 18, 2020 (documented air leak)": "Were there any air leaks on April 18, 2020?",
    "March 10, 2020 (comparison day)": "Any issues on March 10, 2020?",
    "Last 24 hours (no data case)": "Anything in the last 24 hours?",
}

st.set_page_config(page_title="FaultLens", page_icon=str(LOGO), layout="wide")


# ---------- helpers ----------
def load_css():
    st.markdown(f"<style>{CSS.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def header():
    logo_b64 = base64.b64encode(LOGO.read_bytes()).decode()
    st.markdown(
        f"""
        <div class="fl-header">
            <img src="data:image/png;base64,{logo_b64}" alt="FaultLens logo">
            <div>
                <h1>FaultLens</h1>
                <p>Multi-agent fault diagnosis for industrial equipment</p>
                <span class="fl-pill">MetroPT-3 · Air Production Unit · Feb–Sep 2020</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stage_header(num: int, title: str, subtitle: str):
    st.markdown(
        f"""
        <div class="fl-stage">
            <div class="fl-stage-num">{num}</div>
            <div>
                <div class="fl-stage-title">{title}</div>
                <div class="fl-stage-sub">{subtitle}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(text: str, kind: str = "info"):
    """Theme-proof message box. kind: info | warn | ok"""
    st.markdown(f'<div class="fl-note fl-note-{kind}">{text}</div>', unsafe_allow_html=True)


def router_table(parsed: dict):
    tw = parsed.get("time_window", {})
    rows = {
        "Start": tw.get("start", "-"),
        "End": tw.get("end", "-"),
        "Matched phrase": tw.get("matched_phrase") or "none (default: last 24h)",
        "Subsystem": parsed.get("subsystem") or "not specified",
    }
    body = "".join(f"<tr><td>{k}</td><td>{html.escape(str(v))}</td></tr>" for k, v in rows.items())
    st.markdown(f'<table class="fl-kv">{body}</table>', unsafe_allow_html=True)
    with st.expander("Raw output"):
        st.code(json.dumps(parsed, indent=2), language="json")


def flags_table(flags) -> pd.DataFrame:
    return (
        pd.DataFrame([{"sensor": f.sensor, "severity": f.severity} for f in flags])
        .groupby("sensor")["severity"]
        .agg(flags="count", max_severity="max")
        .round(2)
        .sort_values("flags", ascending=False)
        .reset_index()
    )


def flags_chart(table: pd.DataFrame, diagnosed_subsystem: str):
    table = table.copy()
    table["subsystem"] = table["sensor"].map(lambda s: sensor_to_subsystem.get(s, "unknown"))
    table["in_diagnosis"] = table["subsystem"] == diagnosed_subsystem
    return (
        alt.Chart(table)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("flags:Q", title="number of flags"),
            y=alt.Y("sensor:N", sort="-x", title=None),
            color=alt.condition("datum.in_diagnosis", alt.value(AMBER), alt.value(BLUE)),
            tooltip=["sensor", "subsystem", "flags", "max_severity"],
        )
        .properties(height=max(160, 32 * len(table)), background="white")
        .configure_view(strokeWidth=0)
        .configure_axis(labelColor="#5B6B82", titleColor="#5B6B82",
                        gridColor="#E8EDF5", domainColor="#C9D3E3", tickColor="#C9D3E3")
    )


# ---------- state ----------
st.session_state.setdefault("question", EXAMPLES["April 18, 2020 (documented air leak)"])
st.session_state.setdefault("decision", None)
st.session_state.setdefault("history", [])

load_css()

# ---------- sidebar (must come before the text input, it can change the question) ----------
with st.sidebar:
    st.markdown("### Try an example")
    for label, q in EXAMPLES.items():
        if st.button(label, width="stretch"):
            st.session_state.question = q

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown(
        '<div class="fl-side-note">'
        "Router → Retrieval → Anomaly detection → Diagnosis → Recommendation → "
        "<b>Human approval</b>.<br><br>Nothing is final until a person approves it."
        "</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### Decision log")
        st.dataframe(pd.DataFrame(st.session_state.history), hide_index=True, width="stretch")

# ---------- main ----------
header()

with st.container(border=True, key="card-question"):
    col_q, col_btn = st.columns([5, 1], vertical_alignment="bottom")
    col_q.text_input("Ask a question about the machine", key="question")
    run_clicked = col_btn.button("Run diagnosis", type="primary", width="stretch")

if run_clicked:
    with st.spinner("Running the pipeline… (the first run loads 1.5M rows)"):
        st.session_state.stages = run_stages(st.session_state.question)
        st.session_state.asked = st.session_state.question
    st.session_state.decision = None

if "stages" not in st.session_state:
    note("Ask a question or pick an example in the sidebar, then click <b>Run diagnosis</b>.")
    st.stop()

stages = st.session_state.stages

# 1 + 2: router and retrieval side by side
col1, col2 = st.columns(2)
with col1, st.container(border=True, key="card-router"):
    stage_header(1, "Router", "Question → time window + subsystem")
    router_table(stages["parsed"])
with col2, st.container(border=True, key="card-retrieval"):
    stage_header(2, "Retrieval", "Time window → sensor data")
    rows, cols = stages["data_shape"]
    m1, m2 = st.columns(2)
    m1.metric("Rows", f"{rows:,}")
    m2.metric("Sensors", cols)

if stages["recommendation"] is None:
    note("No sensor data in this time window, so nothing can be diagnosed. "
         "The dataset covers February to September 2020.", "warn")
    st.stop()

flags = stages["flags"]
d = stages["diagnosis"]

# 3: anomalies
with st.container(border=True, key="card-anomalies"):
    stage_header(3, "Anomaly detection", "Rolling z-score per sensor · amber = sensors in the diagnosed subsystem")
    if flags:
        table = flags_table(flags)
        m1, m2 = st.columns(2)
        m1.metric("Total flags", f"{len(flags):,}")
        m2.metric("Sensors flagged", len(table))
        st.altair_chart(flags_chart(table, d.subsystem), width="stretch")
        with st.expander("Show table"):
            st.dataframe(table, hide_index=True, width="stretch")
    else:
        note("No anomalies detected in this window.", "ok")

# 4: diagnosis
with st.container(border=True, key="card-diagnosis"):
    stage_header(4, "Diagnosis", "Component graph → most likely failing subsystem")
    c1, c2, c3 = st.columns(3)
    c1.metric("Subsystem", d.subsystem)
    c2.metric("Likely failure", d.likely_failure)
    c3.metric("Confidence", f"{d.confidence:.0%}")
    st.markdown(
        f'<div class="fl-conf-track"><div class="fl-conf-fill" style="width:{d.confidence * 100:.0f}%"></div></div>',
        unsafe_allow_html=True,
    )

# 5: recommendation
with st.container(border=True, key="card-recommendation"):
    stage_header(5, "Recommendation (draft)", "Not final until a person approves it")
    st.markdown(f'<div class="fl-rec">{html.escape(stages["recommendation"])}</div>', unsafe_allow_html=True)

# 6: human approval
with st.container(border=True, key="card-approval"):
    stage_header(6, "Human approval", "Approve or reject the draft recommendation")

    if st.session_state.decision is None:
        note = st.text_input("Note (optional)", placeholder="e.g. checked with maintenance team")
        col_a, col_r, _ = st.columns([1, 1, 3])
        approve = col_a.button("✓ Approve", type="primary", width="stretch")
        reject = col_r.button("✕ Reject", width="stretch")

        if approve or reject:
            st.session_state.decision = {
                "status": "approved" if approve else "rejected",
                "note": note,
                "time": datetime.now().strftime("%H:%M:%S"),
            }
            st.session_state.history.append({
                "time": st.session_state.decision["time"],
                "question": st.session_state.asked,
                "diagnosis": f"{d.likely_failure} ({d.subsystem})",
                "decision": st.session_state.decision["status"],
            })
            st.rerun()
    else:
        dec = st.session_state.decision
        note = f"<small>Note: {html.escape(dec['note'])}</small>" if dec["note"] else ""
        if dec["status"] == "approved":
            st.markdown(f'<div class="fl-decision fl-approved">✓ FINAL: recommendation approved at {dec["time"]}.{note}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="fl-decision fl-rejected">✕ REJECTED at {dec["time"]}: recommendation discarded, nothing is final.{note}</div>',
                        unsafe_allow_html=True)