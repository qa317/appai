import streamlit as st
import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import copy
import re
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.set_page_config(layout="wide", page_title="ATR Dashboard", page_icon="📊")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600&display=swap');
:root {
  --bg: #f4f5f7;
  --brand-accent: #0f766e;
  --surface: transparent;
  --border: #e2e8f0;
  --text: #0f172a;
  --text-muted: #64748b;
  --radius: 16px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 24px rgba(0,0,0,0.10);
  --gradient-brand: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f766e 100%);
  --glass: rgba(255,255,255,0.55);
  --glass-border: rgba(226,232,240,0.8);
}
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 1rem !important; max-width: 1360px; }

/* Force transparent backgrounds everywhere */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stHorizontalBlock"],
div[data-testid="stMetric"],
.stDataFrame { background: transparent !important; }

/* ── Make dataframe toolbar (download/search/fullscreen) visible on hover ── */
div[data-testid="stDataFrame"],
div[data-testid="stDataFrameResizable"] { position: relative; }

div[data-testid="stDataFrame"] [data-testid="stElementToolbar"],
div[data-testid="stDataFrameResizable"] [data-testid="stElementToolbar"],
[data-testid="stElementToolbar"] {
  opacity: 1 !important;
  visibility: visible !important;
  pointer-events: auto !important;
  background: rgba(255,255,255,0.95) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
  transition: opacity 0.2s ease !important;
}
div[data-testid="stDataFrame"]:hover [data-testid="stElementToolbar"],
div[data-testid="stDataFrameResizable"]:hover [data-testid="stElementToolbar"] {
  opacity: 1 !important;
}
[data-testid="stElementToolbarButton"] {
  color: #0f766e !important;
}
[data-testid="stElementToolbarButton"]:hover {
  background: rgba(15,118,110,0.08) !important;
}

/* Bordered containers: frosted glass */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div[data-testid="stVerticalBlock"]) {
  background: var(--glass) !important;
  backdrop-filter: blur(8px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 18px !important;
}

/* Hero Banner */
.hero-banner {
  background: var(--gradient-brand);
  border-radius: 22px; padding: 32px 40px; margin-bottom: 24px;
  display: flex; align-items: center; justify-content: space-between;
  position: relative; overflow: hidden;
  box-shadow: 0 8px 32px rgba(15,23,42,0.25);
}
.hero-banner::before {
  content: ''; position: absolute; top: -60%; right: -8%;
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-banner::after {
  content: ''; position: absolute; bottom: -40%; left: 15%;
  width: 250px; height: 250px;
  background: radial-gradient(circle, rgba(20,184,166,0.12) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-banner h1 { color: #fff; font-size: 28px; font-weight: 800; margin: 0; letter-spacing: -0.5px; position: relative; z-index: 1; }
.hero-banner .hero-sub { color: rgba(255,255,255,0.55); font-size: 13px; font-weight: 400; margin-top: 4px; position: relative; z-index: 1; }
.hero-badge {
  background: rgba(255,255,255,0.10); backdrop-filter: blur(12px);
  color: #fff; padding: 10px 18px; border-radius: 999px;
  font-size: 13px; font-weight: 600;
  border: 1px solid rgba(255,255,255,0.12);
  position: relative; z-index: 1;
  display: flex; align-items: center; gap: 8px;
}
.hero-badge .dot { width: 8px; height: 8px; background: #34d399; border-radius: 50%; animation: pulse-dot 2s ease infinite; }
@keyframes pulse-dot { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.5); } }

/* Section Labels */
.section-label {
  font-size: 11px; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--text-muted);
  margin: 36px 0 14px; display: flex; align-items: center; gap: 10px;
}
.section-label::after { content: ''; flex: 1; height: 1px; background: linear-gradient(90deg, var(--border), transparent); }

/* KPI Stack (vertical fallback) */
.kpi-stack { display: flex; flex-direction: column; gap: 12px; }
.kpi-card-v {
  background: var(--glass); backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border); border-radius: 16px;
  padding: 18px 22px; display: flex; align-items: center; gap: 16px;
  transition: transform 0.15s, box-shadow 0.15s;
}
.kpi-card-v:hover { transform: translateY(-1px); box-shadow: var(--shadow-lg); }
.kpi-card-v .kpi-icon-circle {
  width: 48px; height: 48px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; flex-shrink: 0;
}
.kpi-card-v .kpi-body { flex: 1; }
.kpi-card-v .kpi-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: var(--text-muted); margin-bottom: 2px; }
.kpi-card-v .kpi-value { font-size: 28px; font-weight: 900; font-family: 'JetBrains Mono', monospace; letter-spacing: -1px; line-height: 1.1; }
.kpi-card-v .kpi-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.kpi-card-v .kpi-bar { height: 4px; background: #e2e8f0; border-radius: 99px; overflow: hidden; margin-top: 6px; }
.kpi-card-v .kpi-bar-fill { height: 100%; border-radius: 99px; transition: width 0.6s ease; }

/* KPI Horizontal Row */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
@media (max-width: 900px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
.kpi-tile {
  background: var(--glass); backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border); border-radius: 16px;
  padding: 20px 22px;
  transition: transform 0.15s, box-shadow 0.15s;
}
.kpi-tile:hover { transform: translateY(-1px); box-shadow: var(--shadow); }
.kpi-tile .kpi-tile-label {
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--text-muted); margin-bottom: 8px;
}
.kpi-tile .kpi-tile-value {
  font-size: 30px; font-weight: 900; line-height: 1;
  font-family: 'JetBrains Mono', monospace; letter-spacing: -1.5px;
}
.kpi-tile .kpi-tile-sub { font-size: 11px; color: var(--text-muted); margin-top: 6px; }
.kpi-tile .kpi-tile-bar {
  height: 4px; background: #e2e8f0; border-radius: 99px;
  overflow: hidden; margin-top: 10px;
}
.kpi-tile .kpi-tile-bar-fill { height: 100%; border-radius: 99px; transition: width 0.8s cubic-bezier(.22,.61,.36,1); }

/* Link Grid */
.links-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px; }
@media (max-width: 900px) { .links-grid { grid-template-columns: repeat(3, 1fr); } }
.link-tile {
  background: var(--glass); backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border); border-radius: 14px;
  padding: 16px; text-align: center;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.link-tile:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); border-color: #0f766e; }
