import copy
import json
import re
from datetime import datetime

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from streamlit_folium import st_folium

# ──────────────────────────────────────────────
# PAGE SETUP
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="ATR Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');

:root {
  --bg: #f6f7fb;
  --surface: rgba(255,255,255,0.88);
  --surface-strong: #ffffff;
  --surface-soft: #fafbff;
  --line: #e7eaf3;
  --text: #142033;
  --muted: #6b7280;
  --primary: #00b894;
  --primary-2: #0ea5a4;
  --primary-3: #2563eb;
  --danger: #ef4444;
  --warning: #f59e0b;
  --success: #10b981;
  --shadow-sm: 0 8px 22px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 16px 40px rgba(15, 23, 42, 0.08);
  --radius: 20px;
}

html, body, [class*="css"] {
  font-family: 'Open Sans', sans-serif !important;
}

.stApp {
  background:
    radial-gradient(circle at top left, rgba(0,184,148,0.10), transparent 26%),
    radial-gradient(circle at top right, rgba(37,99,235,0.08), transparent 24%),
    linear-gradient(180deg, #f8fafc 0%, #f6f7fb 100%);
}

#MainMenu, footer, header {
  visibility: hidden;
}

.block-container {
  max-width: 1500px;
  padding-top: 1.2rem !important;
  padding-bottom: 2rem !important;
}

section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98));
  border-right: 1px solid var(--line);
}

section[data-testid="stSidebar"] .block-container {
  padding-top: 1rem;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 0.5rem;
  background: rgba(255,255,255,0.65);
  border: 1px solid var(--line);
  padding: 0.35rem;
  border-radius: 16px;
}

.stTabs [data-baseweb="tab"] {
  border-radius: 12px;
  padding: 0.7rem 1rem;
  font-weight: 700;
}

.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, rgba(0,184,148,0.12), rgba(37,99,235,0.08));
}

[data-testid="stMetric"] {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: var(--shadow-sm);
}

div[data-testid="stVerticalBlockBorderWrapper"]:has(> div[data-testid="stVerticalBlock"]),
div[data-testid="stExpander"],
div[data-testid="stDataFrame"] {
  border-radius: 20px !important;
}

.stDataFrame, div[data-testid="stAlert"], div[data-testid="stExpander"] {
  border: 1px solid var(--line) !important;
  background: var(--surface) !important;
  box-shadow: var(--shadow-sm) !important;
}

div[data-testid="stSelectbox"], div[data-testid="stMultiSelect"], div[data-testid="stTextInput"] {
  background: transparent;
}

.stButton > button, .stDownloadButton > button {
  border-radius: 14px !important;
  font-weight: 700 !important;
  border: 1px solid var(--line) !important;
  box-shadow: var(--shadow-sm) !important;
}

.hero-shell {
  position: relative;
  overflow: hidden;
  border-radius: 28px;
  padding: 28px 30px;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #111827 0%, #0f766e 55%, #2563eb 100%);
  box-shadow: 0 22px 50px rgba(17, 24, 39, 0.18);
}
.hero-shell::before {
  content: "";
  position: absolute;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  top: -170px;
  right: -70px;
  background: radial-gradient(circle, rgba(255,255,255,0.15), transparent 65%);
}
.hero-shell::after {
  content: "";
  position: absolute;
  width: 260px;
  height: 260px;
  border-radius: 50%;
  bottom: -160px;
  left: 15%;
  background: radial-gradient(circle, rgba(255,255,255,0.11), transparent 65%);
}
.hero-grid {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  position: relative;
  z-index: 2;
}
.hero-title {
  color: #fff;
  font-size: 2rem;
  line-height: 1.1;
  font-weight: 800;
  margin: 0;
  letter-spacing: -0.04em;
}
.hero-sub {
  margin-top: 0.4rem;
  color: rgba(255,255,255,0.75);
  font-size: 0.95rem;
}
.hero-chip-row {
  display: flex;
  gap: 0.7rem;
  flex-wrap: wrap;
  margin-top: 1rem;
}
.hero-chip {
  padding: 0.55rem 0.9rem;
  border-radius: 999px;
  background: rgba(255,255,255,0.12);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.14);
  font-size: 0.82rem;
  font-weight: 700;
  backdrop-filter: blur(10px);
}
.hero-user {
  min-width: 240px;
  text-align: right;
}
.hero-user-card {
  display: inline-flex;
  align-items: center;
  gap: 0.8rem;
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.16);
  border-radius: 18px;
  padding: 0.9rem 1rem;
  color: #fff;
  backdrop-filter: blur(12px);
}
.avatar {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255,255,255,0.18);
  font-size: 1.1rem;
}

.section-kicker {
  margin: 0.3rem 0 0.8rem;
  color: var(--muted);
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.glass-card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 22px;
  box-shadow: var(--shadow-sm);
  padding: 1rem 1rem 0.9rem;
}

.info-card {
  background: linear-gradient(180deg, rgba(255,255,255,0.88), rgba(255,255,255,0.75));
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 18px 18px;
  box-shadow: var(--shadow-sm);
  height: 100%;
}
.info-card h4 {
  margin: 0 0 0.35rem 0;
  font-size: 1rem;
  color: var(--text);
}
.info-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.55;
  font-size: 0.92rem;
}

.links-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.8rem;
}
.link-card {
  background: linear-gradient(180deg, #ffffff, #fbfcff);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 16px 14px;
  box-shadow: var(--shadow-sm);
  transition: transform .15s ease, box-shadow .15s ease;
}
.link-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.link-icon {
  font-size: 1.2rem;
  margin-bottom: 0.35rem;
}
.link-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 800;
}
.link-card a {
  color: var(--text);
  text-decoration: none;
  font-weight: 700;
}
.link-card a:hover {
  color: var(--primary-3);
}
.link-empty {
  opacity: 0.55;
  border-style: dashed;
}

.legend-strip {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 0.65rem;
  color: var(--muted);
  font-size: 0.82rem;
}

.kpi-shell {
  background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(248,250,252,0.88));
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 1rem;
  box-shadow: var(--shadow-sm);
}
.kpi-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.6rem;
}
.kpi-label {
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  font-weight: 800;
}
.kpi-icon {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}
.kpi-value {
  font-size: 2rem;
  line-height: 1;
  color: var(--text);
  font-weight: 800;
  letter-spacing: -0.04em;
  font-family: 'JetBrains Mono', monospace;
}
.kpi-sub {
  margin-top: 0.3rem;
  color: var(--muted);
  font-size: 0.86rem;
}
.kpi-bar {
  margin-top: 0.7rem;
  height: 6px;
  border-radius: 999px;
  background: #edf2f7;
  overflow: hidden;
}
.kpi-fill {
  height: 100%;
  border-radius: 999px;
}

.login-wrap {
  max-width: 480px;
  margin: 10vh auto 0;
}
.login-card {
  background: rgba(255,255,255,0.9);
  border: 1px solid var(--line);
  border-radius: 28px;
  padding: 26px;
  box-shadow: var(--shadow-md);
}
.login-badge {
  width: 72px;
  height: 72px;
  border-radius: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f766e, #2563eb);
  color: white;
  font-size: 1.8rem;
  margin-bottom: 1rem;
}

.update-day {
  border-left: 3px solid #dbe4f3;
  padding: 0.2rem 0 0.2rem 1rem;
  margin: 0.8rem 0;
}
.update-date {
  color: #0f766e;
  font-weight: 800;
  margin-bottom: 0.35rem;
}
.update-item {
  color: var(--text);
  margin: 0.3rem 0;
}

@media (max-width: 1100px) {
  .links-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hero-grid { flex-direction: column; }
  .hero-user { text-align: left; }
}

