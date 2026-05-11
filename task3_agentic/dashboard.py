
import streamlit as st
import json, re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

st.set_page_config(
    page_title="Agent Trace — CDAZZDEV Task 3",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Custom CSS ----
st.markdown("""
<style>
.metric-card {
    background: #f8f9fa;
    border-left: 4px solid #4f46e5;
    padding: 12px 16px;
    border-radius: 6px;
    margin-bottom: 8px;
}
.tool-pill {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin: 2px;
}
.pill-price { background:#dbeafe; color:#1e40af; }
.pill-vol   { background:#fce7f3; color:#9d174d; }
.pill-news  { background:#d1fae5; color:#065f46; }
.pill-sent  { background:#fef3c7; color:#92400e; }
.pill-web   { background:#ede9fe; color:#4c1d95; }
.badge-ok  { background:#d1fae5; color:#065f46; padding:2px 8px; border-radius:10px; font-size:11px; }
.badge-err { background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:10px; font-size:11px; }
</style>
""", unsafe_allow_html=True)

PILL = {
    "get_price_data":       "pill-price",
    "calculate_volatility": "pill-vol",
    "get_news":             "pill-news",
    "llm_sentiment":        "pill-sent",
    "web_search":           "pill-web",
}

# ---- Load trace ----
TRACE_FILE = "logs/agent_trace.jsonl"

@st.cache_data(ttl=5)
def load_trace():
    records = []
    p = Path(TRACE_FILE)
    if p.exists():
        with open(p) as f:
            for line in f:
                line = line.strip()
                if line:
                    try: records.append(json.loads(line))
                    except: pass
    return records

@st.cache_data(ttl=5)
def load_cache_files():
    files = []
    for p in Path("research_cache").glob("*.json"):
        try:
            with open(p) as f:
                data = json.load(f)
            files.append({"file": p.name, "ticker": data.get("ticker","?"),
                           "date": data.get("date","?"),
                           "report_preview": str(data.get("report",""))[:120]})
        except: pass
    return files

records = load_trace()

# ---- Sidebar ----
with st.sidebar:
    st.image("https://img.shields.io/badge/CDAZZDEV-MLE-4f46e5?style=for-the-badge", width=200)
    st.markdown("### 🤖 Agent Trace Dashboard")
    st.caption("Task 3 — Multi-Agent Financial Research")
    st.divider()

    if not records:
        st.error("No agent_trace.jsonl found.\nRun the notebook first, then refresh.")
        st.stop()

    sessions = ["All"] + list(dict.fromkeys(r["session_id"] for r in records))
    sel_session = st.selectbox("Session", sessions, index=0)
    st.divider()

    tools_all = list(dict.fromkeys(r["tool_name"] for r in records))
    sel_tools = st.multiselect("Filter tools", tools_all, default=tools_all)
    st.divider()

    st.caption(f"📄 Trace file: `{TRACE_FILE}`")
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()

# ---- Filter ----
df = pd.DataFrame(records)
print(df.columns.tolist())
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df["has_error"]  = df["output_truncated"].str.lower().str.contains("error", na=False)

if sel_session != "All":
    df = df[df["session_id"] == sel_session]
df = df[df["tool_name"].isin(sel_tools)]

# ---- Header ----
st.title("🔍 Agent Trace Dashboard")
st.caption(
    f"CDAZZDEV-MLE Task 3 · {len(df)} tool calls · "
    f"{df['session_id'].nunique()} session(s) · "
    f"Last call: {df['timestamp'].max().strftime('%H:%M:%S') if len(df) > 0 else 'N/A'}"
)

# ---- KPI Row ----
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Calls",     len(df))
c2.metric("Avg Duration",    f"{df['duration_seconds'].mean():.2f}s")
c3.metric("Slowest Call",    f"{df['duration_seconds'].max():.2f}s")
c4.metric("Error Calls",     int(df['has_error'].sum()))
c5.metric("Unique Tools",    df['tool_name'].nunique())

st.divider()

# ---- Two-column layout ----
col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📊 Tool Call Duration")
    fig_bar = px.bar(
        df.sort_values("timestamp"),
        x="tool_name", y="duration_seconds",
        color="tool_name",
        text="duration_seconds",
        labels={"tool_name": "Tool", "duration_seconds": "Duration (s)"},
        color_discrete_map={
            "get_price_data": "#3b82f6",
            "calculate_volatility": "#ec4899",
            "get_news": "#10b981",
            "llm_sentiment": "#f59e0b",
            "web_search": "#8b5cf6",
        },
        template="plotly_white",
    )
    fig_bar.update_traces(texttemplate="%{text:.2f}s", textposition="outside")
    fig_bar.update_layout(showlegend=False, height=320,
                           margin=dict(l=0, r=0, t=20, b=40),
                           xaxis_title="", yaxis_title="seconds")
    st.plotly_chart(fig_bar, use_container_width=True)

with col_right:
    st.subheader("🥧 Tool Distribution")
    counts = df["tool_name"].value_counts().reset_index()
    counts.columns = ["tool", "count"]
    fig_pie = px.pie(
        counts, names="tool", values="count",
        color="tool",
        color_discrete_map={
            "get_price_data": "#3b82f6", "calculate_volatility": "#ec4899",
            "get_news": "#10b981", "llm_sentiment": "#f59e0b", "web_search": "#8b5cf6",
        },
        hole=0.45, template="plotly_white",
    )
    fig_pie.update_traces(textinfo="percent+label")
    fig_pie.update_layout(showlegend=False, height=320,
                           margin=dict(l=0, r=0, t=20, b=0))
    st.plotly_chart(fig_pie, use_container_width=True)

st.divider()

# ---- Timeline ----
st.subheader("⏱️ Tool Call Timeline")
if df["timestamp"].notna().any():
    df_sorted = df.sort_values("timestamp").reset_index(drop=True)
    df_sorted["call_index"] = range(len(df_sorted))
    df_sorted["end_time"]   = df_sorted["timestamp"] + pd.to_timedelta(df_sorted["duration_seconds"], unit="s")

    fig_tl = px.timeline(
        df_sorted,
        x_start="timestamp", x_end="end_time",
        y="tool_name", color="tool_name",
        hover_data=["duration_seconds", "session_id"],
        color_discrete_map={
            "get_price_data": "#3b82f6", "calculate_volatility": "#ec4899",
            "get_news": "#10b981", "llm_sentiment": "#f59e0b", "web_search": "#8b5cf6",
        },
        template="plotly_white",
        labels={"tool_name": "Tool"},
    )
    fig_tl.update_yaxes(autorange="reversed")
    fig_tl.update_layout(showlegend=False, height=280,
                          margin=dict(l=0, r=0, t=10, b=30))
    st.plotly_chart(fig_tl, use_container_width=True)
else:
    st.info("Timestamps not available for timeline view.")

st.divider()

# ---- Detailed trace table ----
st.subheader("📋 Detailed Trace Log")

for i, row in df.iterrows():
    pill_cls = PILL.get(row["tool_name"], "pill-price")
    status   = "🔴 Error" if row["has_error"] else "✅ OK"
    ts_str   = row["timestamp"].strftime("%H:%M:%S.%f")[:-3] if pd.notna(row["timestamp"]) else "N/A"
    label    = (f"<span class='tool-pill {pill_cls}'>{row['tool_name']}</span>&nbsp;"
                f"<small>{ts_str}</small>&nbsp;"
                f"<small>{row['duration_seconds']:.2f}s</small>&nbsp;"
                f"<small>{status}</small>")
    with st.expander(row["tool_name"] + f"  —  {ts_str}  —  {row['duration_seconds']:.2f}s  {status}"):
        ic, oc = st.columns(2)
        with ic:
            st.markdown("**Inputs**")
            try:
                inp = row["inputs"] if isinstance(row["inputs"], dict) else json.loads(row["inputs"])
                st.json(inp)
            except:
                st.code(str(row["inputs"]))
        with oc:
            st.markdown("**Output (truncated to 200 chars)**")
            raw_out = row["output_truncated"]
            try:
                out_parsed = json.loads(raw_out)
                st.json(out_parsed)
            except:
                st.code(raw_out)
        st.caption(f"Session: `{row['session_id']}`")

st.divider()

# ---- Persistent cache viewer ----
st.subheader("💾 Persistent Research Cache")
cache_files = load_cache_files()
if cache_files:
    for cf in cache_files:
        with st.expander(f"📄 {cf['file']}  |  {cf['ticker']}  |  {cf['date']}"):
            st.caption(cf["report_preview"] + "...")
else:
    st.info("No cache files found. Run the full pipeline to generate them.")

st.divider()

# ---- Session stats ----
st.subheader("📈 Per-Session Statistics")
if df["session_id"].nunique() > 0:
    sess_df = (df.groupby("session_id")
                 .agg(calls=("tool_name","count"),
                      total_time=("duration_seconds","sum"),
                      avg_time=("duration_seconds","mean"),
                      errors=("has_error","sum"))
                 .reset_index()
                 .round(3))
    st.dataframe(sess_df, use_container_width=True)

st.divider()
st.caption("CDAZZDEV-MLE Task 3 | Multi-Agent Financial Research System | Observability Dashboard")