.link-tile .tile-icon { font-size: 22px; margin-bottom: 6px; }
.link-tile .tile-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted); margin-bottom: 6px; }
.link-tile a { color: #0f766e; font-weight: 600; text-decoration: none; font-size: 13px; }
.link-tile a:hover { text-decoration: underline; }
.link-tile.na { border-style: dashed; opacity: 0.4; }

/* Legend */
.legend-strip {
  display: flex; gap: 18px; flex-wrap: wrap; align-items: center;
  background: var(--glass); backdrop-filter: blur(6px);
  border-radius: 12px; padding: 10px 18px;
  font-size: 12px; color: var(--text-muted);
  margin-bottom: 8px; border: 1px solid var(--glass-border);
}
.legend-strip b { font-weight: 700; }

/* Archived */
.archived-card {
  background: linear-gradient(135deg, rgba(240,253,250,0.8) 0%, rgba(236,253,245,0.8) 100%);
  backdrop-filter: blur(8px); border: 1px solid #99f6e4;
  border-radius: 18px; padding: 26px 30px; margin: 16px 0;
}
.archived-card h3 { color: #0f766e; margin: 0 0 8px; font-size: 18px; font-weight: 800; }
.archived-card p { color: var(--text); font-size: 14px; line-height: 1.65; margin: 0; }

/* Login */
.login-shell { max-width: 420px; margin: 10vh auto; text-align: center; }
.login-shell .logo-circle {
  width: 72px; height: 72px; background: var(--gradient-brand);
  border-radius: 20px; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 18px; font-size: 32px; color: #fff;
  box-shadow: 0 6px 24px rgba(15,23,42,0.3);
}
.login-shell h2 { font-size: 26px; font-weight: 800; color: var(--text); margin-bottom: 4px; }
.login-shell .sub { font-size: 13px; color: var(--text-muted); margin-bottom: 24px; }
.login-about-card {
  max-width: 420px; margin: 16px auto 0;
  background: var(--glass); backdrop-filter: blur(8px);
  border: 1px solid var(--border); border-radius: 16px;
  padding: 20px 24px; text-align: left;
}
.login-about-card h4 { color: #0f766e; margin: 0 0 6px; font-size: 14px; font-weight: 700; }
.login-about-card p { font-size: 13px; color: var(--text-muted); line-height: 1.55; margin: 0; }
.error-toast {
  background: rgba(254,242,242,0.8); border-left: 4px solid #ef4444;
  border-radius: 12px; padding: 14px 18px; margin-top: 10px; text-align: left;
}
.error-toast strong { color: #991b1b; }
.error-toast p { color: #7f1d1d; font-size: 13px; margin: 4px 0 0; }

/* Updates */
.upd-day { margin: 10px 0 14px; padding-left: 14px; border-left: 3px solid #e2e8f0; }
.upd-date { font-weight: 700; margin-bottom: 6px; color: #0f766e; font-size: 13px; }
.upd-item { margin: 4px 0; color: var(--text); font-size: 13px; }
.upd-dot { color: #94a3b8; margin-right: 8px; }
.upd-sep { height: 1px; background: var(--border); margin: 12px 0; }

/* Streamlit Overrides */
.stSelectbox label, .stMultiSelect label { font-size: 12px !important; font-weight: 700 !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: 0.06em; }
.stDataFrame { border-radius: 14px !important; overflow: visible; box-shadow: var(--shadow) !important; background: var(--glass) !important; }
div[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 16px !important; overflow: hidden; background: var(--glass) !important; backdrop-filter: blur(6px) !important; }
div[data-testid="stExpander"] summary { font-weight: 700 !important; }
.stDownloadButton button { border-radius: 12px !important; font-weight: 600 !important; }
.js-plotly-plot .plotly { border-radius: 14px; }
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 18px !important; }
div[data-testid="stAlert"] { background: var(--glass) !important; backdrop-filter: blur(6px) !important; border-radius: 14px !important; }
</style>
""", unsafe_allow_html=True)

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

df, df_tools, df_users = load_data()
user_dict = df_users.set_index("users")[["password", "project"]].to_dict(orient="index")

# Cached per-URL loader for project-specific Google Sheets (raw submissions,
# QA log, sampling sheet). Avoids re-downloading + re-parsing on every filter
# click. TTL matches load_data() so all data ages together.
@st.cache_data(ttl=120, show_spinner=False)
def fetch_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False, encoding='utf-8')

# ──────────────────────────────────────────────
# AUTH
# ──────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)
    placeholder = st.empty()
    with placeholder.form("login"):
        st.markdown("""<div class="login-shell">
            <div class="logo-circle">📊</div>
            <h2>ATR Consulting</h2>
            <div class="sub">Data Collection & QA Progress Tracker</div>
        </div>""", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In", use_container_width=True)
        st.markdown("""<div class="login-about-card">
            <h4>About This App</h4>
            <p>Track data collection progress, monitor QA workflows, and generate clear data summaries — all in one place.</p>
        </div>""", unsafe_allow_html=True)
    if submit:
        if username in user_dict and password == user_dict[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.username = username
            placeholder.empty()
            st.success("Welcome back!")
        else:
            st.markdown("""<div class="error-toast">
                <strong>Access Denied</strong>
                <p>Incorrect username or password. Please try again.</p>
            </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# MAIN DASHBOARD
# ──────────────────────────────────────────────
if st.session_state.logged_in:

    st.markdown(f"""
    <div class="hero-banner">
        <div>
            <h1>Data Collection & QA Dashboard</h1>
            <div class="hero-sub">ATR Consulting · Progress Tracker</div>
        </div>
        <div class="hero-badge">
            <span class="dot"></span>
            {st.session_state.username}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.toast("Press **R** to refresh · Figures include both complete and incomplete data by default.")

    if user_dict[st.session_state.username]["project"].split(',')[0] == 'All':
        main_project_names = df['Main Project'].unique()
    else:
        main_project_names = df[df['Main Project'].isin(
            user_dict[st.session_state.username]["project"].split(',')
        )]['Main Project'].unique()

    cols1, cols2, cols3 = st.columns([1, 1, 1])
    with cols1:
        main_project = st.selectbox("Project", main_project_names, key="selectbox_1")
    project_data = df[df['Main Project'] == main_project].reset_index()
    project_names = df[df['Main Project'] == main_project]['Project Name'].unique()

    # ── PROJECT TIMELINE ──
    st.markdown('<div class="section-label">Project Timeline</div>', unsafe_allow_html=True)

    PHASES = [
        ("DC",  "Planned Data Collection-Start", "Planned Data Collection-End",
                "Data Collection-Start", "Data Collection-End"),
        ("QA",  "Planned data QA-Start", "Planned data QA-End",
                "data QA-Start", "data QA-End"),
        ("DM",  "Planned DM-Start", "Planned DM-End",
                "DM-Start", "DM-End"),
        ("A&R", "Planned Reporting-Start", "Planned Reporting-End",
                "Reporting-Start", "Reporting-End"),
    ]
    PLANNED_COLOR = "rgba(100,116,139,0.55)"
    ACTUAL_COLOR  = "rgba(14,165,233,0.30)"
    RUNNING_COLOR = "rgba(14,165,233,0.50)"
    CURRENT_PLANNED_COLOR = "rgba(15,118,110,1.0)"
    CURRENT_ACTUAL_COLOR  = "rgba(15,118,110,0.45)"
    ONTIME_COLOR = "#10b981"
    DELAY_COLOR  = "#ef4444"
    PLANNED_W = 3
    ACTUAL_W  = 10
    GAP = 1.1
    today = pd.Timestamp.today().normalize()

    def to_dt(x):
        return pd.to_datetime(x, dayfirst=True, errors="coerce")

    def excel_like_table(df, key, height=350):
      """Render a dataframe with Excel-style per-column filters, sort, resize."""
      df = df.reset_index() if df.index.name or any(df.index.names) else df.copy()
  
      gob = GridOptionsBuilder.from_dataframe(df)
      gob.configure_default_column(
          filter=True,            # enables filter icon on every column
          sortable=True,
          resizable=True,
          floatingFilter=True,    # the always-visible filter row under headers
          editable=False,
      )
      # Use 'set' filter (the Excel-style checkbox list) for object cols,
      # numeric/date filters for the rest — agGrid picks automatically when
      # you pass these per-type filters:
      for col in df.columns:
          if pd.api.types.is_numeric_dtype(df[col]):
              gob.configure_column(col, filter="agNumberColumnFilter")
          elif pd.api.types.is_datetime64_any_dtype(df[col]):
              gob.configure_column(col, filter="agDateColumnFilter")
          else:
              gob.configure_column(col, filter="agSetColumnFilter")  # checkbox list
  
      gob.configure_grid_options(domLayout='normal')
      grid_options = gob.build()
  
      return AgGrid(
          df,
          gridOptions=grid_options,
          height=height,
          theme="streamlit",                 # matches your light theme
          update_mode=GridUpdateMode.NO_UPDATE,
          allow_unsafe_jscode=True,
          fit_columns_on_grid_load=True,
          key=key,
      )
    def delay_days(plan_end, actual_end):
        if pd.notna(plan_end) and pd.notna(actual_end):
            d = (actual_end - plan_end).days
            return d if d > 0 else 0
        return 0

    for _, ps, pe, a_s, a_e in PHASES:
        for c in (ps, pe, a_s, a_e):
            if c in project_data.columns:
                project_data[c] = to_dt(project_data[c])

    fig = go.Figure()
    y_vals, y_labels = [], []
    y = 0
    for _, row in project_data.iterrows():
        project = str(row.get("Project Name", "—"))
        responsible = str(row.get("Responsible", "") or "").strip().lower()
        project_y = []
        for phase, ps_c, pe_c, as_c, ae_c in PHASES:
            ps, pe = row.get(ps_c), row.get(pe_c)
            a_s, a_e = row.get(as_c), row.get(ae_c)
            if pd.isna(ps) or pd.isna(pe):
                continue
            is_current = bool(responsible) and phase.lower() in responsible
            y_vals.append(y)
            y_labels.append(f"{project} — {phase}")
            project_y.append(y)
            planned_color = CURRENT_PLANNED_COLOR if is_current else PLANNED_COLOR
            fig.add_trace(go.Scatter(x=[ps, pe], y=[y, y], mode="lines",
                line=dict(color=planned_color, width=PLANNED_W, dash="dash"), showlegend=False,
                hovertemplate=f"<b>{project}</b><br>{phase}<br>Planned: {ps:%d-%b-%Y} → {pe:%d-%b-%Y}<extra></extra>"))
            if pd.notna(a_s):
                is_running = pd.isna(a_e)
                actual_end = a_e if pd.notna(a_e) else today
                actual_color = CURRENT_ACTUAL_COLOR if is_current else (RUNNING_COLOR if is_running else ACTUAL_COLOR)
                fig.add_trace(go.Scatter(x=[a_s, actual_end], y=[y, y], mode="lines",
                    line=dict(color=actual_color, width=ACTUAL_W), showlegend=False,
                    hovertemplate=f"<b>{project}</b><br>{phase}<br>Actual: {a_s:%d-%b-%Y} → {actual_end:%d-%b-%Y}{' (running)' if is_running else ''}<extra></extra>"))
                if is_running:
                    fig.add_annotation(x=actual_end, y=y, text="<b>↝</b>", showarrow=False,
                        xanchor="left", yanchor="middle", font=dict(size=22, color="#0f766e"), bgcolor="rgba(0,0,0,0)")
                if not is_running:
                    d = delay_days(pe, a_e)
                    if d > 0:
                        fig.add_trace(go.Scatter(x=[a_e], y=[y], mode="markers+text",
                            marker=dict(size=8, color=DELAY_COLOR), text=[f"+{d}d"], textposition="top center",
                            textfont=dict(size=9, color=DELAY_COLOR), showlegend=False))
                    else:
                        fig.add_annotation(x=a_e, y=y, text="<b>✓</b>", showarrow=False, font=dict(size=16, color=ONTIME_COLOR), xshift=8)
            y += 1
        if project_y and responsible:
            fig.add_annotation(xref="paper", x=0.9, xanchor="left",
                y=sum(project_y) / len(project_y), yanchor="middle",
                text=f"<span style='color:#0f766e;font-size:12px;font-weight:700'>{row.get('Responsible')}</span>", showarrow=False)
        y += GAP

    st.markdown("""<div class="legend-strip">
        <span><b style="color:#94a3b8">— — —</b> Planned</span>
        <span><b style="color:#0ea5e9">▬</b> Actual</span>
        <span style="color:#0ea5e9"><b>↝</b> Ongoing</span>
        <span style="color:#10b981"><b>✓</b> On time</span>
        <span style="color:#ef4444"><b>●</b> Delayed</span>
    </div>""", unsafe_allow_html=True)

    fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.35)
    fig.add_annotation(x=today, y=0.99, xref="x", yref="paper",
        text="<b><i>Today</i></b>", showarrow=False, xanchor="center", yanchor="bottom", font=dict(size=12, color="#0f766e"))
    fig.update_yaxes(tickmode="array", tickvals=y_vals, ticktext=y_labels, autorange="reversed", title="")
    max_date = max(project_data[pe_c].max() if pe_c in project_data.columns else pd.Timestamp.today() for _, _, pe_c, _, _ in PHASES)
    fig.update_xaxes(
        range=[project_data[[ps_c for _, ps_c, _, _, _ in PHASES if ps_c in project_data.columns]].min().min(),
               max_date + pd.Timedelta(days=20)],
        showgrid=True, gridcolor="rgba(0,0,0,0.03)", zeroline=False)
    fig.update_layout(
        height=max(380, 20 * len(y_vals)), margin=dict(l=95, r=80, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        hovermode="closest", font=dict(family="Outfit, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)

    # ── SUB-PROJECT ──
    st.markdown('<div class="section-label">Round / Sub-Project</div>', unsafe_allow_html=True)
    collll1, collll2, collll3 = st.columns([1, 1, 1])
    with collll1:
        selected_project = st.selectbox("Sub-project", project_names, key="selectbox_2")

    project_data = df[df['Project Name'] == selected_project].reset_index()
    QA_records_link = project_data['QA-Notes link'][0]
    proj_completed = project_data['Completed'][0]
    project_data_tools = df_tools[df_tools['Project Name'] == selected_project].reset_index()
    tool_col_map = project_data_tools.set_index('Tool')['main_cols'].to_dict()

    def compute_vid(row):
        cols_str = tool_col_map.get(row['Tool'], '')
        cols = [c.strip() for c in cols_str.split('-') if c.strip()]
        parts = []
        for col in cols:
            if col in row:
                parts.append(str(row[col]).removesuffix('.0'))
            else:
                parts.append("NA")
        return f"{row['Tool']}/{'-'.join(parts)}"

    def_var = project_data['Summary_defualt_var'][0]
    if def_var.strip() == "-":
        def_var0, def_var1, def_var2 = [], [], []
    else:
        parts = def_var.split(";")
        def_var0 = [item.strip() for item in parts[0].split(",")] if len(parts) > 0 else []
        def_var1 = [item.strip() for item in parts[1].split(",")] if len(parts) > 1 else []
        def_var2 = [item.strip() for item in parts[2].split(",")] if len(parts) > 2 else []

    # ── ROADMAP ──
    def generate_roadmap_html(steps, current_step_label):
        processed_steps = []
        try:
            current_index = [s['label'] for s in steps].index(current_step_label)
        except ValueError:
            current_index = -1
        for i, step in enumerate(steps):
            if current_index == -1: status = 'upcoming'
            elif i < current_index: status = 'completed'
            elif i == current_index: status = 'ongoing'
            else: status = 'upcoming'
            processed_steps.append({'label': step['label'], 'status': status})
        num_steps = len(processed_steps)
        completed_steps = sum(1 for s in processed_steps if s['status'] == 'completed')
        progress_pct = (completed_steps / (num_steps - 1)) * 100 if num_steps > 1 else 0
        nodes_html = ""
        for i, step in enumerate(processed_steps):
            s = step['status']
            if s == 'completed':
                inner = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3"><path d="M5 13l4 4L19 7"/></svg>'
                ring_bg, ring_border, txt_color, txt_weight, size = '#0f766e', '#0f766e', '#0f766e', '600', '30px'
            elif s == 'ongoing':
                inner = '<div style="width:10px;height:10px;background:#fff;border-radius:50%;animation:pulse-dot 2s ease infinite;"></div>'
                ring_bg, ring_border, txt_color, txt_weight, size = '#1e293b', '#1e293b', '#1e293b', '800', '36px'
            else:
                inner = '<div style="width:6px;height:6px;background:#cbd5e1;border-radius:50%;"></div>'
                ring_bg, ring_border, txt_color, txt_weight, size = 'rgba(255,255,255,0.7)', '#e2e8f0', '#94a3b8', '400', '28px'
            shadow = "box-shadow:0 0 0 4px rgba(30,41,59,0.1);" if s=='ongoing' else ""
            nodes_html += f"""<div style="display:flex;flex-direction:column;align-items:center;width:{100/num_steps}%;">
                <div style="width:{size};height:{size};border-radius:50%;background:{ring_bg};border:2px solid {ring_border};
                    display:flex;align-items:center;justify-content:center;z-index:2;{shadow}">{inner}</div>
                <p style="margin-top:36px;font-size:10px;font-weight:{txt_weight};color:{txt_color};width:80px;text-align:center;line-height:1.3;letter-spacing:0.02em;">{step['label']}</p>
            </div>"""
        pw = f"calc({progress_pct}%)" if num_steps > 1 else "0%"
        return f"""<style>@keyframes pulse-dot{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.5);opacity:.5}}}}</style>
        <div style="max-width:100%;margin:0 auto;padding:20px 8px;"><div style="position:relative;width:100%;">
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:100%;height:4px;background:#e2e8f0;border-radius:99px;"></div>
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:{pw};height:4px;background:linear-gradient(90deg,#0f766e,#14b8a6);border-radius:99px;transition:width .5s;"></div>
            <div style="position:relative;display:flex;justify-content:space-between;align-items:flex-start;width:100%;">{nodes_html}</div>
        </div></div>"""

    steps_data = [{"label": "Form Coding (XLSForm)"}, {"label": "Training"}, {"label": "QA-Manual Checks"},
        {"label": "QA-Automated Checks"}, {"label": "QA-Dataset Finalization"}, {"label": "DM-Dataset Finalization"},
        {"label": "QA Report"}, {"label": "QA Completion"}]
    current_step = project_data['current_step'][0]
    st.components.v1.html(generate_roadmap_html(steps_data, current_step), height=150)

    # ── PROJECT LINKS ──
    st.markdown('<div class="section-label">Project Links</div>', unsafe_allow_html=True)
    links_row = project_data[['Tool link', 'XLSForm link', 'QA-Notes link', 'Tracker link', 'DC Tracker', 'Document folder link']].iloc[0]
    link_labels = {'Tool link': ('🛠️', 'Tool'), 'XLSForm link': ('📋', 'XLSForm'), 'QA-Notes link': ('📊', 'QA Notes'),
        'Tracker link': ('📈', 'QA Tracker'), 'DC Tracker': ('📉', 'DC Tracker'), 'Document folder link': ('📁', 'Docs')}
    cards_html = '<div class="links-grid">'
    for col_name, (icon, label) in link_labels.items():
        value = links_row[col_name]
        if pd.notna(value) and str(value).strip():
            cards_html += f'<div class="link-tile"><div class="tile-icon">{icon}</div><div class="tile-label">{label}</div><a href="{value}" target="_blank">Open →</a></div>'
        else:
            cards_html += f'<div class="link-tile na"><div class="tile-icon">{icon}</div><div class="tile-label">{label}</div><span style="font-size:12px;color:#94a3b8;font-style:italic;">N/A</span></div>'
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ── ARCHIVED OR DATA METRICS ──
    if proj_completed == "Yes":
        st.markdown("""<div class="archived-card"><h3>📁 Project Archived</h3>
            <p>This project has been archived. For complete information on sampling and site visits,
            please refer to the Document field. Relevant datasets and trackers are also available.</p></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-label">Data Metrics</div>', unsafe_allow_html=True)
        with st.spinner('Loading/refreshing project data...'):
            missing = pd.DataFrame(columns=['Tool','V_ID','KEY','Type','QA_Status'])
            rawsheet = project_data['raw_sheet'][0]
            Project_QA_ID = project_data['Sampling_ID'][0]
            Project_QA_ID2 = project_data['QAlog_ID'][0]
            Project_QA_ID3 = project_data['HFC_ID'][0]
            raw_sheet_id = rawsheet.split('/d/')[1].split('/')[0]
            csv_url_raw = f"https://docs.google.com/spreadsheets/d/{raw_sheet_id}/export?format=csv&id={raw_sheet_id}&gid=0"
            t = fetch_csv(csv_url_raw).copy()
            t['KEY_Unique'] = t['KEY']
            qasheet = "https://docs.google.com/spreadsheets/d/1V1SfBZUwHN0NtXFIoiXEh7JGkpTUOLZnGAfFN8QVXYQ/export?format=csv&" + Project_QA_ID2
            qalog = fetch_csv(qasheet)
            t = pd.merge(t, qalog[['QA_Status','KEY_Unique']].drop_duplicates('KEY_Unique'), on='KEY_Unique', how='left')
            t['QA_Status'] = t['QA_Status'].replace('', "Not QA'ed Yet")
            t['QA_Status'] = t['QA_Status'].fillna("Not QA'ed Yet")
            extra_code = project_data['extra_code'][0]
            Add_cols = project_data_tools['Add_columns'][0]
            t['Completion_status'] = 'Complete'
            if extra_code != '-':
                exec(extra_code)
            t['SubmissionDate'] = pd.to_datetime(t['SubmissionDate'], errors='coerce')
            t = t.sort_values(by=['Completion_status', 'QA_Status','SubmissionDate'], ascending=[ True, True,False])
            t['occurance'] = None
            for tool, cols in tool_col_map.items():
                group_cols = [c for c in cols.split('-') if c != 'occurance']
                mask = t['Tool'] == tool
                t.loc[mask, 'occurance'] = t.loc[mask].groupby(group_cols).cumcount() + 1
            t['occurance'] = t['occurance'].fillna(9999).astype(int)
            t['V_ID'] = t.apply(compute_vid, axis=1)
            samplingsheet = "https://docs.google.com/spreadsheets/d/1U0Y7TQnTFEg1edMb0IHejOxv9S2YLY2UH-tp1qzXyBg/export?format=csv&" + Project_QA_ID
            tari = fetch_csv(samplingsheet).copy()
            tari['V_ID'] = tari['Tool'] + "/" + tari['V_ID']
            tari = tari[tari['Skipped'] != "Yes"]
            tari = tari[(tari["Tool"].isin(t["Tool"].unique())) & (tari["Tool"].isin(project_data_tools["Tool"]))]
            df_free = t[t["Tool"].isin(project_data_tools["Tool"]) & ~t["Tool"].isin(tari["Tool"])].copy()
            df_free = df_free.drop(columns=["KEY", "QA_Status"], errors='ignore')
            df_free = df_free[tari.columns.intersection(df_free.columns)]
            tari = pd.concat([tari, df_free], ignore_index=True)

        tool_names = project_data_tools['Tool'].unique()
        coll1, coll2, coll3 = st.columns(3)
        with coll1:
            selected_tool = st.multiselect('Tool', tool_names, default=None)
        if selected_tool:
            t = t[t.Tool.isin(selected_tool)]
            tari = tari[tari.Tool.isin(selected_tool)]
        with coll2:
            qastatus = st.multiselect('QA Status', t.QA_Status.unique().tolist(),
                default=[x for x in t.QA_Status.unique().tolist() if x != 'Rejected_paused'])
        with coll3:
            status_options = ['Complete', 'Incomplete']
            completion = st.multiselect('Completion Status', options=status_options, default=['Complete', 'Incomplete'])

        t = t[(t.QA_Status.isin(qastatus)) & (t.Completion_status.isin(completion))].copy()
        tari = tari.merge(t[['V_ID'] + [c for c in t.columns if c not in tari.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left')
        t = t.merge(tari[['V_ID'] + [c for c in tari.columns if c not in t.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left')

        if list(tool_col_map.values())[0].rsplit('-', 1)[-1] == 'occurance':
            tall2 = t[t["V_ID"].str.startswith(tuple(tari["V_ID"].str.rsplit("-", n=1).str[0].unique()), na=False)]

        tall = t[(t.V_ID.isin(tari.V_ID))].copy()
        tall['d1'] = pd.to_datetime(tall['SubmissionDate'], format='%b %d, %Y %H:%M:%S', errors='coerce').dt.date
        tall['d2'] = pd.to_datetime(tall['SubmissionDate'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce').dt.date
        tall['Date'] = tall.d1.fillna(tall.d2)
        tall['Date'] = pd.to_datetime(tall['Date'])
        tall['Date'] = tall['Date'].dt.strftime('%Y-%m-%d')
        tall = tall.drop(columns=['SubmissionDate', 'occurance', 'd1', 'd2'])

        tari['Date'] = pd.to_datetime(tari['SubmissionDate'], format='mixed', errors='coerce').dt.date
        tari.drop(columns='SubmissionDate', inplace=True)

        dff = tall['Date'].value_counts().reset_index()
        dff.columns = ['Date', 'N']
        dff = dff.sort_values(by='Date', ascending=False)

        fig_timeline = px.area(dff, x='Date', y='N')
        fig_timeline.update_traces(line=dict(color='#0f766e', width=2.5), fillcolor='rgba(15,118,110,0.08)',
            mode='lines+markers', marker=dict(color='#0f766e', size=5, line=dict(width=2, color='rgba(255,255,255,0.8)')))
        fig_timeline.update_layout(xaxis_title='', yaxis_title='Submissions', template='plotly_white', height=320,
            margin=dict(l=40, r=20, t=10, b=30), font=dict(family="Outfit, sans-serif"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(0,0,0,0.03)"), yaxis=dict(gridcolor="rgba(0,0,0,0.05)"))

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
            folium.Choropleth(geo_data=geo, data=counts_df, columns=["Province", "count"],
                key_on="feature.properties.NAME_1", fill_color="YlGnBu",
                fill_opacity=0.8, line_opacity=0.25, nan_fill_color="#EAEAEA",
                nan_fill_opacity=0.65, legend_name="Visits").add_to(m)
            folium.GeoJson(geo, style_function=lambda f: {"color": "#777", "weight": 0.7, "fillOpacity": 0},
                highlight_function=lambda f: {"color": "#111", "weight": 2},
                tooltip=folium.GeoJsonTooltip(fields=["NAME_1", "VISITS"], aliases=["Province:", "Visits:"], sticky=True)).add_to(m)
            return m

        counts = tall.groupby("Province").size().reset_index(name="count")
        counts["Province"] = counts["Province"].astype(str).str.strip()
        counts = counts[["Province", "count"]]
        geo_raw = load_geojson("afghanistan_provinces.geojson")
        m = build_map(geo_raw, counts)

        # ── Compute data_metrics (needed before KPIs and charts) ──
        target = tari.groupby('Tool').size()
        received = tari[tari.QA_Status.notna()].groupby('Tool').size()
        approved = tari[tari.QA_Status == 'Approved'].groupby('Tool').size()
        rejected = tari[tari.QA_Status == 'Rejected'].groupby('Tool').size()
        awaiting = tari[tari.QA_Status.isin(["Not QA'ed Yet", 'Pending'])].groupby('Tool').size()
        data_metrics = pd.DataFrame({'Target': target, 'Received data': received, 'Approved data': approved,
            'Rejected data': rejected, 'Awaiting review': awaiting}).fillna(0).astype(int).reset_index()
        if len(data_metrics) > 1:
            data_metrics.loc['Total'] = data_metrics.sum(numeric_only=True)
            data_metrics.loc['Total', 'Tool'] = 'All Tools'
        data_metrics['DC Completion %'] = ((data_metrics['Received data'] / data_metrics['Target']) * 100).round(2)
        data_metrics['Completed ✅'] = (data_metrics['Target'] == data_metrics['Approved data']).apply(lambda x: '✅' if x else '❌')

        # ── KPI ROW + ANALYTICS CHARTS ──
        total_target = tari.shape[0]
        total_received = tari[tari.QA_Status.isin(qastatus)].shape[0]
        total_remaining = max(0, total_target - total_received)
        g = tari[tari.QA_Status.isin(qastatus)].QA_Status.value_counts().reset_index()
        approved_n = int(g[g['QA_Status'] == 'Approved']['count'].sum()) if 'Approved' in g['QA_Status'].values else 0
        rejected_n = int(g[g['QA_Status'] == 'Rejected']['count'].sum()) if 'Rejected' in g['QA_Status'].values else 0
        dc_pct = round(100 * total_received / total_target) if total_target else 0
        qa_pct = round(100 * approved_n / total_received) if total_received else 0
        rej_pct = round(100 * rejected_n / total_received) if total_received else 0

        ""
        # ── 4 KPIs in horizontal row ──
        st.markdown(f"""<div class="kpi-row">
            <div class="kpi-tile">
                <div class="kpi-tile-label">DC Progress</div>
                <div class="kpi-tile-value" style="color:#0f766e;">{dc_pct}%</div>
                <div class="kpi-tile-sub">{total_received} of {total_target} received</div>
                <div class="kpi-tile-bar"><div class="kpi-tile-bar-fill" style="width:{dc_pct}%;background:linear-gradient(90deg,#0f766e,#14b8a6);"></div></div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-tile-label">QA Approved</div>
                <div class="kpi-tile-value" style="color:#10b981;">{approved_n}</div>
                <div class="kpi-tile-sub">{qa_pct}% approval rate</div>
                <div class="kpi-tile-bar"><div class="kpi-tile-bar-fill" style="width:{qa_pct}%;background:linear-gradient(90deg,#10b981,#34d399);"></div></div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-tile-label">Rejected</div>
                <div class="kpi-tile-value" style="color:#ef4444;">{rejected_n}</div>
                <div class="kpi-tile-sub">{rej_pct}% rejection rate</div>
                <div class="kpi-tile-bar"><div class="kpi-tile-bar-fill" style="width:{rej_pct}%;background:linear-gradient(90deg,#ef4444,#f87171);"></div></div>
            </div>
            <div class="kpi-tile">
                <div class="kpi-tile-label">Remaining</div>
                <div class="kpi-tile-value" style="color:#64748b;">{total_remaining}</div>
                <div class="kpi-tile-sub">Not yet received</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # ── Two analytical charts ──
        chart_col1, chart_col2 = st.columns(2, gap="medium")

        with chart_col1:
            with st.container(border=True):
                dm_chart = data_metrics[data_metrics['Tool'] != 'All Tools'].copy() if 'All Tools' in data_metrics['Tool'].values else data_metrics.copy()
                dm_chart = dm_chart.sort_values('Target', ascending=True).reset_index(drop=True)

                # ── Compute category percentages of each tool's target ──
                dmp = dm_chart.copy()
                dmp['target_safe'] = dmp['Target'].replace(0, 1)
                dmp['remaining_abs'] = (dmp['Target'] - dmp['Received data']).clip(lower=0)
                dmp['pct_approved']  = (dmp['Approved data']  / dmp['target_safe'] * 100).fillna(0)
                dmp['pct_rejected']  = (dmp['Rejected data']  / dmp['target_safe'] * 100).fillna(0)
                dmp['pct_awaiting']  = (dmp['Awaiting review']/ dmp['target_safe'] * 100).fillna(0)
                dmp['pct_remaining'] = (dmp['remaining_abs']  / dmp['target_safe'] * 100).fillna(0)

                # Only label segments large enough to hold the text
                def _labels(series, min_pct=7):
                    return [f"{v:.0f}%" if v >= min_pct else "" for v in series]

                n_tools = max(1, len(dmp))
                # Bar thickness: narrow when only 1-2 tools (so a single bar doesn't
                # dominate a 400px chart), thicker when many tools (so label fits).
                bar_width = 0.45 if n_tools <= 2 else 0.75
                bar_gap   = 0.45 if n_tools <= 2 else 0.18

                fig_tool = go.Figure()
                fig_tool.add_trace(go.Bar(
                    y=dmp['Tool'], x=dmp['pct_approved'], name='Approved',
                    orientation='h', marker_color='#10b981', width=bar_width,
                    customdata=np.stack([dmp['Approved data'], dmp['Target']], axis=-1),
                    text=_labels(dmp['pct_approved']), textposition='inside',
                    insidetextfont=dict(color='white', size=11, family='Outfit'),
                    hovertemplate='<b>%{y}</b><br>Approved: %{x:.1f}%<br>%{customdata[0]:,} of %{customdata[1]:,}<extra></extra>'))
                fig_tool.add_trace(go.Bar(
                    y=dmp['Tool'], x=dmp['pct_rejected'], name='Rejected',
                    orientation='h', marker_color='#ef4444', width=bar_width,
                    customdata=np.stack([dmp['Rejected data'], dmp['Target']], axis=-1),
                    text=_labels(dmp['pct_rejected']), textposition='inside',
                    insidetextfont=dict(color='white', size=11, family='Outfit'),
                    hovertemplate='<b>%{y}</b><br>Rejected: %{x:.1f}%<br>%{customdata[0]:,} of %{customdata[1]:,}<extra></extra>'))
                fig_tool.add_trace(go.Bar(
                    y=dmp['Tool'], x=dmp['pct_awaiting'], name='Awaiting QA',
                    orientation='h', marker_color='#f59e0b', width=bar_width,
                    customdata=np.stack([dmp['Awaiting review'], dmp['Target']], axis=-1),
                    text=_labels(dmp['pct_awaiting']), textposition='inside',
                    insidetextfont=dict(color='white', size=11, family='Outfit'),
                    hovertemplate='<b>%{y}</b><br>Awaiting: %{x:.1f}%<br>%{customdata[0]:,} of %{customdata[1]:,}<extra></extra>'))
                fig_tool.add_trace(go.Bar(
                    y=dmp['Tool'], x=dmp['pct_remaining'], name='Not Received',
                    orientation='h', marker_color='#e2e8f0', width=bar_width,
                    customdata=np.stack([dmp['remaining_abs'], dmp['Target']], axis=-1),
                    text=_labels(dmp['pct_remaining']), textposition='inside',
                    insidetextfont=dict(color='#64748b', size=11, family='Outfit'),
                    hovertemplate='<b>%{y}</b><br>Not received: %{x:.1f}%<br>%{customdata[0]:,} of %{customdata[1]:,}<extra></extra>'))

                # Ensure x-axis fits even if over-collected (>100%)
                stack_max = float((dmp['pct_approved'] + dmp['pct_rejected']
                                   + dmp['pct_awaiting'] + dmp['pct_remaining']).max() or 100)
                x_max = max(100, stack_max) + 3

                # Fixed height so both charts match the timeline/map row
                tool_chart_height = 320

                fig_tool.update_layout(
                    barmode='stack',
                    title=dict(text='Progress by Tool (% of target)',
                               font=dict(size=14, weight=900, family='Outfit')),
                    height=tool_chart_height,
                    margin=dict(l=10, r=20, t=50, b=40),
                    # Enforce a readable minimum font size. 'hide' drops labels that
                    # don't fit rather than shrinking them to unreadable sizes.
                    uniformtext=dict(minsize=11, mode='hide'),
                    template='plotly_white',
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    bargap=bar_gap,
                    legend=dict(orientation='h', y=-0.22, x=0.5, xanchor='center',
                        font=dict(size=10, color='#64748b', family='Outfit')),
                    xaxis=dict(range=[0, x_max], ticksuffix='%',
                               gridcolor='rgba(0,0,0,0.04)', title='',
                               tickfont=dict(size=10, color='#64748b', family='Outfit')),
                    yaxis=dict(gridcolor='rgba(0,0,0,0)', title='',
                               tickfont=dict(size=11, color='#0f172a', family='Outfit')),
                    font=dict(family='Outfit, sans-serif'))

                # Subtle reference line at 100% target
                fig_tool.add_shape(type='line', xref='x', yref='paper',
                    x0=100, x1=100, y0=0, y1=1,
                    line=dict(color='#0f766e', width=1.2, dash='dot'), opacity=0.5)

                st.plotly_chart(fig_tool, use_container_width=True)

        with chart_col2:
            with st.container(border=True):
                if len(tall) > 0 and 'Date' in tall.columns:
                    # ── Build cumulative series from the SAME V_IDs that drive
                    # `total_received` (so the final cumulative value matches the
                    # Sample Tracking table exactly). Each V_ID is counted once,
                    # at the date of its FIRST submission.
                    received_vids = tari.loc[tari.QA_Status.isin(qastatus), 'V_ID'].dropna().unique()
                    _first_sub = (tall[tall['V_ID'].isin(received_vids)]
                                  .sort_values('Date')
                                  .drop_duplicates('V_ID', keep='first'))
                    cum_df = _first_sub.groupby('Date').size().reset_index(name='daily')
                    cum_df['Date'] = pd.to_datetime(cum_df['Date'], errors='coerce')
                    cum_df = cum_df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)
                    cum_df['cumulative'] = cum_df['daily'].cumsum()

                    # Safety: if any received V_ID had no date, pad the last point
                    # so the final cumulative still matches total_received exactly.
                    if len(cum_df) and cum_df['cumulative'].iloc[-1] < total_received:
                        gap = total_received - cum_df['cumulative'].iloc[-1]
                        cum_df.loc[cum_df.index[-1], 'daily']     += gap
                        cum_df.loc[cum_df.index[-1], 'cumulative'] = total_received

                    # Pull planned & actual DC dates from the project row
                    def _pdate(col):
                        if col in project_data.columns and len(project_data):
                            return pd.to_datetime(project_data[col].iloc[0], dayfirst=True, errors='coerce')
                        return pd.NaT
                    planned_start = _pdate('Planned Data Collection-Start')
                    planned_end   = _pdate('Planned Data Collection-End')
                    actual_start  = _pdate('Data Collection-Start')
                    actual_end    = _pdate('Data Collection-End')

                    today = pd.Timestamp.today().normalize()
                    # If DC has an actual end date, collection is officially closed —
                    # no forecasting needed, just show the final state.
                    dc_complete = pd.notna(actual_end)

                    # Anchor start: actual > first submission > planned
                    if pd.notna(actual_start):
                        dc_start = actual_start
                    elif len(cum_df):
                        dc_start = cum_df['Date'].min()
                    else:
                        dc_start = planned_start if pd.notna(planned_start) else today

                    # Average per day (achieved, or being achieved)
                    pace_anchor = actual_end if dc_complete else today
                    days_elapsed = max(1, (pace_anchor - dc_start).days)
                    avg_per_day = total_received / days_elapsed if days_elapsed > 0 else 0
                    est_used = False
                    if avg_per_day <= 0 and not dc_complete:
                        avg_per_day = 20
                        est_used = True

                    # Forecast end date at current pace (only meaningful if DC is still running)
                    remaining = max(0, total_target - total_received)
                    if dc_complete:
                        forecast_end = actual_end
                    else:
                        days_to_finish = (remaining / avg_per_day) if avg_per_day > 0 else 0
                        forecast_end = today + pd.Timedelta(days=int(np.ceil(days_to_finish)))

                    # Required pace to hit planned end date (only when still running)
                    if pd.notna(planned_end) and not dc_complete:
                        days_left_plan = (planned_end - today).days
                        if days_left_plan > 0:
                            required_avg = remaining / days_left_plan
                        else:
                            required_avg = float(remaining)  # past deadline
                    else:
                        days_left_plan = None
                        required_avg = None

                    # Delta vs plan
                    if dc_complete and pd.notna(planned_end):
                        delta_days = (actual_end - planned_end).days
                    elif pd.notna(planned_end):
                        delta_days = (forecast_end - planned_end).days
                    else:
                        delta_days = 0
                    is_behind = delta_days > 0
                    pace_color = '#ef4444' if is_behind else '#10b981'

                    # X-axis end: small buffer past the latest milestone.
                    candidates = [d for d in [forecast_end, planned_end, actual_end] if pd.notna(d)]
                    if len(cum_df):
                        candidates.append(cum_df['Date'].max())
                    latest_event = max(candidates) if candidates else today
                    x_end = latest_event + pd.Timedelta(days=5)

                    # Plotly's add_vline does `Timestamp + int` internally on newer pandas
                    # which now raises — pass ISO strings instead of pd.Timestamps.
                    _fmt = lambda d: d.strftime('%Y-%m-%d') if pd.notna(d) else None
                    today_s        = _fmt(today)
                    forecast_end_s = _fmt(forecast_end)
                    planned_end_s  = _fmt(planned_end)
                    dc_start_s     = _fmt(dc_start)
                    x_end_s        = _fmt(x_end)

                    fig_cum = go.Figure()

                    # Target horizontal line
                    fig_cum.add_hline(
                        y=total_target, line_dash='dot', line_color='#94a3b8', line_width=1.3,
                        annotation_text=f'🎯 Target {total_target:,}',
                        annotation_position='top left',
                        annotation_font=dict(size=10, color='#475569', family='Outfit'))

                    # Actual cumulative (area + line)
                    fig_cum.add_trace(go.Scatter(
                        x=cum_df['Date'], y=cum_df['cumulative'],
                        name='Actual', mode='lines',
                        line=dict(color='#0f766e', width=3, shape='spline'),
                        fill='tozeroy', fillcolor='rgba(15,118,110,0.09)',
                        hovertemplate='<b>%{x|%d %b %Y}</b><br>Received: <b>%{y:,}</b><extra></extra>'))

                    # Today marker point on the actual line
                    if len(cum_df):
                        fig_cum.add_trace(go.Scatter(
                            x=[cum_df['Date'].iloc[-1]], y=[cum_df['cumulative'].iloc[-1]],
                            mode='markers', showlegend=False,
                            marker=dict(size=9, color='#0f766e', line=dict(color='#ffffff', width=2)),
                            hovertemplate='<b>Last submission</b><br>%{x|%d %b %Y}<br>Received: <b>%{y:,}</b><extra></extra>'))

                    # ── Stall segment ──
                    # If the last submission is before today AND collection isn't complete
                    # (neither target-complete nor officially ended), draw a flat dashed
                    # line across the gap so the pause is visible.
                    last_sub_date = cum_df['Date'].max() if len(cum_df) else None
                    stall_days = (today - last_sub_date).days if last_sub_date is not None else 0
                    is_stalled = (last_sub_date is not None
                                  and stall_days >= 1
                                  and total_received < total_target
                                  and not dc_complete)
                    if is_stalled:
                        fig_cum.add_trace(go.Scatter(
                            x=[last_sub_date, today],
                            y=[total_received, total_received],
                            name=f'No collection · {stall_days}d',
                            mode='lines',
                            line=dict(color='#94a3b8', width=2, dash='dot'),
                            hovertemplate='<b>No submissions</b><br>%{x|%d %b %Y}<extra></extra>'))

                    # Current-pace projection: only when DC is still running
                    if not dc_complete:
                        fig_cum.add_trace(go.Scatter(
                            x=[today, forecast_end], y=[total_received, total_target],
                            name=f'Current pace · {avg_per_day:.0f}/day',
                            mode='lines',
                            line=dict(color=pace_color, width=2.3, dash='dash'),
                            hovertemplate='<b>Current-pace projection</b><br>%{x|%d %b %Y} → %{y:,}<extra></extra>'))

                    # Planned end vertical line (use add_shape — add_vline has a bug
                    # doing numeric arithmetic on date x-values in some plotly versions)
                    if pd.notna(planned_end):
                        fig_cum.add_shape(
                            type='line', xref='x', yref='paper',
                            x0=planned_end, x1=planned_end, y0=0, y1=1,
                            line=dict(color='#6366f1', width=1.2, dash='dash'),
                            opacity=0.7)
                        fig_cum.add_annotation(
                            xref='x', yref='paper', x=planned_end, y=1.0,
                            yanchor='bottom', xanchor='center', showarrow=False,
                            text=f'Planned end<br>{planned_end:%d %b}',
                            font=dict(size=9, color='#6366f1', family='Outfit'))

                    # Forecast / Actual end vertical line
                    if dc_complete:
                        fig_cum.add_shape(
                            type='line', xref='x', yref='paper',
                            x0=actual_end, x1=actual_end, y0=0, y1=1,
                            line=dict(color=pace_color, width=1.5, dash='solid'),
                            opacity=0.8)
                        fig_cum.add_annotation(
                            xref='x', yref='paper', x=actual_end, y=0.0,
                            yanchor='top', xanchor='center', showarrow=False,
                            text=f'Actual end<br>{actual_end:%d %b}',
                            font=dict(size=9, color=pace_color, family='Outfit'))
                    else:
                        fig_cum.add_shape(
                            type='line', xref='x', yref='paper',
                            x0=forecast_end, x1=forecast_end, y0=0, y1=1,
                            line=dict(color=pace_color, width=1.2, dash='dash'),
                            opacity=0.7)
                        fig_cum.add_annotation(
                            xref='x', yref='paper', x=forecast_end, y=0.0,
                            yanchor='top', xanchor='center', showarrow=False,
                            text=f'Forecast<br>{forecast_end:%d %b}',
                            font=dict(size=9, color=pace_color, family='Outfit'))

                    # Today dotted vertical (only while DC is running)
                    if not dc_complete:
                        fig_cum.add_shape(
                            type='line', xref='x', yref='paper',
                            x0=today, x1=today, y0=0, y1=1,
                            line=dict(color='#0f172a', width=1, dash='dot'),
                            opacity=0.25)

                    # Status badge text
                    if dc_complete and pd.notna(planned_end):
                        if delta_days > 0:
                            status_txt = f"<b style='color:#ef4444'>⚠ Finished {delta_days}d late</b>"
                        elif delta_days < 0:
                            status_txt = f"<b style='color:#10b981'>✓ Finished {abs(delta_days)}d early</b>"
                        else:
                            status_txt = f"<b style='color:#10b981'>✓ Finished on time</b>"
                    elif pd.notna(planned_end):
                        if delta_days > 0:
                            status_txt = f"<b style='color:#ef4444'>⚠ {delta_days}d behind</b>"
                        elif delta_days < 0:
                            status_txt = f"<b style='color:#10b981'>✓ {abs(delta_days)}d ahead</b>"
                        else:
                            status_txt = f"<b style='color:#10b981'>✓ On track</b>"
                    else:
                        status_txt = "<b style='color:#64748b'>No planned end</b>"

                    if dc_complete:
                        # Closed collection — report final state, no forecast
                        duration_days = max(1, (actual_end - dc_start).days)
                        completion_pct = (total_received / total_target * 100) if total_target else 0
                        info_html = (
                            f"<span style='font-size:10px;color:#64748b;font-weight:700;letter-spacing:0.06em;text-transform:uppercase'>DATA COLLECTION · CLOSED</span><br>"
                            f"<b>Final:</b>&nbsp;<span style='color:#0f766e'>{total_received:,} / {total_target:,} ({completion_pct:.1f}%)</span><br>"
                            f"<b>Duration:</b>&nbsp;{duration_days} days<br>"
                            f"<b>Avg pace:</b>&nbsp;<span style='color:#0f766e'>{avg_per_day:.1f}/day</span><br>"
                            f"<b>Actual end:</b>&nbsp;<span style='color:{pace_color}'>{actual_end:%d %b %Y}</span><br>"
                            f"{status_txt}"
                        )
                        card_x_anchor = actual_end
                    else:
                        # Running collection — show forecast
                        est_tag = " <span style='color:#94a3b8;font-size:9px'>(est.)</span>" if est_used else ""
                        req_line = (f"<b>Required:</b>&nbsp;<span style='color:#6366f1'>{required_avg:.1f}/day</span><br>"
                                    if required_avg is not None else "")
                        info_html = (
                            f"<span style='font-size:10px;color:#64748b;font-weight:700;letter-spacing:0.06em;text-transform:uppercase'>PROGRESS FORECAST</span><br>"
                            f"<b>Current pace:</b>&nbsp;<span style='color:#0f766e'>{avg_per_day:.1f}/day{est_tag}</span><br>"
                            f"{req_line}"
                            f"<b>Forecast end:</b>&nbsp;<span style='color:{pace_color}'>{forecast_end:%d %b %Y}</span><br>"
                            f"{status_txt}"
                        )
                        card_x_anchor = forecast_end

                    fig_cum.add_annotation(
                        xref='x', yref='paper',
                        x=card_x_anchor, y=0.04,
                        xanchor='right', yanchor='bottom',
                        xshift=-10,  # small visual gap left of the anchor line
                        text=info_html, showarrow=False, align='left',
                        font=dict(size=11, family='Outfit', color='#0f172a'),
                        bgcolor='rgba(255,255,255,0.95)', bordercolor='#e2e8f0',
                        borderwidth=1, borderpad=10)

                    # Y-axis: fit whichever is higher — the target or the tallest actual
                    # point — so the line and target are always visible.
                    y_peak = max(float(total_target), float(cum_df['cumulative'].max()) if len(cum_df) else 0.0)
                    y_max = y_peak * 1.10 if y_peak > 0 else 1

                    # Fixed height, matching the tool chart beside it
                    cum_chart_height = 320

                    cum_title = 'Cumulative Progress · Closed' if dc_complete else 'Cumulative Progress & Forecast'
                    fig_cum.update_layout(
                        title=dict(text=cum_title,
                                   font=dict(size=14, weight=900, family='Outfit')),
                        height=cum_chart_height,
                        autosize=True,
                        margin=dict(l=45, r=25, t=55, b=20),
                        template='plotly_white',
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        legend=dict(orientation='h', y=-0.18, x=0.5, xanchor='center',
                            font=dict(size=10, color='#64748b', family='Outfit'),
                            bgcolor='rgba(0,0,0,0)'),
                        xaxis=dict(gridcolor='rgba(0,0,0,0.03)', title='',
                                   range=[(dc_start - pd.Timedelta(days=1)).strftime('%Y-%m-%d'), x_end_s]),
                        yaxis=dict(gridcolor='rgba(0,0,0,0.05)', title='Cumulative Submissions',
                                   range=[0, y_max]),
                        font=dict(family='Outfit, sans-serif'),
                        hovermode='x unified')
                    st.plotly_chart(fig_cum, use_container_width=True)
                else:
                    st.info("No submission dates available for cumulative chart.")

        # ── GEOGRAPHIC COVERAGE + SUBMISSION TIMELINE ──
        colii1, colii2 = st.columns(2)
        with colii1:
            with st.container(border=True):
                st.markdown("### Geographic Coverage")
                st_folium(m, height=320, use_container_width=True, returned_objects=[], key="afg_map")
        with colii2:
            with st.container(border=True):
                st.markdown("### Submission Timeline")
                st.plotly_chart(fig_timeline, use_container_width=True)

        # ── SAMPLE TRACKING TABLE ──
        st.markdown('<div class="section-label">Sample Tracking</div>', unsafe_allow_html=True)
        st.dataframe(data_metrics, hide_index=True, use_container_width=True)

        t = t[t['QA_Status'].isin(qastatus)]
        m_df = tari[~tari.V_ID.isin(t.V_ID)]
        m_df['Type'] = 'Missing Data'
        ext = t[(~t.V_ID.isin(tari.V_ID)) & (t.QA_Status == 'Approved')][['Tool', 'V_ID', 'KEY', 'QA_Status']]
        ext['Type'] = 'Extra data'
        dup = t[t.V_ID.duplicated(keep='first')][['Tool', 'V_ID', 'KEY', 'QA_Status']]
        dup['Type'] = 'Duplicate Data'
        missing = pd.concat([missing, m_df, ext, dup])
        if "Call Status" in tall.columns:
            try: tall2
            except NameError: tall2 = tall
        tall = tall[~tall.KEY.isin(pd.concat([ext.KEY, dup.KEY]))]

        col1, col2 = st.columns(2)
        with col1:
            tari_csv = convert_df_to_csv(tari)
            st.download_button(label="⬇ Download Target Data", data=tari_csv, file_name='Sample_Tracking.csv', mime='text/csv')

        j = project_data['notes'][0]
        if j != "-":
            st.markdown(eval(j[1:-1]), unsafe_allow_html=True)

        # ── SUMMARY GENERATION ──
        st.markdown('<div class="section-label">Summary Generation</div>', unsafe_allow_html=True)
        st.info('Summaries include both "Complete" and "Incomplete" submissions by default. Select only "Complete" for accurate sample tracking.')
        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True):
                disag2 = st.multiselect('Sample Summary', tari.columns.tolist(), def_var0,
                                        help='Create summaries based on selected columns.')
                if disag2:
                    st.markdown("**DC Progress Summary**")
                    total_target_s  = tari.fillna('NAN').groupby(disag2).size()
                    received_data_s = tari.fillna('NAN')[tari['QA_Status'].isin(qastatus)].groupby(disag2).size()
                    summary = pd.DataFrame({
                        'Total_Target': total_target_s,
                        'Received_Data': received_data_s
                    }).fillna(0).astype(int)
                    summary['Remaining'] = summary['Total_Target'] - summary['Received_Data']
                    summary['Completed ✅'] = (summary['Received_Data'] == summary['Total_Target'])\
                                              .apply(lambda x: '✅' if x else '❌')
        
                    excel_like_table(summary, key="sample_summary_grid", height=380)
        with col4:
            with st.container(border=True):
                disag = st.multiselect('Dataset Summary', tall.columns.tolist(), default=def_var1, help='Create summaries based on selected columns.')
                if disag:
                    st.markdown("**Summary**")
                    if len(disag) == 1:
                        disag_t = tall.groupby(disag).size().reset_index().rename(columns={0: 'N'})
                        disag_t.loc[len(disag_t)] = ['Total', disag_t['N'].sum()]
                    else:
                        disag_t = tall.groupby(disag).size().unstack(disag[-1], fill_value=0).reset_index()
                        disag_t.loc['Total'] = disag_t.sum(numeric_only=True)
                    st.dataframe(disag_t)
        if 'tall2' in locals():
            disag_raw = st.multiselect('Tryouts Summary (Phone Surveys)', tall2.columns.tolist(), def_var2,
                help='For phone surveys where multiple attempts to reach respondents may be necessary.')
            if disag_raw:
                st.markdown("**Raw Data (Tryouts)**")
                if len(disag_raw) == 1:
                    disag_traw = tall2.groupby(disag_raw).size().reset_index().rename(columns={0: 'N'})
                    disag_traw.loc[len(disag_traw)] = ['Total', disag_traw['N'].sum()]
                else:
                    disag_traw = tall2.groupby(disag_raw).size().unstack(disag_raw[-1], fill_value=0).reset_index()
                    disag_traw.loc['Total'] = disag_traw.sum(numeric_only=True)
                st.dataframe(disag_traw)

    # ── UPDATE LOGS ──
    def parse_log(log_text):
        log_text = log_text if isinstance(log_text, str) else ""
        parts = [p.strip() for p in re.split(r";;\s*", log_text.strip()) if p.strip()]
        rows = []
        for p in parts:
            if ":" not in p: continue
            ds, msg = p.split(":", 1)
            d = datetime.strptime(ds.strip(), "%d/%m/%Y").date()
            rows.append((d, msg.strip()))
        rows.sort(key=lambda x: x[0])
        return rows
    log_text = project_data.loc[0, "Logs"]
    rows = parse_log(log_text)
    by_day = {}
    for d, msg in rows:
        by_day.setdefault(d, []).append(msg)
    dates = list(by_day.keys())
    total_logs = sum(len(v) for v in by_day.values())
    start_d, end_d = (min(dates), max(dates)) if dates else (None, None)
    header = f"📋 Project Updates · {total_logs} update{'s' if total_logs != 1 else ''}"
    if start_d:
        header += f" · {start_d.strftime('%d %b %Y')} → {end_d.strftime('%d %b %Y')}"
    with st.expander(header, expanded=False):
        days = list(by_day.items())
        for i, (d, msgs) in enumerate(days):
            st.markdown(f"""<div class="upd-day"><div class="upd-date">{d.strftime('%d %b %Y')}</div>
                {''.join([f"<div class='upd-item'><span class='upd-dot'>•</span>{m_item}</div>" for m_item in msgs])}
                </div>{"<div class='upd-sep'></div>" if i < len(days)-1 else ""}""", unsafe_allow_html=True)

    # ── SURVEYOR REPORT (ECD / EFSP) ──
    if main_project in ['ECD', 'EFSP']:
        sr = st.button("Generate Surveyor Performance Report", key="create_report_btn", type="primary")
        if sr and main_project in ['ECD', 'EFSP']:
            qalog2 = pd.merge(tall, qalog[['Issue_Type', 'Issue_Description', 'surveyor_notified', 'surveyor_response', 'issue_resolved', 'KEY_Unique']], on='KEY_Unique', how='left')
            qalog2['severity'] = qalog2['QA_Status'].map({'Rejected': 'High', 'Approved': 'Low', 'Pending': 'Medium'})
            issues = qalog2[['Site_Visit_ID', 'Province', 'Village', 'severity', 'QA_Status', 'Surveyor_Name', 'KEY', 'Date', 'Issue_Type', 'Issue_Description', 'surveyor_notified', 'surveyor_response', 'issue_resolved']].copy()
            summary_sr = (qalog2.groupby('Surveyor_Name').agg(total_submissions=('Surveyor_Name', 'size'),
                rejected_count=('QA_Status', lambda x: (x == 'Rejected').sum()),
                total_feedback_ratio=('Issue_Type', lambda x: x.notna().mean()))
                .assign(rejection_ratio=lambda d: d.rejected_count / d.total_submissions).reset_index())
            hfcsheet = "https://docs.google.com/spreadsheets/d/16EWCV7HTEx729ILvsYa72LkJ1P1Sw7Fo2R0FzXs3GvE/export?format=csv&" + Project_QA_ID3
            hfc = pd.read_csv(hfcsheet)
            hfc = hfc.drop_duplicates(subset='Surveyor_Name')
            summary_sr = pd.merge(summary_sr, hfc, on='Surveyor_Name', how='left').fillna(0)
            issues = issues[issues.Issue_Type.notna()].copy()
            issues["issue_resolved"] = issues["issue_resolved"].fillna("No").replace("", "No")
            for c in ["Issue_Description", "surveyor_response", "Province", "Village", "Site_Visit_ID", "Surveyor_Name", "Issue_Type", "KEY"]:
                issues[c] = issues[c].fillna("")
            issues['Location'] = issues['Province'] + "-" + issues['Village']
            qalog2['Date'] = pd.to_datetime(qalog2['Date'], errors='coerce')
            chart_source = qalog2[['Date', 'QA_Status', 'Surveyor_Name', 'Issue_Type', 'Issue_Description', 'surveyor_response', 'KEY', 'Site_Visit_ID', 'Province', 'Village', 'issue_resolved']].copy()
            chart_source['Date'] = chart_source['Date'].dt.strftime('%Y-%m-%d')
            chart_source = chart_source.dropna(subset=['Date'])
            for c in ['Issue_Type', 'Issue_Description', 'surveyor_response', 'KEY', 'Site_Visit_ID', 'Province', 'Village']:
                chart_source[c] = chart_source[c].fillna('')
            chart_source['issue_resolved'] = chart_source['issue_resolved'].fillna('No').replace('', 'No')
            chart_source['Location'] = chart_source['Province'] + "-" + chart_source['Village']
            chart_source_json = chart_source.to_json(orient='records')

            def score_surveyors(df_s, w_rej=0.5, w_out=0.10, w_out2=0.2, w_fb=0.2):
                df_s = df_s.copy()
                score = 100 - (df_s["rejection_ratio"]*100*w_rej + df_s["hfc_outliers_ratio"]*100*w_out + df_s["ta_outliers"]*100*w_out2 + df_s["total_feedback_ratio"]*100*w_fb)
                df_s["score"] = score.round(1).clip(0, 100)
                conds = [df_s["score"] >= 85, df_s["score"] >= 70, df_s["score"] >= 55]
                df_s["band"] = np.select(conds, ["Excellent", "Good", "Watch"], default="Critical")
                df_s["band_color"] = np.select(conds, ["#10b981", "#3b82f6", "#f59e0b"], default="#ef4444")
                df_s["recommendation"] = np.select(conds, ["Maintain monitoring", "Minor coaching", "Verify records"], default="Urgent Retraining")
                return df_s

            # The HTML report builder is identical to original - keeping it compact
            def build_html_report(project_name, meta, summary_df, issues_df, chart_src_json):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                issues_df, summary_df = issues_df.copy(), summary_df.copy()
                for c in ["Site_Visit_ID", "Location"]:
                    if c not in issues_df.columns: issues_df[c] = ""
                total_issues = len(issues_df)
                resolved_count = int((issues_df.get("issue_resolved") == "Yes").sum()) if total_issues else 0
                pending_count = total_issues - resolved_count
                notified_count = int((issues_df.get("surveyor_notified") == "Yes").sum()) if total_issues else 0
                not_notified_count = int(issues_df["surveyor_response"].fillna("").eq("").sum())
                high_severity = int((issues_df.get("severity") == "High").sum()) if total_issues else 0
                avg_score = float(summary_df["score"].mean()) if len(summary_df) else 0.0
                matrix_df = summary_df.sort_values("score", ascending=True).head(10)
                matrix_rows = "".join(f"""<tr><td><div class="name">{r.Surveyor_Name}</div><div class="muted">ID: SURV-{abs(hash(r.Surveyor_Name)) % 1000}</div></td><td class="c"><div class="score">{r.score}</div><div class="bar"><span style="width:{r.score}%;background:{r.band_color}"></span></div></td><td><span class="pill" style="background:{r.band_color}">{r.band}</span></td><td class="c mono">{int(r.total_submissions)}</td><td class="c mono">{int(r.rejected_count)}</td><td class="c mono red">{(r.rejection_ratio*100):.1f}%</td><td class="c mono blue">{(r.total_feedback_ratio*100):.1f}%</td><td class="c mono blue">{(r.hfc_outliers_ratio*100):.1f}%</td><td class="c mono">{(float(getattr(r,"ta_outliers",0.0))*100):.1f}%</td><td class="rec">{r.recommendation}</td></tr>""" for r in matrix_df.itertuples(index=False))
                issues_json = issues_df.to_json(orient="records")
                return f"""<!doctype html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{project_name} - QA Report</title><script src="https://cdn.jsdelivr.net/npm/chart.js"></script><style>@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');:root{{--bg:#f4f5f7;--card:#fff;--text:#0f172a;--muted:#64748b;--line:#e2e8f0;--issue-bg:#fff7ed;--issue-bd:#fed7aa;--issue-date:#9a3412;--issue-txt:#7c2d12;--resp-bg:#f0fdfa;--resp-bd:#99f6e4;--resp-date:#0f766e;--resp-txt:#334155;}}*{{box-sizing:border-box}}body{{margin:0;font-family:'Outfit',system-ui,sans-serif;background:var(--bg);color:var(--text)}}.wrap{{max-width:1100px;margin:0 auto;padding:18px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px}}.top{{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f766e 100%);color:#fff;border:none;}}.top .muted{{color:rgba(255,255,255,0.6);}}.badge{{display:inline-block;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,0.15);color:#fff;font-size:11px;font-weight:800}}.muted{{color:var(--muted);font-size:12px}}h1{{margin:8px 0 2px;font-size:26px;line-height:1.1}}.btn{{border:0;border-radius:14px;padding:12px 14px;background:#0f766e;color:#fff;font-weight:800;cursor:pointer;font-family:'Outfit'}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}}.kpi .label{{font-size:11px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}}.kpi .val{{font-size:28px;font-weight:900;margin-top:6px;font-family:'JetBrains Mono',monospace}}.bar{{height:7px;background:#eef2f7;border-radius:999px;overflow:hidden;margin-top:8px}}.bar span{{display:block;height:100%}}.tablecard{{margin-top:12px;padding:0;overflow:hidden}}.thead{{padding:14px 18px;border-bottom:1px solid var(--line);background:#fafafa}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px 14px;border-bottom:1px solid #f1f5f9;vertical-align:top;font-size:13px}}th{{text-align:left;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;background:#fafafa}}.c{{text-align:center}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}.name{{font-weight:900}}.score{{font-weight:900}}.pill{{display:inline-block;padding:4px 8px;border-radius:999px;color:#fff;font-size:11px;font-weight:900}}.rec{{color:var(--muted);font-style:italic;font-size:12px}}.red{{color:#dc2626}}.blue{{color:#2563eb}}.filters{{display:grid;grid-template-columns:1fr 180px 220px 140px;gap:10px;margin-top:12px}}input,select{{padding:10px 12px;border:1px solid var(--line);border-radius:12px;font-size:13px;background:#fff;font-family:'Outfit'}}.ghost{{background:#f1f5f9;color:#0f172a}}.ticker tbody tr{{border-bottom:1px dashed #e5e7eb}}.ticker tbody tr:last-child{{border-bottom:none}}.ticker tbody tr td{{padding-top:18px;padding-bottom:18px}}.comment{{margin-top:8px;padding:10px 12px;border-radius:12px;border:1px solid;}}.comment-date{{font-weight:900;font-size:12px}}.comment-body{{margin-top:4px;line-height:1.35;}}.comment-divider{{height:1px;margin:10px 2px;background:linear-gradient(90deg,rgba(148,163,184,0),rgba(148,163,184,0.85),rgba(148,163,184,0))}}.issue-comments .comment{{background:var(--issue-bg);border-color:var(--issue-bd);border-left:4px solid #fb923c;}}.issue-comments .comment-date{{color:var(--issue-date);}}.issue-comments .comment-body{{color:var(--issue-txt);}}.response-comments .comment{{background:var(--resp-bg);border-color:var(--resp-bd);border-left:4px solid #14b8a6;}}.response-comments .comment-date{{color:var(--resp-date);}}.response-comments .comment-body{{color:var(--resp-txt);font-style:italic;}}.awaiting-response{{color:#b91c1c;opacity:0.45;font-style:italic;font-weight:300;}}.charts-row{{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;padding:18px;margin-top:4px;}}.chart-box{{background:#ffffff;border:1px solid var(--line);border-radius:14px;padding:16px;position:relative;}}.chart-box canvas{{width:100%!important;}}@media print{{.no-print{{display:none!important}}body{{background:#fff}}.wrap{{padding:0}}.card{{border:0}}}}@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}.filters{{grid-template-columns:1fr}}.charts-row{{grid-template-columns:1fr}}}}</style></head><body><div class="wrap"><div class="card top"><div><span class="badge">{meta}</span><span class="muted" style="margin-left:10px">Report Generated: {now}</span><h1>{project_name}</h1><div class="muted">Surveyor Quality Matrix + Detailed Feedback Log</div></div><button class="btn no-print" onclick="window.print()">Export PDF</button></div><div class="grid"><div class="card kpi"><div class="label">Overall Quality Score</div><div class="val">{avg_score:.1f} <span class="muted">/ 100</span></div><div class="bar"><span style="width:{avg_score}%;background:#0f766e"></span></div></div><div class="card kpi"><div class="label">Total Recorded Cases</div><div class="val" style="color:#4f46e5">{total_issues}</div><div class="muted">{resolved_count} Resolved • {pending_count} Open</div></div><div class="card kpi"><div class="label">Surveyor Notifications</div><div class="val">{notified_count}</div><div class="muted">Awaiting responses for {not_notified_count} cases.</div></div><div class="card kpi"><div class="label">Critical (High severity)</div><div class="val" style="color:#dc2626">{high_severity}</div><div class="muted">Immediate coaching required</div></div></div><div class="card tablecard"><div class="thead"><div style="font-weight:900">Surveyor Performance Matrix (Worst 10)</div><div class="muted">Lowest quality score surveyors</div></div><div style="overflow:auto"><table><thead><tr><th>Surveyor</th><th class="c">Score</th><th>Band</th><th class="c">Total Subs</th><th class="c">Rej #</th><th class="c">Rej %</th><th class="c">Feedback %</th><th class="c">Data incons. %</th><th class="c">Speed Vio. %</th><th>Action</th></tr></thead><tbody>{matrix_rows}</tbody></table></div></div><div class="card tablecard" style="margin-top:12px"><div class="thead"><div style="font-weight:900;text-align:center">Detailed Feedback Log</div><div class="filters no-print"><input id="q" placeholder="Search logs..."/><select id="fResolved"><option value="">Status: All</option><option value="Yes">Resolved</option><option value="No">Pending</option></select><select id="fSurveyor"><option value="">Surveyor: All</option></select><button class="btn ghost" id="reset" type="button">Clear</button></div></div><div class="charts-row"><div class="chart-box"><canvas id="trendChart"></canvas></div><div class="chart-box"><canvas id="issueTypeChart"></canvas></div></div><div style="overflow:auto"><table class="ticker"><thead><tr><th>Verification Detail</th><th>Surveyor Response</th><th class="c">Severity</th><th class="c">Status</th></tr></thead><tbody id="tbody"></tbody></table></div></div></div><script>const data={issues_json};const chartSource={chart_src_json};const tbody=document.getElementById('tbody');const sSelect=document.getElementById('fSurveyor');const uniq=Array.from(new Set(data.map(x=>x.Surveyor_Name))).filter(Boolean).sort();for(const s of uniq){{const o=document.createElement('option');o.value=s;o.textContent=s;sSelect.appendChild(o);}}function esc(x){{return String(x??"").replace(/[&<>"']/g,m=>({{'"':"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}})[m]);}}function formatComments(raw){{const s=String(raw??"").trim();if(!s)return"";const re=/\\[(\\d{{1,2}}\\/\\d{{1,2}}\\/\\d{{4}})\\]\\s*:?:?\\s*/g;let match,lastIndex=0,lastDate=null;const blocks=[];while((match=re.exec(s))!==null){{if(lastDate!==null){{blocks.push({{date:lastDate,body:s.slice(lastIndex,match.index).trim()}});}}lastDate=match[1];lastIndex=re.lastIndex;}}if(lastDate!==null){{blocks.push({{date:lastDate,body:s.slice(lastIndex).trim()}});}}if(!blocks.length)return esc(s);let html="";for(let i=0;i<blocks.length;i++){{if(i>0)html+='<div class="comment-divider"></div>';html+=`<div class="comment"><div class="comment-date">[${{esc(blocks[i].date)}}]</div><div class="comment-body">${{esc(blocks[i].body)}}</div></div>`;}}return html;}}const barColors=['#0f766e','#f59e0b','#ef4444','#10b981','#3b82f6','#ec4899','#8b5cf6','#14b8a6','#f97316','#64748b'];const ctx1=document.getElementById('trendChart').getContext('2d');const trendChart=new Chart(ctx1,{{type:'line',data:{{labels:[],datasets:[{{label:'Total',data:[],borderColor:'#0f766e',backgroundColor:'rgba(15,118,110,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#0f766e'}},{{label:'Rejected',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#ef4444'}}]}},options:{{responsive:true,maintainAspectRatio:true,plugins:{{title:{{display:true,text:'Daily Submissions',font:{{size:14,weight:'900',family:'Outfit'}}}},legend:{{position:'top',labels:{{usePointStyle:true,pointStyle:'circle',padding:14,font:{{size:11,weight:'700'}}}}}}}},scales:{{x:{{ticks:{{maxRotation:45,font:{{size:9}},maxTicksLimit:15}},grid:{{display:false}}}},y:{{beginAtZero:true,grid:{{color:'#f1f5f9'}}}}}}}}}});const ctx2=document.getElementById('issueTypeChart').getContext('2d');const issueTypeChart=new Chart(ctx2,{{type:'bar',data:{{labels:[],datasets:[{{label:'Count',data:[],backgroundColor:[],borderColor:[],borderWidth:1.5,borderRadius:6,barPercentage:0.7}}]}},options:{{responsive:true,maintainAspectRatio:true,indexAxis:'y',plugins:{{title:{{display:true,text:'Issues by Type',font:{{size:14,weight:'900',family:'Outfit'}}}},legend:{{display:false}}}},scales:{{x:{{beginAtZero:true,grid:{{color:'#f1f5f9'}},ticks:{{stepSize:1}}}},y:{{ticks:{{font:{{size:11,weight:'600'}}}},grid:{{display:false}}}}}}}}}});function updateCharts(sf,qf,rf){{let f=chartSource;if(sf)f=f.filter(r=>r.Surveyor_Name===sf);if(rf)f=f.filter(r=>r.issue_resolved===rf);if(qf){{const q=qf.toLowerCase();f=f.filter(r=>((r.Surveyor_Name||'')+' '+(r.KEY||'')+' '+(r.Issue_Type||'')+' '+(r.Issue_Description||'')).toLowerCase().includes(q));}}const dm={{}};for(const r of f){{if(!r.Date)continue;if(!dm[r.Date])dm[r.Date]={{t:0,r:0}};dm[r.Date].t+=1;if(r.QA_Status==='Rejected')dm[r.Date].r+=1;}}const sd=Object.keys(dm).sort();trendChart.data.labels=sd;trendChart.data.datasets[0].data=sd.map(d=>dm[d].t);trendChart.data.datasets[1].data=sd.map(d=>dm[d].r);trendChart.update();const tm={{}};for(const r of f){{if(!r.Issue_Type)continue;tm[r.Issue_Type]=(tm[r.Issue_Type]||0)+1;}}const st=Object.entries(tm).sort((a,b)=>b[1]-a[1]);issueTypeChart.data.labels=st.map(e=>e[0]);issueTypeChart.data.datasets[0].data=st.map(e=>e[1]);issueTypeChart.data.datasets[0].backgroundColor=st.map((_,i)=>barColors[i%barColors.length]+'cc');issueTypeChart.data.datasets[0].borderColor=st.map((_,i)=>barColors[i%barColors.length]);issueTypeChart.update();}}function render(){{const q=document.getElementById('q').value.toLowerCase();const res=document.getElementById('fResolved').value;const sur=document.getElementById('fSurveyor').value;updateCharts(sur,q,res);const out=[];for(const i of data){{if(res&&i.issue_resolved!==res)continue;if(sur&&i.Surveyor_Name!==sur)continue;if(q){{const blob=((i.Surveyor_Name||"")+' '+(i.KEY||"")+' '+(i.Issue_Type||"")+' '+(i.Issue_Description||"")).toLowerCase();if(!blob.includes(q))continue;}}out.push(`<tr><td><div class="muted" style="font-weight:900;text-transform:uppercase;color:#0f766e">${{esc(i.Surveyor_Name)}}</div><div class="muted">KEY: ${{esc(i.KEY)}}</div><div class="muted">Location: ${{esc(i.Location)}}</div><div style="font-weight:700;margin-top:8px">Issue: <span style="font-weight:400;text-decoration:underline">${{esc(i.Issue_Type)}}</span></div><div class="muted">QA: <span style="font-weight:900;color:${{i.QA_Status==='Rejected'?'#ef4444':'#10b981'}}">${{esc(i.QA_Status)}}</span></div><div class="muted" style="margin-top:8px"><span style="color:#dc2626;font-weight:900">ISSUE:</span><div class="issue-comments">${{formatComments(i.Issue_Description)}}</div></div></td><td><div class="response-comments">${{i.surveyor_response?formatComments(i.surveyor_response):'<div class="awaiting-response">Awaiting response...</div>'}}</div></td><td class="c"><span class="pill" style="background:#e2e8f0;color:#0f172a">${{esc(i.severity)}}</span></td><td class="c"><span class="pill" style="background:${{i.issue_resolved==="Yes"?"#dcfce7":"#ffe4e6"}};color:${{i.issue_resolved==="Yes"?"#166534":"#9f1239"}}">${{i.issue_resolved==="Yes"?"Closed":"Pending"}}</span></td></tr>`);}}tbody.innerHTML=out.join("");}}document.getElementById('q').addEventListener('input',render);document.getElementById('fResolved').addEventListener('input',render);document.getElementById('fSurveyor').addEventListener('input',render);document.getElementById('reset').addEventListener('click',()=>{{document.getElementById('q').value="";document.getElementById('fResolved').value="";document.getElementById('fSurveyor').value="";render();}});render();</script></body></html>"""

            p_name = selected_project
            m_text = "ATR-QA Department"
            summary_scored = score_surveyors(summary_sr, w_rej=0.35, w_out=0.1, w_out2=0.2, w_fb=0.35)
            report_html = build_html_report(p_name, m_text, summary_scored, issues, chart_source_json)
            st.download_button(label="⬇ Download Surveyor Report (HTML)", data=report_html,
                file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html",
                use_container_width=True, type="primary", key="download_report_btn")

    # ── FOOTER ──
    ""
    ""
    st.divider()
    col_foot1, col_foot2, col_foot3 = st.columns([1, 2, 1])
    with col_foot1:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    with col_foot3:
        st.markdown(f"<div style='text-align:right;color:#94a3b8;font-size:11px;padding-top:8px;'>ATR Dashboard · {datetime.now().strftime('%Y')}</div>", unsafe_allow_html=True)