@media (max-width: 640px) {
  .links-grid { grid-template-columns: 1fr; }
}
</style>
""",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# DATA LOADING
# ──────────────────────────────────────────────
csv_url = st.secrets["CSV_URL_MAIN"]
csv_url_tools = st.secrets["CSV_URL_TOOLS"]
csv_url_users = st.secrets["CSV_URL_USERS"]


@st.cache_data(ttl=120)
def load_data():
    return (
        pd.read_csv(csv_url),
        pd.read_csv(csv_url_tools),
        pd.read_csv(csv_url_users),
    )


def convert_df_to_csv(dataframe: pd.DataFrame):
    return dataframe.to_csv(index=False, encoding="utf-8")


def to_dt(series_or_val):
    return pd.to_datetime(series_or_val, dayfirst=True, errors="coerce")


def safe_read_csv(url_or_path, **kwargs):
    try:
        return pd.read_csv(url_or_path, **kwargs)
    except Exception:
        return pd.DataFrame()


def safe_value(row, key, default=""):
    if key in row:
        value = row[key]
        if pd.isna(value):
            return default
        return value
    return default


def render_section_label(text: str):
    st.markdown(f"<div class='section-kicker'>{text}</div>", unsafe_allow_html=True)


def render_info_card(title: str, body: str):
    st.markdown(
        f"<div class='info-card'><h4>{title}</h4><p>{body}</p></div>",
        unsafe_allow_html=True,
    )


def render_kpi_card(label, value, sub, icon, icon_bg, fill_pct=None, fill_bg=None):
    fill = ""
    if fill_pct is not None and fill_bg:
        fill = (
            f"<div class='kpi-bar'><div class='kpi-fill' style='width:{max(0, min(100, fill_pct))}%;"
            f"background:{fill_bg};'></div></div>"
        )
    st.markdown(
        f"""
        <div class="kpi-shell">
            <div class="kpi-top">
                <div class="kpi-label">{label}</div>
                <div class="kpi-icon" style="background:{icon_bg}">{icon}</div>
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-sub">{sub}</div>
            {fill}
        </div>
        """,
        unsafe_allow_html=True,
    )


def generate_roadmap_html(steps, current_step_label):
    processed_steps = []
    try:
        current_index = [s["label"] for s in steps].index(current_step_label)
    except ValueError:
        current_index = -1

    for i, step in enumerate(steps):
        if current_index == -1:
            status = "upcoming"
        elif i < current_index:
            status = "completed"
        elif i == current_index:
            status = "ongoing"
        else:
            status = "upcoming"
        processed_steps.append({"label": step["label"], "status": status})

    num_steps = len(processed_steps)
    completed_steps = sum(1 for s in processed_steps if s["status"] == "completed")
    progress_pct = (completed_steps / (num_steps - 1)) * 100 if num_steps > 1 else 0
    nodes_html = ""

    for step in processed_steps:
        s = step["status"]
        if s == "completed":
            inner = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><path d="M5 13l4 4L19 7"/></svg>'
            ring_bg, ring_border, txt_color, txt_weight, size = "#00b894", "#00b894", "#0f766e", "700", "30px"
        elif s == "ongoing":
            inner = '<div style="width:10px;height:10px;background:#fff;border-radius:50%;animation:pulse-dot 2s ease infinite;"></div>'
            ring_bg, ring_border, txt_color, txt_weight, size = "#1e293b", "#1e293b", "#1e293b", "800", "36px"
        else:
            inner = '<div style="width:7px;height:7px;background:#cbd5e1;border-radius:50%;"></div>'
            ring_bg, ring_border, txt_color, txt_weight, size = "#ffffff", "#dbe4f3", "#94a3b8", "600", "28px"
        shadow = "box-shadow:0 0 0 5px rgba(37,99,235,0.10);" if s == "ongoing" else ""
        nodes_html += f"""
        <div style="display:flex;flex-direction:column;align-items:center;width:{100/num_steps}%;">
            <div style="width:{size};height:{size};border-radius:999px;background:{ring_bg};border:2px solid {ring_border};
                 display:flex;align-items:center;justify-content:center;z-index:2;{shadow}">{inner}</div>
            <div style="margin-top:18px;font-size:10px;font-weight:{txt_weight};color:{txt_color};width:86px;text-align:center;line-height:1.3;">{step['label']}</div>
        </div>
        """

    return f"""
    <style>@keyframes pulse-dot{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.6);opacity:.55}}}}</style>
    <div style="max-width:100%;margin:0 auto;padding:8px 8px 12px;">
        <div style="position:relative;width:100%;padding-top:14px;">
            <div style="position:absolute;top:30px;width:100%;height:5px;background:#eaf0f7;border-radius:999px;"></div>
            <div style="position:absolute;top:30px;width:calc({progress_pct}%);height:5px;background:linear-gradient(90deg,#00b894,#2563eb);border-radius:999px;"></div>
            <div style="position:relative;display:flex;justify-content:space-between;align-items:flex-start;width:100%;">{nodes_html}</div>
        </div>
    </div>
    """


def parse_log(log_text):
    log_text = log_text if isinstance(log_text, str) else ""
    parts = [p.strip() for p in re.split(r";;\s*", log_text.strip()) if p.strip()]
    rows = []
    for p in parts:
        if ":" not in p:
            continue
        ds, msg = p.split(":", 1)
        try:
            d = datetime.strptime(ds.strip(), "%d/%m/%Y").date()
            rows.append((d, msg.strip()))
        except ValueError:
            continue
    rows.sort(key=lambda x: x[0])
    return rows


def make_donut(labels, values, title, colors, note=""):
    total = sum(values)
    pct = round(100 * values[0] / total) if total else 0
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.78,
            textinfo="percent",
            textfont=dict(size=11, color="#64748b", family="Open Sans"),
            marker=dict(
                colors=colors[: len(values)],
                line=dict(color="rgba(246,247,251,1)", width=4),
            ),
            pull=[0.03] + [0] * max(0, len(values) - 1),
            hovertemplate="<b>%{label}</b>: %{percent}<extra></extra>",
            showlegend=True,
            sort=False,
        )
    )
    fig.update_layout(
        title=dict(text=title, x=0.5, xanchor="center", font=dict(size=14, color="#0f172a")),
        height=300,
        margin=dict(l=0, r=0, t=48, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=11, color="#64748b")),
        annotations=[
            dict(
                text=(
                    f"<b style='font-size:28px;color:#0f172a;font-family:JetBrains Mono'>{pct}%</b>"
                    f"<br><span style='font-size:10px;color:#94a3b8'>{note}</span>"
                ),
                x=0.5,
                y=0.5,
                showarrow=False,
            )
        ],
    )
    return fig


def build_submission_timeline(dff):
    fig_timeline = px.area(dff, x="Date", y="N")
    fig_timeline.update_traces(
        line=dict(color="#00b894", width=2.5),
        fillcolor="rgba(0,184,148,0.10)",
        mode="lines+markers",
        marker=dict(color="#00b894", size=5, line=dict(width=2, color="rgba(255,255,255,0.9)")),
    )
    fig_timeline.update_layout(
        xaxis_title="",
        yaxis_title="Submissions",
        template="plotly_white",
        height=340,
        margin=dict(l=30, r=16, t=10, b=20),
        font=dict(family="Open Sans"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="rgba(0,0,0,0.03)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0.06)"),
    )
    return fig_timeline


@st.cache_data(show_spinner=False)
def load_geojson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_map(geo_raw, counts_df):
    geo = copy.deepcopy(geo_raw)
    count_map = dict(zip(counts_df["Province"], counts_df["count"]))
    for feat in geo["features"]:
        name = feat["properties"].get("NAME_1")
        feat["properties"]["VISITS"] = int(count_map.get(name, 0))

    m = folium.Map(location=[34.5, 66.0], zoom_start=5, tiles="CartoDB positron")
    folium.Choropleth(
        geo_data=geo,
        data=counts_df,
        columns=["Province", "count"],
        key_on="feature.properties.NAME_1",
        fill_color="YlGnBu",
        fill_opacity=0.82,
        line_opacity=0.25,
        nan_fill_color="#edf2f7",
        nan_fill_opacity=0.65,
        legend_name="Visits",
    ).add_to(m)
    folium.GeoJson(
        geo,
        style_function=lambda f: {"color": "#64748b", "weight": 0.8, "fillOpacity": 0},
        highlight_function=lambda f: {"color": "#0f172a", "weight": 2},
        tooltip=folium.GeoJsonTooltip(fields=["NAME_1", "VISITS"], aliases=["Province:", "Visits:"], sticky=True),
    ).add_to(m)
    return m


def build_project_timeline(project_data):
    phases = [
        ("DC", "Planned Data Collection-Start", "Planned Data Collection-End", "Data Collection-Start", "Data Collection-End"),
        ("QA", "Planned data QA-Start", "Planned data QA-End", "data QA-Start", "data QA-End"),
        ("DM", "Planned DM-Start", "Planned DM-End", "DM-Start", "DM-End"),
        ("A&R", "Planned Reporting-Start", "Planned Reporting-End", "Reporting-Start", "Reporting-End"),
    ]
    planned_color = "rgba(100,116,139,0.50)"
    actual_color = "rgba(37,99,235,0.28)"
    running_color = "rgba(37,99,235,0.48)"
    current_planned_color = "rgba(0,184,148,1.0)"
    current_actual_color = "rgba(0,184,148,0.45)"
    ontime_color = "#10b981"
    delay_color = "#ef4444"
    planned_w = 3
    actual_w = 10
    gap = 1.05
    today = pd.Timestamp.today().normalize()

    for _, ps, pe, a_s, a_e in phases:
        for c in (ps, pe, a_s, a_e):
            if c in project_data.columns:
                project_data[c] = to_dt(project_data[c])

    fig = go.Figure()
    y_vals, y_labels = [], []
    y = 0

    def delay_days(plan_end, actual_end):
        if pd.notna(plan_end) and pd.notna(actual_end):
            d = (actual_end - plan_end).days
            return d if d > 0 else 0
        return 0

    for _, row in project_data.iterrows():
        project = str(row.get("Project Name", "—"))
        responsible = str(row.get("Responsible", "") or "").strip().lower()
        project_y = []
        for phase, ps_c, pe_c, as_c, ae_c in phases:
            ps, pe = row.get(ps_c), row.get(pe_c)
            a_s, a_e = row.get(as_c), row.get(ae_c)
            if pd.isna(ps) or pd.isna(pe):
                continue
            is_current = bool(responsible) and phase.lower() in responsible
            y_vals.append(y)
            y_labels.append(f"{project} — {phase}")
            project_y.append(y)
            pc = current_planned_color if is_current else planned_color
            fig.add_trace(
                go.Scatter(
                    x=[ps, pe],
                    y=[y, y],
                    mode="lines",
                    line=dict(color=pc, width=planned_w, dash="dash"),
                    showlegend=False,
                    hovertemplate=f"<b>{project}</b><br>{phase}<br>Planned: {ps:%d-%b-%Y} → {pe:%d-%b-%Y}<extra></extra>",
                )
            )
            if pd.notna(a_s):
                is_running = pd.isna(a_e)
                actual_end = a_e if pd.notna(a_e) else today
                ac = current_actual_color if is_current else (running_color if is_running else actual_color)
                fig.add_trace(
                    go.Scatter(
                        x=[a_s, actual_end],
                        y=[y, y],
                        mode="lines",
                        line=dict(color=ac, width=actual_w),
                        showlegend=False,
                        hovertemplate=f"<b>{project}</b><br>{phase}<br>Actual: {a_s:%d-%b-%Y} → {actual_end:%d-%b-%Y}{' (running)' if is_running else ''}<extra></extra>",
                    )
                )
                if is_running:
                    fig.add_annotation(
                        x=actual_end,
                        y=y,
                        text="<b>↝</b>",
                        showarrow=False,
                        xanchor="left",
                        yanchor="middle",
                        font=dict(size=22, color="#00b894"),
                        bgcolor="rgba(255,255,255,0.7)",
                    )
                if not is_running:
                    d = delay_days(pe, a_e)
                    if d > 0:
                        fig.add_trace(
                            go.Scatter(
                                x=[a_e],
                                y=[y],
                                mode="markers+text",
                                marker=dict(size=8, color=delay_color),
                                text=[f"+{d}d"],
                                textposition="top center",
                                textfont=dict(size=9, color=delay_color),
                                showlegend=False,
                            )
                        )
                    else:
                        fig.add_annotation(
                            x=a_e,
                            y=y,
                            text="<b>✓</b>",
                            showarrow=False,
                            font=dict(size=16, color=ontime_color),
                            xshift=8,
                        )
            y += 1
        if project_y and responsible:
            fig.add_annotation(
                xref="paper",
                x=0.92,
                xanchor="left",
                y=sum(project_y) / len(project_y),
                yanchor="middle",
                text=f"<span style='color:#0f766e;font-size:12px;font-weight:700'>{row.get('Responsible')}</span>",
                showarrow=False,
            )
        y += gap

    min_start = project_data[[ps_c for _, ps_c, _, _, _ in phases if ps_c in project_data.columns]].min().min()
    max_date = max(
        project_data[pe_c].max() if pe_c in project_data.columns else pd.Timestamp.today() for _, _, pe_c, _, _ in phases
    )

    fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.35)
    fig.add_annotation(
        x=today,
        y=0.99,
        xref="x",
        yref="paper",
        text="<b><i>Today</i></b>",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=12, color="#0f766e"),
    )
    fig.update_yaxes(tickmode="array", tickvals=y_vals, ticktext=y_labels, autorange="reversed", title="")
    fig.update_xaxes(
        range=[min_start, max_date + pd.Timedelta(days=20)],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.03)",
        zeroline=False,
    )
    fig.update_layout(
        height=max(420, 24 * len(y_vals)),
        margin=dict(l=95, r=80, t=10, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        hovermode="closest",
        font=dict(family="Open Sans"),
    )
    return fig


def build_surveyor_report_html(project_name, meta, summary_df, issues_df, chart_src_json):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    issues_df, summary_df = issues_df.copy(), summary_df.copy()
    for c in ["Site_Visit_ID", "Location"]:
        if c not in issues_df.columns:
            issues_df[c] = ""
    total_issues = len(issues_df)
    resolved_count = int((issues_df.get("issue_resolved") == "Yes").sum()) if total_issues else 0
    pending_count = total_issues - resolved_count
    notified_count = int((issues_df.get("surveyor_notified") == "Yes").sum()) if total_issues else 0
    not_notified_count = int(issues_df["surveyor_response"].fillna("").eq("").sum()) if total_issues else 0
    high_severity = int((issues_df.get("severity") == "High").sum()) if total_issues else 0
    avg_score = float(summary_df["score"].mean()) if len(summary_df) else 0.0
    matrix_df = summary_df.sort_values("score", ascending=True).head(10)
    matrix_rows = "".join(
        f"""
        <tr>
            <td><div class="name">{r.Surveyor_Name}</div><div class="muted">ID: SURV-{abs(hash(r.Surveyor_Name)) % 1000}</div></td>
            <td class="c"><div class="score">{r.score}</div><div class="bar"><span style="width:{r.score}%;background:{r.band_color}"></span></div></td>
            <td><span class="pill" style="background:{r.band_color}">{r.band}</span></td>
            <td class="c mono">{int(r.total_submissions)}</td>
            <td class="c mono">{int(r.rejected_count)}</td>
            <td class="c mono red">{(r.rejection_ratio*100):.1f}%</td>
            <td class="c mono blue">{(r.total_feedback_ratio*100):.1f}%</td>
            <td class="c mono blue">{(r.hfc_outliers_ratio*100):.1f}%</td>
            <td class="c mono">{(float(getattr(r, 'ta_outliers', 0.0))*100):.1f}%</td>
            <td class="rec">{r.recommendation}</td>
        </tr>
        """
        for r in matrix_df.itertuples(index=False)
    )
    issues_json = issues_df.to_json(orient="records")
    return f"""<!doctype html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{project_name} - QA Report</title><script src="https://cdn.jsdelivr.net/npm/chart.js"></script><style>@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;500;600;700;800&display=swap');:root{{--bg:#f4f6fb;--card:#fff;--text:#132033;--muted:#6b7280;--line:#e7eaf3;--issue-bg:#fff7ed;--issue-bd:#fed7aa;--issue-date:#9a3412;--issue-txt:#7c2d12;--resp-bg:#f0fdfa;--resp-bd:#99f6e4;--resp-date:#0f766e;--resp-txt:#334155;}}*{{box-sizing:border-box}}body{{margin:0;font-family:'Open Sans',system-ui,sans-serif;background:var(--bg);color:var(--text)}}.wrap{{max-width:1120px;margin:0 auto;padding:18px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:18px}}.top{{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;background:linear-gradient(135deg,#111827 0%,#0f766e 55%,#2563eb 100%);color:#fff;border:none;box-shadow:0 20px 50px rgba(17,24,39,.18)}}.top .muted{{color:rgba(255,255,255,.72);}}.badge{{display:inline-block;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,0.15);color:#fff;font-size:11px;font-weight:800}}.muted{{color:var(--muted);font-size:12px}}h1{{margin:8px 0 2px;font-size:28px;line-height:1.08}}.btn{{border:0;border-radius:14px;padding:12px 14px;background:#00b894;color:#fff;font-weight:800;cursor:pointer;font-family:'Open Sans'}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:12px}}.kpi .label{{font-size:11px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}}.kpi .val{{font-size:28px;font-weight:900;margin-top:6px;font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}.bar{{height:7px;background:#eef2f7;border-radius:999px;overflow:hidden;margin-top:8px}}.bar span{{display:block;height:100%}}.tablecard{{margin-top:12px;padding:0;overflow:hidden}}.thead{{padding:14px 18px;border-bottom:1px solid var(--line);background:#fafbff}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px 14px;border-bottom:1px solid #f1f5f9;vertical-align:top;font-size:13px}}th{{text-align:left;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;background:#fafbff}}.c{{text-align:center}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}.name{{font-weight:900}}.score{{font-weight:900}}.pill{{display:inline-block;padding:4px 8px;border-radius:999px;color:#fff;font-size:11px;font-weight:900}}.rec{{color:var(--muted);font-style:italic;font-size:12px}}.red{{color:#dc2626}}.blue{{color:#2563eb}}.filters{{display:grid;grid-template-columns:1fr 180px 220px 140px;gap:10px;margin-top:12px}}input,select{{padding:10px 12px;border:1px solid var(--line);border-radius:12px;font-size:13px;background:#fff;font-family:'Open Sans'}}.ghost{{background:#f1f5f9;color:#132033}}.ticker tbody tr{{border-bottom:1px dashed #e5e7eb}}.ticker tbody tr:last-child{{border-bottom:none}}.ticker tbody tr td{{padding-top:18px;padding-bottom:18px}}.comment{{margin-top:8px;padding:10px 12px;border-radius:12px;border:1px solid;}}.comment-date{{font-weight:900;font-size:12px}}.comment-body{{margin-top:4px;line-height:1.35;}}.comment-divider{{height:1px;margin:10px 2px;background:linear-gradient(90deg,rgba(148,163,184,0),rgba(148,163,184,.85),rgba(148,163,184,0))}}.issue-comments .comment{{background:var(--issue-bg);border-color:var(--issue-bd);border-left:4px solid #fb923c;}}.issue-comments .comment-date{{color:var(--issue-date);}}.issue-comments .comment-body{{color:var(--issue-txt);}}.response-comments .comment{{background:var(--resp-bg);border-color:var(--resp-bd);border-left:4px solid #14b8a6;}}.response-comments .comment-date{{color:var(--resp-date);}}.response-comments .comment-body{{color:var(--resp-txt);font-style:italic;}}.awaiting-response{{color:#b91c1c;opacity:.45;font-style:italic;font-weight:300;}}.charts-row{{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;padding:18px;margin-top:4px;}}.chart-box{{background:#ffffff;border:1px solid var(--line);border-radius:16px;padding:16px;position:relative;}}.chart-box canvas{{width:100%!important;}}@media print{{.no-print{{display:none!important}}body{{background:#fff}}.wrap{{padding:0}}.card{{border:0;box-shadow:none}}}}@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}.filters{{grid-template-columns:1fr}}.charts-row{{grid-template-columns:1fr}}}}</style></head><body><div class="wrap"><div class="card top"><div><span class="badge">{meta}</span><span class="muted" style="margin-left:10px">Report Generated: {now}</span><h1>{project_name}</h1><div class="muted">Surveyor Quality Matrix + Detailed Feedback Log</div></div><button class="btn no-print" onclick="window.print()">Export PDF</button></div><div class="grid"><div class="card kpi"><div class="label">Overall Quality Score</div><div class="val">{avg_score:.1f} <span class="muted">/ 100</span></div><div class="bar"><span style="width:{avg_score}%;background:#00b894"></span></div></div><div class="card kpi"><div class="label">Total Recorded Cases</div><div class="val" style="color:#4f46e5">{total_issues}</div><div class="muted">{resolved_count} Resolved • {pending_count} Open</div></div><div class="card kpi"><div class="label">Surveyor Notifications</div><div class="val">{notified_count}</div><div class="muted">Awaiting responses for {not_notified_count} cases.</div></div><div class="card kpi"><div class="label">Critical (High severity)</div><div class="val" style="color:#dc2626">{high_severity}</div><div class="muted">Immediate coaching required</div></div></div><div class="card tablecard"><div class="thead"><div style="font-weight:900">Surveyor Performance Matrix (Worst 10)</div><div class="muted">Lowest quality score surveyors</div></div><div style="overflow:auto"><table><thead><tr><th>Surveyor</th><th class="c">Score</th><th>Band</th><th class="c">Total Subs</th><th class="c">Rej #</th><th class="c">Rej %</th><th class="c">Feedback %</th><th class="c">Data incons. %</th><th class="c">Speed Vio. %</th><th>Action</th></tr></thead><tbody>{matrix_rows}</tbody></table></div></div><div class="card tablecard" style="margin-top:12px"><div class="thead"><div style="font-weight:900;text-align:center">Detailed Feedback Log</div><div class="filters no-print"><input id="q" placeholder="Search logs..."/><select id="fResolved"><option value="">Status: All</option><option value="Yes">Resolved</option><option value="No">Pending</option></select><select id="fSurveyor"><option value="">Surveyor: All</option></select><button class="btn ghost" id="reset" type="button">Clear</button></div></div><div class="charts-row"><div class="chart-box"><canvas id="trendChart"></canvas></div><div class="chart-box"><canvas id="issueTypeChart"></canvas></div></div><div style="overflow:auto"><table class="ticker"><thead><tr><th>Verification Detail</th><th>Surveyor Response</th><th class="c">Severity</th><th class="c">Status</th></tr></thead><tbody id="tbody"></tbody></table></div></div></div><script>const data={issues_json};const chartSource={chart_src_json};const tbody=document.getElementById('tbody');const sSelect=document.getElementById('fSurveyor');const uniq=Array.from(new Set(data.map(x=>x.Surveyor_Name))).filter(Boolean).sort();for(const s of uniq){{const o=document.createElement('option');o.value=s;o.textContent=s;sSelect.appendChild(o);}}function esc(x){{return String(x??'').replace(/[&<>"']/g,m=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}})[m]);}}function formatComments(raw){{const s=String(raw??'').trim();if(!s)return'';const re=/\[(\d{{1,2}}\/\d{{1,2}}\/\d{{4}})\]\s*:?:?\s*/g;let match,lastIndex=0,lastDate=null;const blocks=[];while((match=re.exec(s))!==null){{if(lastDate!==null)blocks.push({{date:lastDate,body:s.slice(lastIndex,match.index).trim()}});lastDate=match[1];lastIndex=re.lastIndex;}}if(lastDate!==null)blocks.push({{date:lastDate,body:s.slice(lastIndex).trim()}});if(!blocks.length)return esc(s);let html='';for(let i=0;i<blocks.length;i++){{if(i>0)html+='<div class="comment-divider"></div>';html+=`<div class="comment"><div class="comment-date">[${{esc(blocks[i].date)}}]</div><div class="comment-body">${{esc(blocks[i].body)}}</div></div>`;}}return html;}}const barColors=['#00b894','#f59e0b','#ef4444','#10b981','#3b82f6','#ec4899','#8b5cf6','#14b8a6','#f97316','#64748b'];const trendCtx=document.getElementById('trendChart').getContext('2d');const trendChart=new Chart(trendCtx,{{type:'line',data:{{labels:[],datasets:[{{label:'Total',data:[],borderColor:'#00b894',backgroundColor:'rgba(0,184,148,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#00b894'}},{{label:'Rejected',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#ef4444'}}]}},options:{{responsive:true,maintainAspectRatio:true,plugins:{{title:{{display:true,text:'Daily Submissions',font:{{size:14,weight:'900',family:'Open Sans'}}}},legend:{{position:'top',labels:{{usePointStyle:true,pointStyle:'circle',padding:14,font:{{size:11,weight:'700'}}}}}}}},scales:{{x:{{ticks:{{maxRotation:45,font:{{size:9}},maxTicksLimit:15}},grid:{{display:false}}}},y:{{beginAtZero:true,grid:{{color:'#f1f5f9'}}}}}}}});const typeCtx=document.getElementById('issueTypeChart').getContext('2d');const issueTypeChart=new Chart(typeCtx,{{type:'bar',data:{{labels:[],datasets:[{{label:'Count',data:[],backgroundColor:[],borderColor:[],borderWidth:1.5,borderRadius:6,barPercentage:0.7}}]}},options:{{responsive:true,maintainAspectRatio:true,indexAxis:'y',plugins:{{title:{{display:true,text:'Issues by Type',font:{{size:14,weight:'900',family:'Open Sans'}}}},legend:{{display:false}}}},scales:{{x:{{beginAtZero:true,grid:{{color:'#f1f5f9'}},ticks:{{stepSize:1}}}},y:{{ticks:{{font:{{size:11,weight:'600'}}}},grid:{{display:false}}}}}}}});function updateCharts(sf,qf,rf){{let f=chartSource;if(sf)f=f.filter(r=>r.Surveyor_Name===sf);if(rf)f=f.filter(r=>r.issue_resolved===rf);if(qf){{const q=qf.toLowerCase();f=f.filter(r=>((r.Surveyor_Name||'')+' '+(r.KEY||'')+' '+(r.Issue_Type||'')+' '+(r.Issue_Description||'')).toLowerCase().includes(q));}}const dm={{}};for(const r of f){{if(!r.Date)continue;if(!dm[r.Date])dm[r.Date]={{t:0,r:0}};dm[r.Date].t+=1;if(r.QA_Status==='Rejected')dm[r.Date].r+=1;}}const sd=Object.keys(dm).sort();trendChart.data.labels=sd;trendChart.data.datasets[0].data=sd.map(d=>dm[d].t);trendChart.data.datasets[1].data=sd.map(d=>dm[d].r);trendChart.update();const tm={{}};for(const r of f){{if(!r.Issue_Type)continue;tm[r.Issue_Type]=(tm[r.Issue_Type]||0)+1;}}const st=Object.entries(tm).sort((a,b)=>b[1]-a[1]);issueTypeChart.data.labels=st.map(e=>e[0]);issueTypeChart.data.datasets[0].data=st.map(e=>e[1]);issueTypeChart.data.datasets[0].backgroundColor=st.map((_,i)=>barColors[i%barColors.length]+'cc');issueTypeChart.data.datasets[0].borderColor=st.map((_,i)=>barColors[i%barColors.length]);issueTypeChart.update();}}function render(){{const q=document.getElementById('q').value.toLowerCase();const res=document.getElementById('fResolved').value;const sur=document.getElementById('fSurveyor').value;updateCharts(sur,q,res);const out=[];for(const i of data){{if(res&&i.issue_resolved!==res)continue;if(sur&&i.Surveyor_Name!==sur)continue;if(q){{const blob=((i.Surveyor_Name||'')+' '+(i.KEY||'')+' '+(i.Issue_Type||'')+' '+(i.Issue_Description||'')).toLowerCase();if(!blob.includes(q))continue;}}out.push(`<tr><td><div class="muted" style="font-weight:900;text-transform:uppercase;color:#0f766e">${{esc(i.Surveyor_Name)}}</div><div class="muted">KEY: ${{esc(i.KEY)}}</div><div class="muted">Location: ${{esc(i.Location)}}</div><div style="font-weight:700;margin-top:8px">Issue: <span style="font-weight:400;text-decoration:underline">${{esc(i.Issue_Type)}}</span></div><div class="muted">QA: <span style="font-weight:900;color:${{i.QA_Status==='Rejected'?'#ef4444':'#10b981'}}">${{esc(i.QA_Status)}}</span></div><div class="muted" style="margin-top:8px"><span style="color:#dc2626;font-weight:900">ISSUE:</span><div class="issue-comments">${{formatComments(i.Issue_Description)}}</div></div></td><td><div class="response-comments">${{i.surveyor_response?formatComments(i.surveyor_response):'<div class="awaiting-response">Awaiting response...</div>'}}</div></td><td class="c"><span class="pill" style="background:#e2e8f0;color:#0f172a">${{esc(i.severity)}}</span></td><td class="c"><span class="pill" style="background:${{i.issue_resolved==='Yes'?'#dcfce7':'#ffe4e6'}};color:${{i.issue_resolved==='Yes'?'#166534':'#9f1239'}}">${{i.issue_resolved==='Yes'?'Closed':'Pending'}}</span></td></tr>`);}}tbody.innerHTML=out.join('');}}document.getElementById('q').addEventListener('input',render);document.getElementById('fResolved').addEventListener('input',render);document.getElementById('fSurveyor').addEventListener('input',render);document.getElementById('reset').addEventListener('click',()=>{{document.getElementById('q').value='';document.getElementById('fResolved').value='';document.getElementById('fSurveyor').value='';render();}});render();</script></body></html>"""


def score_surveyors(df_s, w_rej=0.5, w_out=0.10, w_out2=0.2, w_fb=0.2):
    df_s = df_s.copy()
    score = 100 - (
        df_s["rejection_ratio"] * 100 * w_rej
        + df_s["hfc_outliers_ratio"] * 100 * w_out
        + df_s["ta_outliers"] * 100 * w_out2
        + df_s["total_feedback_ratio"] * 100 * w_fb
    )
    df_s["score"] = score.round(1).clip(0, 100)
    conds = [df_s["score"] >= 85, df_s["score"] >= 70, df_s["score"] >= 55]
    df_s["band"] = np.select(conds, ["Excellent", "Good", "Watch"], default="Critical")
    df_s["band_color"] = np.select(conds, ["#10b981", "#3b82f6", "#f59e0b"], default="#ef4444")
    df_s["recommendation"] = np.select(
        conds,
        ["Maintain monitoring", "Minor coaching", "Verify records"],
        default="Urgent Retraining",
    )
    return df_s


# ──────────────────────────────────────────────
# LOAD CORE DATA
# ──────────────────────────────────────────────
df, df_tools, df_users = load_data()
user_dict = df_users.set_index("users")[["password", "project"]].to_dict(orient="index")

# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div class='login-wrap'>", unsafe_allow_html=True)
    with st.container():
        st.markdown(
            """
            <div class="login-card">
                <div class="login-badge">📊</div>
                <div style="font-size:2rem;font-weight:800;color:#142033;letter-spacing:-0.04em;">ATR Consulting</div>
                <div style="margin-top:0.35rem;color:#6b7280;line-height:1.6;">A redesigned data operations dashboard for collection progress, QA tracking, sample monitoring, and reporting.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)
    st.markdown(
        """
        <div class="info-card" style="margin-top:14px;">
            <h4>What changed</h4>
            <p>The dashboard has been reorganized into a cleaner executive layout with stronger hierarchy, premium cards, clearer filters, and more polished chart presentation.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        if username in user_dict and password == user_dict[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Incorrect username or password.")
    st.stop()

# ──────────────────────────────────────────────
# MAIN APP
# ──────────────────────────────────────────────
username = st.session_state.username
allowed_projects = user_dict[username]["project"].split(",")
if allowed_projects[0] == "All":
    main_project_names = sorted(df["Main Project"].dropna().unique())
else:
    main_project_names = sorted(df[df["Main Project"].isin(allowed_projects)]["Main Project"].dropna().unique())

with st.sidebar:
    st.markdown("### ATR Dashboard")
    st.caption("Premium redesign for cleaner navigation and reporting.")
    main_project = st.selectbox("Main project", main_project_names, key="main_project")
    project_names = sorted(df[df["Main Project"] == main_project]["Project Name"].dropna().unique())
    selected_project = st.selectbox("Sub-project / round", project_names, key="sub_project")
    st.divider()
    st.markdown("**Session**")
    st.caption(f"Signed in as **{username}**")
    if st.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

project_rows_main = df[df["Main Project"] == main_project].reset_index(drop=True).copy()
project_data = df[df["Project Name"] == selected_project].reset_index(drop=True).copy()
project_data_tools = df_tools[df_tools["Project Name"] == selected_project].reset_index(drop=True).copy()
if project_data.empty:
    st.error("No project data found for the selected sub-project.")
    st.stop()

proj_completed = safe_value(project_data.loc[0], "Completed", "No")
current_step = safe_value(project_data.loc[0], "current_step", "")
QA_records_link = safe_value(project_data.loc[0], "QA-Notes link", "")

st.markdown(
    f"""
    <div class="hero-shell">
        <div class="hero-grid">
            <div>
                <div class="hero-title">Data Collection & QA Dashboard</div>
                <div class="hero-sub">ATR Consulting • redesigned operational cockpit for field progress, QA status, and sample completion</div>
                <div class="hero-chip-row">
                    <div class="hero-chip">Main Project: {main_project}</div>
                    <div class="hero-chip">Sub-project: {selected_project}</div>
                    <div class="hero-chip">Status: {'Archived' if proj_completed == 'Yes' else 'Active'}</div>
                </div>
            </div>
            <div class="hero-user">
                <div class="hero-user-card">
                    <div class="avatar">👤</div>
                    <div>
                        <div style="font-size:0.78rem;opacity:.78;">Logged in</div>
                        <div style="font-size:1rem;font-weight:800;">{username}</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.toast("Use the sidebar to switch projects and sub-projects. Filters update the charts and summaries below.")

# Default vars
raw_def_var = str(safe_value(project_data.loc[0], "Summary_defualt_var", "-") or "-")
if raw_def_var.strip() == "-":
    def_var0, def_var1, def_var2 = [], [], []
else:
    parts = raw_def_var.split(";")
    def_var0 = [item.strip() for item in parts[0].split(",") if item.strip()] if len(parts) > 0 else []
    def_var1 = [item.strip() for item in parts[1].split(",") if item.strip()] if len(parts) > 1 else []
    def_var2 = [item.strip() for item in parts[2].split(",") if item.strip()] if len(parts) > 2 else []

# Links
links_row = project_data[["Tool link", "XLSForm link", "QA-Notes link", "Tracker link", "DC Tracker", "Document folder link"]].iloc[0]
link_labels = {
    "Tool link": ("🛠️", "Tool"),
    "XLSForm link": ("📋", "XLSForm"),
    "QA-Notes link": ("🧪", "QA Notes"),
    "Tracker link": ("📈", "QA Tracker"),
    "DC Tracker": ("🗂️", "DC Tracker"),
    "Document folder link": ("📁", "Document Folder"),
}

# Roadmap steps
steps_data = [
    {"label": "Form Coding (XLSForm)"},
    {"label": "Training"},
    {"label": "QA-Manual Checks"},
    {"label": "QA-Automated Checks"},
    {"label": "QA-Dataset Finalization"},
    {"label": "DM-Dataset Finalization"},
    {"label": "QA Report"},
    {"label": "QA Completion"},
]

# ──────────────────────────────────────────────
# LOAD OPERATIONAL DATA
# ──────────────────────────────────────────────
missing = pd.DataFrame(columns=["Tool", "V_ID", "KEY", "Type", "QA_Status"])
rawsheet = safe_value(project_data.loc[0], "raw_sheet", "")
Project_QA_ID = safe_value(project_data.loc[0], "Sampling_ID", "")
Project_QA_ID2 = safe_value(project_data.loc[0], "QAlog_ID", "")
Project_QA_ID3 = safe_value(project_data.loc[0], "HFC_ID", "")
extra_code = safe_value(project_data.loc[0], "extra_code", "-")

raw_sheet_id = ""
if isinstance(rawsheet, str) and "/d/" in rawsheet:
    raw_sheet_id = rawsheet.split("/d/")[1].split("/")[0]

csv_url_raw = (
    f"https://docs.google.com/spreadsheets/d/{raw_sheet_id}/export?format=csv&id={raw_sheet_id}&gid=0"
    if raw_sheet_id
    else ""
)

qasheet = (
    "https://docs.google.com/spreadsheets/d/1V1SfBZUwHN0NtXFIoiXEh7JGkpTUOLZnGAfFN8QVXYQ/export?format=csv&" + str(Project_QA_ID2)
    if Project_QA_ID2
    else ""
)

samplingsheet = (
    "https://docs.google.com/spreadsheets/d/1U0Y7TQnTFEg1edMb0IHejOxv9S2YLY2UH-tp1qzXyBg/export?format=csv&" + str(Project_QA_ID)
    if Project_QA_ID
    else ""
)

hfcsheet = (
    "https://docs.google.com/spreadsheets/d/16EWCV7HTEx729ILvsYa72LkJ1P1Sw7Fo2R0FzXs3GvE/export?format=csv&" + str(Project_QA_ID3)
    if Project_QA_ID3
    else ""
)

t = safe_read_csv(csv_url_raw)
qalog = safe_read_csv(qasheet)
tari = safe_read_csv(samplingsheet)
hfc = safe_read_csv(hfcsheet)

if t.empty:
    st.warning("The raw submission sheet could not be loaded for this project.")
    t = pd.DataFrame(columns=["Tool", "KEY", "SubmissionDate", "Province"])
if qalog.empty:
    qalog = pd.DataFrame(columns=["QA_Status", "KEY_Unique"])
if tari.empty:
    tari = pd.DataFrame(columns=["Tool", "V_ID", "Skipped"])
if hfc.empty:
    hfc = pd.DataFrame(columns=["Surveyor_Name", "hfc_outliers_ratio", "ta_outliers"])

if "KEY" in t.columns:
    t["KEY_Unique"] = t["KEY"]
else:
    t["KEY_Unique"] = ""

if not qalog.empty and {"QA_Status", "KEY_Unique"}.issubset(qalog.columns):
    t = pd.merge(
        t,
        qalog[["QA_Status", "KEY_Unique"]].drop_duplicates("KEY_Unique"),
        on="KEY_Unique",
        how="left",
    )
else:
    t["QA_Status"] = "Not QA'ed Yet"

t["QA_Status"] = t["QA_Status"].replace("", "Not QA'ed Yet").fillna("Not QA'ed Yet")
t["Completion_status"] = "Complete"

if extra_code != "-":
    try:
        exec(extra_code)
    except Exception as e:
        st.warning(f"extra_code execution skipped: {e}")

if "SubmissionDate" in t.columns:
    t["SubmissionDate"] = pd.to_datetime(t["SubmissionDate"], errors="coerce")

project_data_tools = project_data_tools.copy()
tool_col_map = project_data_tools.set_index("Tool")["main_cols"].to_dict() if not project_data_tools.empty else {}


def compute_vid(row):
    cols_str = tool_col_map.get(row.get("Tool", ""), "")
    cols = [c.strip() for c in str(cols_str).split("-") if c.strip()]
    parts = []
    for col in cols:
        if col in row:
            parts.append(str(row[col]).removesuffix(".0"))
        else:
            parts.append("NA")
    return f"{row.get('Tool', 'NA')}/{'-'.join(parts)}"


t = t.sort_values(by=[c for c in ["Completion_status", "QA_Status"] if c in t.columns], ascending=True)
t["occurance"] = None
for tool, cols in tool_col_map.items():
    group_cols = [c for c in str(cols).split("-") if c != "occurance" and c in t.columns]
    if not group_cols:
        continue
    mask = t["Tool"].eq(tool) if "Tool" in t.columns else pd.Series(False, index=t.index)
    t.loc[mask, "occurance"] = t.loc[mask].groupby(group_cols).cumcount() + 1

t["occurance"] = t["occurance"].fillna(9999).astype(int)
t["V_ID"] = t.apply(compute_vid, axis=1) if not t.empty else pd.Series(dtype=str)

if not tari.empty:
    if "V_ID" in tari.columns and "Tool" in tari.columns:
        tari["V_ID"] = tari["Tool"].astype(str) + "/" + tari["V_ID"].astype(str)
    if "Skipped" in tari.columns:
        tari = tari[tari["Skipped"] != "Yes"]
    if "Tool" in tari.columns and "Tool" in t.columns and not project_data_tools.empty:
        tari = tari[(tari["Tool"].isin(t["Tool"].unique())) & (tari["Tool"].isin(project_data_tools["Tool"]))]

if not tari.empty:
    df_free = t[t["Tool"].isin(project_data_tools["Tool"]) & ~t["Tool"].isin(tari["Tool"])].copy() if "Tool" in t.columns else pd.DataFrame()
    if not df_free.empty:
        df_free = df_free.drop(columns=["KEY", "QA_Status"], errors="ignore")
        df_free = df_free[tari.columns.intersection(df_free.columns)]
        tari = pd.concat([tari, df_free], ignore_index=True)

# Dashboard filters
with st.sidebar:
    st.divider()
    st.markdown("**Dashboard filters**")
    tool_names = sorted(project_data_tools["Tool"].dropna().unique().tolist()) if not project_data_tools.empty else []
    selected_tool = st.multiselect("Tool", tool_names, default=[])
    if selected_tool and "Tool" in t.columns:
        t = t[t["Tool"].isin(selected_tool)].copy()
        if "Tool" in tari.columns:
            tari = tari[tari["Tool"].isin(selected_tool)].copy()
    qa_options = sorted(t["QA_Status"].dropna().astype(str).unique().tolist()) if "QA_Status" in t.columns else []
    default_qa = [x for x in qa_options if x != "Rejected_paused"] or qa_options
    qastatus = st.multiselect("QA Status", qa_options, default=default_qa)
    completion = st.multiselect("Completion Status", ["Complete", "Incomplete"], default=["Complete", "Incomplete"])

if "QA_Status" in t.columns and qastatus:
    t = t[t["QA_Status"].isin(qastatus)].copy()
if "Completion_status" in t.columns and completion:
    t = t[t["Completion_status"].isin(completion)].copy()

if not tari.empty and not t.empty and "V_ID" in tari.columns and "V_ID" in t.columns:
    tari = tari.merge(
        t[["V_ID"] + [c for c in t.columns if c not in tari.columns and c != "V_ID"]].drop_duplicates("V_ID"),
        on="V_ID",
        how="left",
    )
    t = t.merge(
        tari[["V_ID"] + [c for c in tari.columns if c not in t.columns and c != "V_ID"]].drop_duplicates("V_ID"),
        on="V_ID",
        how="left",
    )

if tool_col_map:
    first_map = list(tool_col_map.values())[0]
    if str(first_map).rsplit("-", 1)[-1] == "occurance" and not tari.empty and not t.empty:
        prefixes = tari["V_ID"].astype(str).str.rsplit("-", n=1).str[0].unique()
        tall2 = t[t["V_ID"].astype(str).str.startswith(tuple(prefixes), na=False)].copy()

# Derived tracking tables
if not tari.empty and "V_ID" in tari.columns and "V_ID" in t.columns:
    tall = t[t["V_ID"].isin(tari["V_ID"])].copy()
else:
    tall = t.copy()

if "SubmissionDate" in tall.columns:
    tall["d1"] = pd.to_datetime(tall["SubmissionDate"], format="%b %d, %Y %H:%M:%S", errors="coerce").dt.date
    tall["d2"] = pd.to_datetime(tall["SubmissionDate"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors="coerce").dt.date
    tall["Date"] = pd.to_datetime(tall["d1"].fillna(tall["d2"]))
    tall["Date"] = tall["Date"].dt.strftime("%Y-%m-%d")
    tall = tall.drop(columns=[c for c in ["occurance", "d1", "d2"] if c in tall.columns], errors="ignore")
else:
    tall["Date"] = None

dff = tall["Date"].value_counts(dropna=True).reset_index() if "Date" in tall.columns else pd.DataFrame(columns=["Date", "N"])
if not dff.empty:
    dff.columns = ["Date", "N"]
    dff = dff.sort_values(by="Date", ascending=False)
else:
    dff = pd.DataFrame({"Date": [], "N": []})

counts = (
    t.groupby("Province").size().reset_index(name="count")
    if "Province" in t.columns and not t.empty
    else pd.DataFrame(columns=["Province", "count"])
)
if not counts.empty:
    counts["Province"] = counts["Province"].astype(str).str.strip()

# KPI values
if tari.empty:
    total_target = 0
    total_received = 0
    total_remaining = 0
    approved_n = 0
    rejected_n = 0
    dc_pct = 0
    qa_pct = 0
    data_metrics = pd.DataFrame()
    g = pd.DataFrame(columns=["QA_Status", "count"])
else:
    total_target = tari.shape[0]
    total_received = tari[tari["QA_Status"].isin(qastatus)].shape[0] if "QA_Status" in tari.columns else 0
    total_remaining = max(0, total_target - total_received)
    g = tari[tari["QA_Status"].isin(qastatus)]["QA_Status"].value_counts().reset_index()
    if not g.empty:
        g.columns = ["QA_Status", "count"]
    approved_n = int(g[g["QA_Status"] == "Approved"]["count"].sum()) if not g.empty else 0
    rejected_n = int(g[g["QA_Status"] == "Rejected"]["count"].sum()) if not g.empty else 0
    dc_pct = round(100 * total_received / total_target) if total_target else 0
    qa_pct = round(100 * approved_n / total_received) if total_received else 0

    target = tari.groupby("Tool").size() if "Tool" in tari.columns else pd.Series(dtype=int)
    received = tari[tari["QA_Status"].notna()].groupby("Tool").size() if {"Tool", "QA_Status"}.issubset(tari.columns) else pd.Series(dtype=int)
    approved = tari[tari["QA_Status"] == "Approved"].groupby("Tool").size() if {"Tool", "QA_Status"}.issubset(tari.columns) else pd.Series(dtype=int)
    rejected = tari[tari["QA_Status"] == "Rejected"].groupby("Tool").size() if {"Tool", "QA_Status"}.issubset(tari.columns) else pd.Series(dtype=int)
    awaiting = tari[tari["QA_Status"].isin(["Not QA'ed Yet", "Pending"])].groupby("Tool").size() if {"Tool", "QA_Status"}.issubset(tari.columns) else pd.Series(dtype=int)
    data_metrics = pd.DataFrame(
        {
            "Target": target,
            "Received data": received,
            "Approved data": approved,
            "Rejected data": rejected,
            "Awaiting review": awaiting,
        }
    ).fillna(0).astype(int).reset_index()
    if len(data_metrics) > 1:
        data_metrics.loc["Total"] = data_metrics.sum(numeric_only=True)
        data_metrics.loc["Total", "Tool"] = "All Tools"
    if not data_metrics.empty:
        data_metrics["DC Completion %"] = ((data_metrics["Received data"] / data_metrics["Target"]) * 100).round(2).replace(np.inf, 0)
        data_metrics["Completed ✅"] = (data_metrics["Target"] == data_metrics["Approved data"]).apply(lambda x: "✅" if x else "❌")

# Quality checks table
m_df = tari[~tari["V_ID"].isin(t["V_ID"])] if not tari.empty and "V_ID" in tari.columns and "V_ID" in t.columns else pd.DataFrame()
if not m_df.empty:
    m_df = m_df.copy()
    m_df["Type"] = "Missing Data"
    missing = pd.concat([missing, m_df], ignore_index=True)

ext = (
    t[(~t["V_ID"].isin(tari["V_ID"])) & (t["QA_Status"] == "Approved")][["Tool", "V_ID", "KEY", "QA_Status"]]
    if not tari.empty and all(c in t.columns for c in ["V_ID", "QA_Status", "Tool", "KEY"]) and "V_ID" in tari.columns
    else pd.DataFrame(columns=["Tool", "V_ID", "KEY", "QA_Status"])
)
if not ext.empty:
    ext = ext.copy()
    ext["Type"] = "Extra data"
    missing = pd.concat([missing, ext], ignore_index=True)

dup = (
    t[t["V_ID"].duplicated(keep="first")][["Tool", "V_ID", "KEY", "QA_Status"]]
    if all(c in t.columns for c in ["V_ID", "Tool", "KEY", "QA_Status"])
    else pd.DataFrame(columns=["Tool", "V_ID", "KEY", "QA_Status"])
)
if not dup.empty:
    dup = dup.copy()
    dup["Type"] = "Duplicate Data"
    missing = pd.concat([missing, dup], ignore_index=True)

if "KEY" in tall.columns and not ext.empty and not dup.empty:
    tall = tall[~tall["KEY"].isin(pd.concat([ext["KEY"], dup["KEY"]]))]

# ──────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Tracking", "Summaries", "Updates & Reports"])

with tab1:
    render_section_label("Executive overview")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_kpi_card(
            "DC Progress",
            f"{dc_pct}%",
            f"{total_received} of {total_target} samples received",
            "📥",
            "rgba(0,184,148,0.10)",
            dc_pct,
            "linear-gradient(90deg,#00b894,#0ea5a4)",
        )
    with k2:
        render_kpi_card(
            "QA Approved",
            approved_n,
            f"{qa_pct}% approval rate",
            "✅",
            "rgba(16,185,129,0.10)",
            qa_pct,
            "linear-gradient(90deg,#10b981,#34d399)",
        )
    with k3:
        render_kpi_card("Rejected", rejected_n, "Needs correction or recollection", "✕", "rgba(239,68,68,0.10)")
    with k4:
        render_kpi_card("Remaining", total_remaining, "Not yet received", "⏳", "rgba(100,116,139,0.10)")

    c1, c2 = st.columns([1.35, 1])
    with c1:
        render_section_label("Workflow roadmap")
        with st.container(border=True):
            st.markdown("#### Current delivery stage")
            st.caption("The roadmap highlights the active stage and overall project maturity.")
            components.html(generate_roadmap_html(steps_data, current_step), height=170)
    with c2:
        render_section_label("Project context")
        info1, info2 = st.columns(2)
        with info1:
            render_info_card("Selected project", f"<b>{selected_project}</b><br>Tracking under the main project <b>{main_project}</b>.")
        with info2:
            render_info_card("QA records", "Open the QA notes directly from the quick links below to review issue logs and field actions.")

    render_section_label("Project links")
    cards_html = '<div class="links-grid">'
    for col_name, (icon, label) in link_labels.items():
        value = links_row[col_name]
        if pd.notna(value) and str(value).strip():
            cards_html += (
                f'<div class="link-card"><div class="link-icon">{icon}</div><div class="link-label">{label}</div>'
                f'<div style="margin-top:8px;"><a href="{value}" target="_blank">Open resource →</a></div></div>'
            )
        else:
            cards_html += (
                f'<div class="link-card link-empty"><div class="link-icon">{icon}</div><div class="link-label">{label}</div>'
                f'<div style="margin-top:8px;color:#94a3b8;font-weight:700;">Not available</div></div>'
            )
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)

    render_section_label("Project timeline")
    st.markdown(
        """
        <div class="legend-strip">
            <span><b style="color:#94a3b8">— — —</b> Planned</span>
            <span><b style="color:#2563eb">▬</b> Actual</span>
            <span><b style="color:#2563eb">↝</b> Ongoing</span>
            <span><b style="color:#10b981">✓</b> On time</span>
            <span><b style="color:#ef4444">●</b> Delayed</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(build_project_timeline(project_rows_main.copy()), use_container_width=True, theme="streamlit")

    if proj_completed == "Yes":
        st.info("This project is archived. Use the document links above for the final dataset, trackers, and reference materials.")
    else:
        mcol1, mcol2 = st.columns([1, 1])
        with mcol1:
            render_section_label("Geographic coverage")
            with st.container(border=True):
                geo_raw = load_geojson("afghanistan_provinces.geojson")
                m = build_map(geo_raw, counts if not counts.empty else pd.DataFrame({"Province": [], "count": []}))
                st_folium(m, height=340, use_container_width=True, returned_objects=[], key=f"afg_map_{selected_project}")
        with mcol2:
            render_section_label("Submission rhythm")
            with st.container(border=True):
                st.plotly_chart(build_submission_timeline(dff), use_container_width=True, theme="streamlit")

with tab2:
    render_section_label("Operational tracking")
    left, right = st.columns([1.1, 1])
    with left:
        with st.container(border=True):
            st.markdown("#### Sample tracking table")
            st.caption("Tool-level progress against target samples and QA outcomes.")
            if data_metrics.empty:
                st.info("No sample tracking data available for the current filter set.")
            else:
                st.dataframe(data_metrics, hide_index=True, use_container_width=True)
    with right:
        with st.container(border=True):
            st.markdown("#### Collection vs QA status")
            labels1 = ["Received", "Remaining"]
            values1 = [total_received, total_remaining]
            labels2 = g["QA_Status"].tolist() if not g.empty else ["No data"]
            values2 = g["count"].tolist() if not g.empty else [1]
            d1, d2 = st.columns(2)
            with d1:
                st.plotly_chart(make_donut(labels1, values1, "Data Collection", ["#00b894", "#e5e7eb"], "received"), use_container_width=True, theme="streamlit")
            with d2:
                st.plotly_chart(make_donut(labels2, values2, "QA Progress", ["#10b981", "#ef4444", "#f59e0b", "#cbd5e1"], "reviewed"), use_container_width=True, theme="streamlit")

    b1, b2 = st.columns([1.2, 1])
    with b1:
        with st.container(border=True):
            st.markdown("#### Data quality exceptions")
            st.caption("Missing, extra, or duplicate records detected from the sample and submission join.")
            if missing.empty:
                st.success("No missing, duplicate, or extra data detected for the current filter set.")
            else:
                show_cols = [c for c in ["Tool", "V_ID", "KEY", "QA_Status", "Type"] if c in missing.columns]
                st.dataframe(missing[show_cols], use_container_width=True, hide_index=True)
    with b2:
        with st.container(border=True):
            st.markdown("#### Exports")
            st.caption("Download the latest filtered target/sample frame.")
            tari_csv = convert_df_to_csv(tari)
            st.download_button(
                label="Download sample tracking CSV",
                data=tari_csv,
                file_name="Sample_Tracking.csv",
                mime="text/csv",
                use_container_width=True,
            )
            if QA_records_link:
                st.link_button("Open QA notes", QA_records_link, use_container_width=True)
            notes = safe_value(project_data.loc[0], "notes", "-")
            if notes != "-":
                try:
                    st.markdown(eval(notes[1:-1]), unsafe_allow_html=True)
                except Exception:
                    st.caption("Project note available, but could not be rendered.")

with tab3:
    render_section_label("Dynamic summaries")
    st.info('Summaries include both "Complete" and "Incomplete" submissions unless you restrict the filter in the sidebar.')
    s1, s2 = st.columns(2)
    with s1:
        with st.container(border=True):
            st.markdown("#### Sample summary")
            disag2 = st.multiselect(
                "Group target vs received by",
                tari.columns.tolist() if not tari.empty else [],
                default=[x for x in def_var0 if x in tari.columns] if not tari.empty else [],
                help="Create grouped sample progress summaries.",
            )
            if disag2 and not tari.empty:
                total_target_s = tari.fillna("NAN").groupby(disag2).size()
                received_data_s = tari.fillna("NAN")[tari["QA_Status"].isin(qastatus)].groupby(disag2).size() if "QA_Status" in tari.columns else pd.Series(dtype=int)
                summary = pd.DataFrame({"Total_Target": total_target_s, "Received_Data": received_data_s}).fillna(0).astype(int)
                summary["Remaining"] = summary["Total_Target"] - summary["Received_Data"]
                summary["Completed ✅"] = (summary["Received_Data"] == summary["Total_Target"]).apply(lambda x: "✅" if x else "❌")
                st.dataframe(summary, use_container_width=True)
    with s2:
        with st.container(border=True):
            st.markdown("#### Dataset summary")
            disag = st.multiselect(
                "Group dataset by",
                tall.columns.tolist(),
                default=[x for x in def_var1 if x in tall.columns],
                help="Create grouped summaries from the submission dataset.",
            )
            if disag:
                if len(disag) == 1:
                    disag_t = tall.groupby(disag).size().reset_index().rename(columns={0: "N"})
                    disag_t.loc[len(disag_t)] = ["Total", disag_t["N"].sum()]
                else:
                    disag_t = tall.groupby(disag).size().unstack(disag[-1], fill_value=0).reset_index()
                    disag_t.loc["Total"] = disag_t.sum(numeric_only=True)
                st.dataframe(disag_t, use_container_width=True)

    if "tall2" in locals():
        with st.container(border=True):
            st.markdown("#### Tryouts summary (phone surveys)")
            disag_raw = st.multiselect(
                "Group tryouts by",
                tall2.columns.tolist(),
                default=[x for x in def_var2 if x in tall2.columns],
                help="Useful for phone surveys with multiple attempts per respondent.",
            )
            if disag_raw:
                if len(disag_raw) == 1:
                    disag_traw = tall2.groupby(disag_raw).size().reset_index().rename(columns={0: "N"})
                    disag_traw.loc[len(disag_traw)] = ["Total", disag_traw["N"].sum()]
                else:
                    disag_traw = tall2.groupby(disag_raw).size().unstack(disag_raw[-1], fill_value=0).reset_index()
                    disag_traw.loc["Total"] = disag_traw.sum(numeric_only=True)
                st.dataframe(disag_traw, use_container_width=True)

with tab4:
    render_section_label("Updates and reporting")
    logs = parse_log(safe_value(project_data.loc[0], "Logs", ""))
    by_day = {}
    for d, msg in logs:
        by_day.setdefault(d, []).append(msg)

    u1, u2 = st.columns([1, 1])
    with u1:
        with st.container(border=True):
            st.markdown("#### Project updates")
            if not by_day:
                st.caption("No updates logged for this project.")
            else:
                for d, msgs in by_day.items():
                    items = "".join([f"<div class='update-item'>• {m}</div>" for m in msgs])
                    st.markdown(
                        f"<div class='update-day'><div class='update-date'>{d.strftime('%d %b %Y')}</div>{items}</div>",
                        unsafe_allow_html=True,
                    )
    with u2:
        with st.container(border=True):
            st.markdown("#### Reporting utilities")
            st.caption("Generate the surveyor performance report for supported projects.")
            if main_project in ["ECD", "EFSP"]:
                if st.button("Build surveyor performance report", type="primary", use_container_width=True):
                    qalog2 = pd.merge(
                        tall,
                        qalog[[c for c in ["Issue_Type", "Issue_Description", "surveyor_notified", "surveyor_response", "issue_resolved", "KEY_Unique"] if c in qalog.columns]],
                        on="KEY_Unique",
                        how="left",
                    )
                    qalog2["severity"] = qalog2["QA_Status"].map({"Rejected": "High", "Approved": "Low", "Pending": "Medium"})
                    issues_cols = [
                        c for c in ["Site_Visit_ID", "Province", "Village", "severity", "QA_Status", "Surveyor_Name", "KEY", "Date", "Issue_Type", "Issue_Description", "surveyor_notified", "surveyor_response", "issue_resolved"] if c in qalog2.columns
                    ]
                    issues = qalog2[issues_cols].copy()
                    summary_sr = (
                        qalog2.groupby("Surveyor_Name")
                        .agg(
                            total_submissions=("Surveyor_Name", "size"),
                            rejected_count=("QA_Status", lambda x: (x == "Rejected").sum()),
                            total_feedback_ratio=("Issue_Type", lambda x: x.notna().mean()),
                        )
                        .assign(rejection_ratio=lambda d: d.rejected_count / d.total_submissions)
                        .reset_index()
                    )
                    if not hfc.empty and "Surveyor_Name" in hfc.columns:
                        hfc2 = hfc.drop_duplicates(subset="Surveyor_Name")
                        summary_sr = pd.merge(summary_sr, hfc2, on="Surveyor_Name", how="left").fillna(0)
                    else:
                        summary_sr["hfc_outliers_ratio"] = 0
                        summary_sr["ta_outliers"] = 0

                    if "Issue_Type" in issues.columns:
                        issues = issues[issues["Issue_Type"].notna()].copy()
                    if not issues.empty:
                        issues["issue_resolved"] = issues.get("issue_resolved", "No").fillna("No").replace("", "No")
                        for c in ["Issue_Description", "surveyor_response", "Province", "Village", "Site_Visit_ID", "Surveyor_Name", "Issue_Type", "KEY"]:
                            if c in issues.columns:
                                issues[c] = issues[c].fillna("")
                        if {"Province", "Village"}.issubset(issues.columns):
                            issues["Location"] = issues["Province"] + "-" + issues["Village"]

                    chart_cols = [c for c in ["Date", "QA_Status", "Surveyor_Name", "Issue_Type", "Issue_Description", "surveyor_response", "KEY", "Site_Visit_ID", "Province", "Village", "issue_resolved"] if c in qalog2.columns]
                    chart_source = qalog2[chart_cols].copy()
                    chart_source["Date"] = pd.to_datetime(chart_source["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
                    chart_source = chart_source.dropna(subset=["Date"])
                    for c in ["Issue_Type", "Issue_Description", "surveyor_response", "KEY", "Site_Visit_ID", "Province", "Village"]:
                        if c in chart_source.columns:
                            chart_source[c] = chart_source[c].fillna("")
                    if "issue_resolved" in chart_source.columns:
                        chart_source["issue_resolved"] = chart_source["issue_resolved"].fillna("No").replace("", "No")
                    else:
                        chart_source["issue_resolved"] = "No"
                    if {"Province", "Village"}.issubset(chart_source.columns):
                        chart_source["Location"] = chart_source["Province"] + "-" + chart_source["Village"]
                    else:
                        chart_source["Location"] = ""
                    chart_source_json = chart_source.to_json(orient="records")

                    summary_scored = score_surveyors(summary_sr, w_rej=0.35, w_out=0.1, w_out2=0.2, w_fb=0.35)
                    report_html = build_surveyor_report_html(selected_project, "ATR-QA Department", summary_scored, issues, chart_source_json)
                    st.download_button(
                        label="Download surveyor report (HTML)",
                        data=report_html,
                        file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html",
                        mime="text/html",
                        use_container_width=True,
                        type="primary",
                    )
            else:
                st.info("Surveyor performance reporting is enabled only for ECD and EFSP projects.")

st.divider()
foot1, foot2 = st.columns([1, 1])
with foot1:
    st.caption("ATR Dashboard redesign • polished layout, lighter premium theme, clearer hierarchy")
with foot2:
    st.markdown(
        f"<div style='text-align:right;color:#94a3b8;font-size:12px;'>Updated {datetime.now().strftime('%d %b %Y')}</div>",
        unsafe_allow_html=True,
    )
