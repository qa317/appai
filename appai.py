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

st.set_page_config(layout="wide", page_title="ATR Dashboard", page_icon="◈")

# ═══════════════════════════════════════════════════════
#  PREMIUM DARK DASHBOARD THEME
# ═══════════════════════════════════════════════════════
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

:root {
  --bg-primary: #0a0e1a;
  --bg-card: rgba(15,20,40,0.65);
  --bg-card-solid: #0f1428;
  --glass-border: rgba(255,255,255,0.06);
  --glass-shine: rgba(255,255,255,0.08);
  --text-primary: #e8edf5;
  --text-secondary: #7a8baa;
  --text-dim: #4a5675;
  --accent-cyan: #00e5ff;
  --accent-purple: #a78bfa;
  --accent-emerald: #34d399;
  --accent-rose: #fb7185;
  --accent-amber: #fbbf24;
  --accent-blue: #60a5fa;
  --gradient-1: linear-gradient(135deg, #00e5ff 0%, #a78bfa 100%);
  --gradient-2: linear-gradient(135deg, #34d399 0%, #00e5ff 100%);
  --gradient-3: linear-gradient(135deg, #a78bfa 0%, #fb7185 100%);
  --radius: 16px;
  --radius-sm: 10px;
  --shadow: 0 4px 30px rgba(0,0,0,0.4);
  --shadow-glow: 0 0 40px rgba(0,229,255,0.08);
}
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; color: var(--text-primary) !important; }
.stApp, .main, section[data-testid="stSidebar"],
[data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: var(--bg-primary) !important; }
.block-container { padding: 1.2rem 2rem 2rem !important; max-width: 1360px; }
#MainMenu, footer, header { visibility: hidden !important; height: 0 !important; }
[data-testid="stHeader"] { height: 0 !important; }
div[data-testid="stDecoration"], div[data-testid="stToolbar"] { display: none !important; }
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.08); border-radius: 99px; }

.top-bar {
  background: linear-gradient(135deg, rgba(15,20,40,0.9) 0%, rgba(10,14,26,0.95) 100%);
  border: 1px solid var(--glass-border); border-radius: 20px; padding: 22px 30px; margin-bottom: 18px;
  display: flex; align-items: center; justify-content: space-between;
  position: relative; overflow: hidden; box-shadow: var(--shadow), var(--shadow-glow);
}
.top-bar::before { content: ''; position: absolute; top: -50%; left: -20%; width: 60%; height: 200%; background: radial-gradient(ellipse, rgba(0,229,255,0.06) 0%, transparent 70%); pointer-events: none; }
.top-bar::after { content: ''; position: absolute; bottom: -50%; right: -10%; width: 40%; height: 200%; background: radial-gradient(ellipse, rgba(167,139,250,0.05) 0%, transparent 70%); pointer-events: none; }
.top-bar .logo { display: flex; align-items: center; gap: 14px; position: relative; z-index: 1; }
.top-bar .logo-icon { width: 42px; height: 42px; border-radius: 12px; background: var(--gradient-1); display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: 900; color: #0a0e1a; box-shadow: 0 0 20px rgba(0,229,255,0.25); }
.top-bar h1 { font-size: 20px; font-weight: 800; margin: 0; background: var(--gradient-1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; }
.top-bar .sub { color: var(--text-dim); font-size: 12px; font-weight: 400; margin-top: 1px; }
.user-badge { background: rgba(255,255,255,0.04); border: 1px solid var(--glass-border); border-radius: 99px; padding: 7px 16px; font-size: 12px; font-weight: 600; color: var(--accent-cyan); display: flex; align-items: center; gap: 6px; position: relative; z-index: 1; }
.user-badge .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent-emerald); box-shadow: 0 0 8px var(--accent-emerald); }

.sec-head { display: flex; align-items: center; gap: 10px; margin: 28px 0 12px; }
.sec-head .sec-dot { width: 8px; height: 8px; border-radius: 50%; box-shadow: 0 0 12px currentColor; }
.sec-head h2 { font-size: 14px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin: 0; }
.sec-head .sec-line { flex: 1; height: 1px; background: linear-gradient(90deg, var(--glass-border), transparent); }

.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 12px 0; }
@media (max-width: 900px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
.kpi-box { background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: var(--radius); padding: 18px 20px; position: relative; overflow: hidden; box-shadow: var(--shadow); }
.kpi-box::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.kpi-box.cyan::before { background: var(--gradient-2); }
.kpi-box.purple::before { background: var(--gradient-3); }
.kpi-box.emerald::before { background: linear-gradient(90deg, #34d399, #6ee7b7); }
.kpi-box.rose::before { background: linear-gradient(90deg, #fb7185, #fda4af); }
.kpi-box .kpi-label { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.12em; color: var(--text-dim); margin-bottom: 6px; }
.kpi-box .kpi-val { font-family: 'Space Mono', monospace; font-size: 30px; font-weight: 700; line-height: 1; }
.kpi-box .kpi-sub { font-size: 11px; color: var(--text-dim); margin-top: 6px; }
.kpi-box .kpi-glow { position: absolute; bottom: -20px; right: -20px; width: 80px; height: 80px; border-radius: 50%; filter: blur(30px); opacity: 0.15; pointer-events: none; }

.link-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 10px; }
@media (max-width: 900px) { .link-grid { grid-template-columns: repeat(3,1fr); } }
.link-box { background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: 14px; padding: 16px 12px; text-align: center; transition: all .25s ease; box-shadow: var(--shadow); }
.link-box:hover { border-color: rgba(0,229,255,0.2); transform: translateY(-2px); box-shadow: var(--shadow), 0 0 20px rgba(0,229,255,0.06); }
.link-box .lbl { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: .1em; color: var(--text-dim); margin-bottom: 8px; }
.link-box a { display: inline-flex; align-items: center; gap: 4px; color: var(--accent-cyan); font-size: 12px; font-weight: 600; text-decoration: none; }
.link-box a:hover { color: #fff; }
.link-box.na { border-style: dashed; opacity: .4; }
.link-box.na .na-text { font-size: 11px; color: var(--text-dim); font-style: italic; }

.legend-strip { display: flex; gap: 18px; flex-wrap: wrap; align-items: center; padding: 8px 16px; margin-bottom: 4px; background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: var(--radius-sm); font-size: 11px; color: var(--text-dim); }

.archived { background: linear-gradient(135deg, rgba(52,211,153,0.08), rgba(96,165,250,0.06)); border: 1px solid rgba(52,211,153,0.2); border-radius: var(--radius); padding: 24px 28px; margin: 18px 0; }
.archived h3 { color: var(--accent-emerald); margin: 0 0 8px; font-size: 17px; }
.archived p { color: var(--text-secondary); font-size: 13px; line-height: 1.65; margin: 0; }

.upd-day { margin: 10px 0 14px; padding-left: 16px; border-left: 2px solid rgba(0,229,255,0.2); }
.upd-date { font-weight: 700; color: var(--accent-cyan); font-size: 12px; font-family: 'Space Mono', monospace; margin-bottom: 6px; }
.upd-item { margin: 3px 0; color: var(--text-secondary); font-size: 12px; line-height: 1.5; }
.upd-dot { color: var(--text-dim); margin-right: 6px; }
.upd-sep { height: 1px; background: var(--glass-border); margin: 14px 0; }

.login-shell { max-width: 420px; margin: 10vh auto 0; background: var(--bg-card); border: 1px solid var(--glass-border); border-radius: 24px; padding: 40px 34px 30px; text-align: center; box-shadow: var(--shadow), var(--shadow-glow); position: relative; overflow: hidden; }
.login-shell::before { content: ''; position: absolute; top: -40%; left: -30%; width: 80%; height: 180%; background: radial-gradient(ellipse, rgba(0,229,255,0.04), transparent 70%); pointer-events: none; }
.login-shell .l-icon { width: 56px; height: 56px; margin: 0 auto 16px; border-radius: 16px; background: var(--gradient-1); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: 900; color: #0a0e1a; box-shadow: 0 0 30px rgba(0,229,255,0.2); }
.login-shell h2 { font-size: 22px; font-weight: 800; margin: 0; color: var(--text-primary); }
.login-shell .l-sub { font-size: 13px; color: var(--text-dim); margin: 4px 0 20px; }
.login-about { max-width: 420px; margin: 14px auto 0; background: rgba(255,255,255,0.02); border: 1px solid var(--glass-border); border-radius: 16px; padding: 18px 22px; text-align: left; }
.login-about h4 { color: var(--accent-purple); margin: 0 0 6px; font-size: 13px; font-weight: 700; }
.login-about p { font-size: 12px; color: var(--text-dim); line-height: 1.55; margin: 0; }
.err-box { background: rgba(251,113,133,0.08); border: 1px solid rgba(251,113,133,0.2); border-radius: 12px; padding: 14px 18px; margin-top: 12px; text-align: left; }
.err-box strong { color: var(--accent-rose); font-size: 13px; }
.err-box p { color: var(--text-secondary); font-size: 12px; margin: 4px 0 0; }

/* Streamlit overrides */
.stSelectbox > div > div, .stMultiSelect > div > div { background: var(--bg-card-solid) !important; border: 1px solid var(--glass-border) !important; border-radius: var(--radius-sm) !important; color: var(--text-primary) !important; }
.stSelectbox label, .stMultiSelect label { font-size: 11px !important; font-weight: 700 !important; color: var(--text-dim) !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
div[data-testid="stExpander"] { background: var(--bg-card) !important; border: 1px solid var(--glass-border) !important; border-radius: var(--radius) !important; }
div[data-testid="stExpander"] summary { font-weight: 700 !important; color: var(--text-primary) !important; font-size: 13px !important; }
div[data-testid="stExpander"] summary:hover { color: var(--accent-cyan) !important; }
.stDataFrame { border-radius: 12px !important; overflow: hidden; }
.stDataFrame [data-testid="stDataFrameResizable"] { border: 1px solid var(--glass-border) !important; border-radius: 12px !important; }
.stDownloadButton button { background: var(--bg-card-solid) !important; border: 1px solid var(--glass-border) !important; border-radius: var(--radius-sm) !important; color: var(--text-primary) !important; font-weight: 600 !important; transition: all .2s !important; }
.stDownloadButton button:hover { border-color: var(--accent-cyan) !important; box-shadow: 0 0 16px rgba(0,229,255,0.1) !important; }
button[data-testid="stBaseButton-primary"] { background: var(--gradient-1) !important; color: #0a0e1a !important; font-weight: 700 !important; border: none !important; border-radius: var(--radius-sm) !important; }
div[data-testid="stToast"] { background: var(--bg-card-solid) !important; border: 1px solid var(--glass-border) !important; color: var(--text-primary) !important; }
.stAlert { background: rgba(96,165,250,0.06) !important; border: 1px solid rgba(96,165,250,0.15) !important; border-radius: var(--radius-sm) !important; color: var(--text-secondary) !important; }
.stTextInput > div > div > input { background: rgba(255,255,255,0.03) !important; border: 1px solid var(--glass-border) !important; border-radius: var(--radius-sm) !important; color: var(--text-primary) !important; }
.stTextInput > div > div > input:focus { border-color: var(--accent-cyan) !important; box-shadow: 0 0 0 2px rgba(0,229,255,0.1) !important; }
button[kind="formSubmit"], button[data-testid="stFormSubmitButton"] > button { background: var(--gradient-1) !important; color: #0a0e1a !important; font-weight: 700 !important; border: none !important; border-radius: var(--radius-sm) !important; }
.js-plotly-plot .plotly .main-svg { border-radius: 12px; }
</style>
"""
st.markdown(THEME_CSS, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  DATA
# ═══════════════════════════════════════════════════════
csv_url = st.secrets["CSV_URL_MAIN"]
csv_url_tools = st.secrets["CSV_URL_TOOLS"]
csv_url_users = st.secrets["CSV_URL_USERS"]

@st.cache_data(ttl=120)
def load_data():
    return pd.read_csv(csv_url), pd.read_csv(csv_url_tools), pd.read_csv(csv_url_users)

df, df_tools, df_users = load_data()
user_dict = df_users.set_index("users")[["password", "project"]].to_dict(orient="index")

def convert_df_to_csv(dataframe):
    return dataframe.to_csv(index=False, encoding='utf-8')

PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(15,20,40,0.6)",
    plot_bgcolor="rgba(15,20,40,0.3)",
    font=dict(family="Outfit", color="#7a8baa"),
    margin=dict(l=40, r=20, t=30, b=30),
)

def sec_header(title, color="var(--accent-cyan)"):
    st.markdown(f'''<div class="sec-head">
        <div class="sec-dot" style="background:{color};color:{color};"></div>
        <h2 style="color:{color};">{title}</h2>
        <div class="sec-line"></div>
    </div>''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  AUTH
# ═══════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    placeholder = st.empty()
    with placeholder.form("login"):
        st.markdown('''<div class="login-shell">
            <div class="l-icon">◈</div>
            <h2>ATR Consulting</h2>
            <div class="l-sub">Data Collection & QA Progress Tracker</div>
        </div>''', unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In", use_container_width=True)
        st.markdown('''<div class="login-about">
            <h4>◈ About This Platform</h4>
            <p>Track data collection, monitor QA workflows, and generate clear data summaries — powered by real-time insights.</p>
        </div>''', unsafe_allow_html=True)
    if submit:
        if username in user_dict and password == user_dict[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.username = username
            placeholder.empty()
        else:
            st.markdown('''<div class="err-box">
                <strong>Access Denied</strong>
                <p>Incorrect credentials. Please try again.</p>
            </div>''', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
#  DASHBOARD
# ═══════════════════════════════════════════════════════
if st.session_state.logged_in:

    st.markdown(f'''
    <div class="top-bar">
        <div class="logo">
            <div class="logo-icon">◈</div>
            <div>
                <h1>Data Collection & QA Dashboard</h1>
                <div class="sub">ATR Consulting · Real-time Progress Tracker</div>
            </div>
        </div>
        <div class="user-badge"><div class="dot"></div>{st.session_state.username}</div>
    </div>''', unsafe_allow_html=True)

    st.toast("Press **R** to refresh · Figures include complete + incomplete data by default.")

    if user_dict[st.session_state.username]["project"].split(',')[0] == 'All':
        main_project_names = df['Main Project'].unique()
    else:
        main_project_names = df[df['Main Project'].isin(user_dict[st.session_state.username]["project"].split(','))]['Main Project'].unique()

    cols1, _, _ = st.columns([1, 1, 1])
    with cols1:
        main_project = st.selectbox("PROJECT", main_project_names, key="selectbox_1")

    project_data = df[df['Main Project'] == main_project].reset_index()
    project_names = df[df['Main Project'] == main_project]['Project Name'].unique()

    # ── TIMELINE ──
    sec_header("Project Timeline")

    PHASES = [
        ("DC",  "Planned Data Collection-Start", "Planned Data Collection-End", "Data Collection-Start", "Data Collection-End"),
        ("QA",  "Planned data QA-Start", "Planned data QA-End", "data QA-Start", "data QA-End"),
        ("DM",  "Planned DM-Start", "Planned DM-End", "DM-Start", "DM-End"),
        ("A&R", "Planned Reporting-Start", "Planned Reporting-End", "Reporting-Start", "Reporting-End"),
    ]
    today = pd.Timestamp.today().normalize()

    def to_dt(x):
        return pd.to_datetime(x, dayfirst=True, errors="coerce")
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
            if pd.isna(ps) or pd.isna(pe): continue
            is_current = bool(responsible) and phase.lower() in responsible
            y_vals.append(y); y_labels.append(f"{project} — {phase}"); project_y.append(y)
            pc = "rgba(52,211,153,0.9)" if is_current else "rgba(122,139,170,0.5)"
            fig.add_trace(go.Scatter(x=[ps, pe], y=[y, y], mode="lines", line=dict(color=pc, width=3, dash="dash"), showlegend=False, hovertemplate=f"<b>{project}</b><br>{phase}<br>Planned: {ps:%d-%b-%Y} → {pe:%d-%b-%Y}<extra></extra>"))
            if pd.notna(a_s):
                is_running = pd.isna(a_e)
                actual_end = a_e if pd.notna(a_e) else today
                ac = "rgba(52,211,153,0.45)" if is_current else ("rgba(0,229,255,0.45)" if is_running else "rgba(0,229,255,0.25)")
                fig.add_trace(go.Scatter(x=[a_s, actual_end], y=[y, y], mode="lines", line=dict(color=ac, width=10), showlegend=False, hovertemplate=f"<b>{project}</b><br>{phase}<br>Actual: {a_s:%d-%b-%Y} → {actual_end:%d-%b-%Y}{' (running)' if is_running else ''}<extra></extra>"))
                if is_running:
                    fig.add_annotation(x=actual_end, y=y, text="<b>↝</b>", showarrow=False, xanchor="left", yanchor="middle", font=dict(size=22, color="#00e5ff"), bgcolor="rgba(10,14,26,0.7)")
                if not is_running:
                    d = delay_days(pe, a_e)
                    if d > 0:
                        fig.add_trace(go.Scatter(x=[a_e], y=[y], mode="markers+text", marker=dict(size=8, color="#fb7185"), text=[f"+{d}d"], textposition="top center", textfont=dict(size=9, color="#fb7185"), showlegend=False))
                    else:
                        fig.add_annotation(x=a_e, y=y, text="<b>✓</b>", showarrow=False, font=dict(size=16, color="#34d399"), xshift=8)
            y += 1
        if project_y and responsible:
            fig.add_annotation(xref="paper", x=0.92, xanchor="left", y=sum(project_y)/len(project_y), yanchor="middle", text=f"<span style='color:#a78bfa;font-size:11px;'>● <b>{row.get('Responsible')}</b></span>", showarrow=False)
        y += 1.1

    st.markdown('''<div class="legend-strip">
        <span><b style="color:#7a8baa">— —</b> Planned</span>
        <span><b style="color:#00e5ff">▬</b> Actual</span>
        <span style="color:#00e5ff"><b>↝</b> Ongoing</span>
        <span style="color:#34d399"><b>✓</b> On time</span>
        <span style="color:#fb7185"><b>●</b> Delayed</span>
    </div>''', unsafe_allow_html=True)

    fig.add_vline(x=today, line_dash="dot", line_width=1, line_color="rgba(0,229,255,0.3)")
    fig.add_annotation(x=today, y=0.99, xref="x", yref="paper", text="<b>Today</b>", showarrow=False, xanchor="center", yanchor="bottom", font=dict(size=11, color="#00e5ff"))
    fig.update_yaxes(tickmode="array", tickvals=y_vals, ticktext=y_labels, autorange="reversed", title="", tickfont=dict(size=11, color="#7a8baa"), gridcolor="rgba(255,255,255,0.02)")
    max_date = max(project_data[pe_c].max() if pe_c in project_data.columns else pd.Timestamp.today() for _, _, pe_c, _, _ in PHASES)
    fig.update_xaxes(range=[project_data[[ps_c for _, ps_c, _, _, _ in PHASES if ps_c in project_data.columns]].min().min(), max_date + pd.Timedelta(days=20)], showgrid=True, gridcolor="rgba(255,255,255,0.03)", zeroline=False, tickfont=dict(color="#4a5675"))
    fig.update_layout(height=max(380, 20 * len(y_vals)), **PLOT_LAYOUT, margin=dict(l=95, r=80, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

    # ── SUB-PROJECT ──
    sec_header("Round / Sub-Project", "var(--accent-purple)")
    c1, _, _ = st.columns([1, 1, 1])
    with c1:
        selected_project = st.selectbox("SUB-PROJECT", project_names, key="selectbox_2")

    project_data = df[df['Project Name'] == selected_project].reset_index()
    QA_records_link = project_data['QA-Notes link'][0]
    proj_completed = project_data['Completed'][0]
    project_data_tools = df_tools[df_tools['Project Name'] == selected_project].reset_index()
    tool_col_map = project_data_tools.set_index('Tool')['main_cols'].to_dict()

    def compute_vid(row):
        cols_str = tool_col_map.get(row['Tool'], '')
        cols = [c.strip() for c in cols_str.split('-') if c.strip()]
        parts = [str(row[col]).removesuffix('.0') if col in row else "NA" for col in cols]
        return f"{row['Tool']}/{'-'.join(parts)}"

    def_var = project_data['Summary_defualt_var'][0]
    if def_var.strip() == "-":
        def_var0, def_var1, def_var2 = [], [], []
    else:
        parts = def_var.split(";")
        def_var0 = [item.strip() for item in parts[0].split(",")] if len(parts) > 0 else []
        def_var1 = [item.strip() for item in parts[1].split(",")] if len(parts) > 1 else []
        def_var2 = [item.strip() for item in parts[2].split(",")] if len(parts) > 2 else []

    # ── Roadmap ──
    def generate_roadmap(steps, current_step_label):
        try:
            ci = [s['label'] for s in steps].index(current_step_label)
        except ValueError:
            ci = -1
        n = len(steps)
        pct = (ci / (n - 1)) * 100 if ci > 0 and n > 1 else 0
        nodes = ""
        for i, step in enumerate(steps):
            if ci == -1: s = 'upcoming'
            elif i < ci: s = 'completed'
            elif i == ci: s = 'ongoing'
            else: s = 'upcoming'
            if s == 'completed':
                ring = 'border-color:#34d399;'; dot_bg = '#34d399'; txt = 'color:#34d399;font-weight:600;'; anim = ''
            elif s == 'ongoing':
                ring = 'border-color:#00e5ff;box-shadow:0 0 18px rgba(0,229,255,.4);'; dot_bg = '#00e5ff'; txt = 'color:#00e5ff;font-weight:800;'; anim = 'animation:rp 2s ease infinite;'
            else:
                ring = 'border-color:#2a3050;'; dot_bg = '#2a3050'; txt = 'color:#4a5675;'; anim = ''
            sz = '36px' if s == 'ongoing' else '30px'
            nodes += f'''<div style="display:flex;flex-direction:column;align-items:center;width:{100/n}%;">
                <div style="width:{sz};height:{sz};border-radius:50%;border:3px solid;{ring}background:#0a0e1a;display:flex;align-items:center;justify-content:center;z-index:2;">
                    <div style="width:9px;height:9px;background:{dot_bg};border-radius:50%;{anim}"></div>
                </div>
                <p style="margin-top:36px;font-size:10px;{txt}width:85px;text-align:center;line-height:1.3;letter-spacing:.02em;">{step['label']}</p>
            </div>'''
        return f'''<style>@keyframes rp{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.6);opacity:.5}}}}</style>
        <div style="padding:20px 8px;"><div style="position:relative;width:100%;">
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:100%;height:4px;background:#1a2040;border-radius:99px;"></div>
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:{pct}%;height:4px;background:linear-gradient(90deg,#34d399,#00e5ff);border-radius:99px;box-shadow:0 0 12px rgba(0,229,255,.2);"></div>
            <div style="position:relative;display:flex;justify-content:space-between;align-items:flex-start;width:100%;">{nodes}</div>
        </div></div>'''

    steps_data = [{"label": "Form Coding (XLSForm)"}, {"label": "Training"}, {"label": "QA-Manual Checks"}, {"label": "QA-Automated Checks"}, {"label": "QA-Dataset Finalization"}, {"label": "DM-Dataset Finalization"}, {"label": "QA Report"}, {"label": "QA Completion"}]
    current_step = project_data['current_step'][0]
    st.components.v1.html(generate_roadmap(steps_data, current_step), height=150)

    # ── Links ──
    sec_header("Project Links", "var(--accent-blue)")
    links_row = project_data[['Tool link', 'XLSForm link', 'QA-Notes link', 'Tracker link', 'DC Tracker', 'Document folder link']].iloc[0]
    link_labels = {'Tool link': ('🛠', 'Tool'), 'XLSForm link': ('📄', 'XLSForm'), 'QA-Notes link': ('📊', 'QA Notes'), 'Tracker link': ('📈', 'QA Tracker'), 'DC Tracker': ('📈', 'DC Tracker'), 'Document folder link': ('📁', 'Docs')}
    cards = '<div class="link-grid">'
    for col_name, (icon, label) in link_labels.items():
        v = links_row[col_name]
        if pd.notna(v) and str(v).strip():
            cards += f'<div class="link-box"><div class="lbl">{icon} {label}</div><a href="{v}" target="_blank">Open →</a></div>'
        else:
            cards += f'<div class="link-box na"><div class="lbl">{icon} {label}</div><span class="na-text">N/A</span></div>'
    cards += '</div>'
    st.markdown(cards, unsafe_allow_html=True)

    # ═══════════════════════════════════════════
    #  MAIN DATA
    # ═══════════════════════════════════════════
    if proj_completed == "Yes":
        st.markdown('''<div class="archived"><h3>📁 Project Archived</h3>
            <p>This project has been archived. Datasets and trackers remain available for reference.</p></div>''', unsafe_allow_html=True)
    else:
        sec_header("Data Metrics", "var(--accent-emerald)")
        tool_names = project_data_tools['Tool'].unique()
        coll1, coll2, coll3 = st.columns(3)
        with coll1:
            selected_tool = st.multiselect('TOOL', tool_names, default=None)

        missing = pd.DataFrame(columns=['Tool','V_ID','KEY','Type','QA_Status'])
        rawsheet = project_data['raw_sheet'][0]
        Project_QA_ID = project_data['Sampling_ID'][0]
        Project_QA_ID2 = project_data['QAlog_ID'][0]
        Project_QA_ID3 = project_data['HFC_ID'][0]
        raw_sheet_id = rawsheet.split('/d/')[1].split('/')[0]
        csv_url_raw = f"https://docs.google.com/spreadsheets/d/{raw_sheet_id}/export?format=csv&id={raw_sheet_id}&gid=0"
        t = pd.read_csv(csv_url_raw)
        t['KEY_Unique'] = t['KEY']
        qasheet = "https://docs.google.com/spreadsheets/d/1V1SfBZUwHN0NtXFIoiXEh7JGkpTUOLZnGAfFN8QVXYQ/export?format=csv&" + Project_QA_ID2
        qalog = pd.read_csv(qasheet)
        t = pd.merge(t, qalog[['QA_Status','KEY_Unique']].drop_duplicates('KEY_Unique'), on='KEY_Unique', how='left')
        t['QA_Status'] = t['QA_Status'].replace('', "Not QA'ed Yet").fillna("Not QA'ed Yet")
        extra_code = project_data['extra_code'][0]
        Add_cols = project_data_tools['Add_columns'][0]
        t['Completion_status'] = 'Complete'
        if extra_code != '-':
            exec(extra_code)
        t['SubmissionDate'] = pd.to_datetime(t['SubmissionDate'], errors='coerce')
        t = t.sort_values(by=['Completion_status', 'QA_Status'], ascending=True)
        t['occurance'] = None
        for tool, cols in tool_col_map.items():
            group_cols = [c for c in cols.split('-') if c != 'occurance']
            mask = t['Tool'] == tool
            t.loc[mask, 'occurance'] = t.loc[mask].groupby(group_cols).cumcount() + 1
        t['occurance'] = t['occurance'].fillna(9999).astype(int)
        t['V_ID'] = t.apply(compute_vid, axis=1)
        samplingsheet = "https://docs.google.com/spreadsheets/d/1U0Y7TQnTFEg1edMb0IHejOxv9S2YLY2UH-tp1qzXyBg/export?format=csv&" + Project_QA_ID
        tari = pd.read_csv(samplingsheet)
        tari['V_ID'] = tari['Tool'] + "/" + tari['V_ID']
        tari = tari[tari['Skipped'] != "Yes"]
        tari = tari[(tari["Tool"].isin(t["Tool"].unique())) & (tari["Tool"].isin(project_data_tools["Tool"]))]
        df_free = t[t["Tool"].isin(project_data_tools["Tool"]) & ~t["Tool"].isin(tari["Tool"])].copy()
        df_free = df_free.drop(columns=["KEY", "QA_Status"], errors='ignore')
        df_free = df_free[tari.columns.intersection(df_free.columns)]
        tari = pd.concat([tari, df_free], ignore_index=True)
        if selected_tool:
            t = t[t.Tool.isin(selected_tool)]
            tari = tari[tari.Tool.isin(selected_tool)]

        with coll2:
            qastatus = st.multiselect('QA STATUS', t.QA_Status.unique().tolist(), default=[x for x in t.QA_Status.unique().tolist() if x != 'Rejected_paused'])
        with coll3:
            status_options = ['Complete', 'Incomplete']
            completion = st.multiselect('COMPLETION', options=status_options, default=['Complete', 'Incomplete'])

        t = t[(t.QA_Status.isin(qastatus)) & (t.Completion_status.isin(completion))].copy()
        tari = tari.merge(t[['V_ID'] + [c for c in t.columns if c not in tari.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left')
        t = t.merge(tari[['V_ID'] + [c for c in tari.columns if c not in t.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left')
        if list(tool_col_map.values())[0].rsplit('-', 1)[-1] == 'occurance':
            tall2 = t[t["V_ID"].str.startswith(tuple(tari["V_ID"].str.rsplit("-", n=1).str[0].unique()), na=False)]
        tall = t[(t.V_ID.isin(tari.V_ID))].copy()
        tall['d1'] = pd.to_datetime(tall['SubmissionDate'], format='%b %d, %Y %H:%M:%S', errors='coerce').dt.date
        tall['d2'] = pd.to_datetime(tall['SubmissionDate'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce').dt.date
        tall['Date'] = tall.d1.fillna(tall.d2)
        tall['Date'] = pd.to_datetime(tall['Date']).dt.strftime('%Y-%m-%d')
        tall = tall.drop(columns=['SubmissionDate', 'occurance', 'd1', 'd2'])

        dff = tall['Date'].value_counts().reset_index()
        dff.columns = ['Date', 'N']
        dff = dff.sort_values(by='Date')

        fig_tl = go.Figure()
        fig_tl.add_trace(go.Scatter(x=dff['Date'], y=dff['N'], mode='lines+markers',
            line=dict(color='#00e5ff', width=2.5), marker=dict(color='#00e5ff', size=7, line=dict(color='#0a0e1a', width=2)),
            fill='tozeroy', fillcolor='rgba(0,229,255,0.06)', hovertemplate='<b>%{x}</b><br>%{y} submissions<extra></extra>'))
        fig_tl.update_layout(height=300, **PLOT_LAYOUT, xaxis=dict(showgrid=False, tickfont=dict(color="#4a5675")), yaxis=dict(title="Submissions", gridcolor="rgba(255,255,255,0.03)", tickfont=dict(color="#4a5675")))

        @st.cache_data(show_spinner=False)
        def load_geojson(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)

        def build_map(geo_raw, counts_df):
            geo = copy.deepcopy(geo_raw)
            count_map = dict(zip(counts_df["Province"], counts_df["count"]))
            for feat in geo["features"]:
                feat["properties"]["VISITS"] = int(count_map.get(feat["properties"].get("NAME_1"), 0))
            m_obj = folium.Map(location=[34.5, 66.0], zoom_start=5, tiles="CartoDB dark_matter")
            folium.Choropleth(geo_data=geo, data=counts_df, columns=["Province", "count"], key_on="feature.properties.NAME_1", fill_color="YlGnBu", fill_opacity=0.7, line_opacity=0.2, nan_fill_color="#1a2040", nan_fill_opacity=0.65, legend_name="Visits").add_to(m_obj)
            folium.GeoJson(geo, style_function=lambda f: {"color": "#334", "weight": 0.7, "fillOpacity": 0}, highlight_function=lambda f: {"color": "#00e5ff", "weight": 2}, tooltip=folium.GeoJsonTooltip(fields=["NAME_1", "VISITS"], aliases=["Province:", "Visits:"], sticky=True)).add_to(m_obj)
            return m_obj

        counts = t.groupby("Province").size().reset_index(name="count")
        counts["Province"] = counts["Province"].astype(str).str.strip()
        counts = counts[["Province", "count"]]
        geo_raw = load_geojson("afghanistan_provinces.geojson")
        m_map = build_map(geo_raw, counts)

        ci1, ci2 = st.columns(2)
        with ci1:
            st_folium(m_map, height=300, use_container_width=True, returned_objects=[], key="afg_map")
        with ci2:
            st.plotly_chart(fig_tl, use_container_width=True)

        # ── Sample Tracking ──
        sec_header("Sample Tracking", "var(--accent-amber)")
        target_s = tari.groupby('Tool').size()
        received_s = tari[tari.QA_Status.notna()].groupby('Tool').size()
        approved_s = tari[tari.QA_Status == 'Approved'].groupby('Tool').size()
        rejected_s = tari[tari.QA_Status == 'Rejected'].groupby('Tool').size()
        awaiting_s = tari[tari.QA_Status.isin(["Not QA'ed Yet", 'Pending'])].groupby('Tool').size()
        data_metrics = pd.DataFrame({'Target': target_s, 'Received': received_s, 'Approved': approved_s, 'Rejected': rejected_s, 'Awaiting': awaiting_s}).fillna(0).astype(int).reset_index()
        if len(data_metrics) > 1:
            data_metrics.loc['Total'] = data_metrics.sum(numeric_only=True)
            data_metrics.loc['Total', 'Tool'] = 'All Tools'
        data_metrics['DC %'] = ((data_metrics['Received'] / data_metrics['Target']) * 100).round(1)
        data_metrics['Done'] = (data_metrics['Target'] == data_metrics['Approved']).apply(lambda x: '✅' if x else '❌')
        st.dataframe(data_metrics, hide_index=True, use_container_width=True)

        total_target = tari.shape[0]
        total_received = tari[tari.QA_Status.isin(qastatus)].shape[0]
        total_remaining = max(0, total_target - total_received)
        g = tari[tari.QA_Status.isin(qastatus)].QA_Status.value_counts().reset_index()
        approved_n = int(g[g['QA_Status'] == 'Approved']['count'].sum()) if 'Approved' in g['QA_Status'].values else 0
        rejected_n = int(g[g['QA_Status'] == 'Rejected']['count'].sum()) if 'Rejected' in g['QA_Status'].values else 0
        dc_pct = round(100 * total_received / total_target) if total_target else 0
        qa_pct = round(100 * approved_n / total_received) if total_received else 0

        st.markdown(f'''<div class="kpi-row">
            <div class="kpi-box cyan"><div class="kpi-label">DC Progress</div><div class="kpi-val" style="color:#00e5ff;">{dc_pct}%</div><div class="kpi-sub">{total_received} / {total_target} received</div><div class="kpi-glow" style="background:#00e5ff;"></div></div>
            <div class="kpi-box emerald"><div class="kpi-label">Approved</div><div class="kpi-val" style="color:#34d399;">{approved_n}</div><div class="kpi-sub">{qa_pct}% approval rate</div><div class="kpi-glow" style="background:#34d399;"></div></div>
            <div class="kpi-box rose"><div class="kpi-label">Rejected</div><div class="kpi-val" style="color:#fb7185;">{rejected_n}</div><div class="kpi-sub">Requires action</div><div class="kpi-glow" style="background:#fb7185;"></div></div>
            <div class="kpi-box purple"><div class="kpi-label">Remaining</div><div class="kpi-val" style="color:#a78bfa;">{total_remaining}</div><div class="kpi-sub">Pending collection</div><div class="kpi-glow" style="background:#a78bfa;"></div></div>
        </div>''', unsafe_allow_html=True)

        # Donuts
        labels1 = ['Received', 'Remaining']; values1 = [total_received, total_remaining]
        labels2 = g['QA_Status'].tolist(); values2 = g['count'].tolist()

        def make_donut(labels, values, title, colors, note=""):
            pct = round(100 * values[0] / sum(values)) if sum(values) else 0
            fig_d = go.Figure(go.Pie(labels=labels, values=values, hole=0.8, textinfo="percent", textfont=dict(size=10, color="#4a5675"), marker=dict(colors=colors, line=dict(color='#0a0e1a', width=3)), pull=[0.03]+[0]*(len(values)-1), hovertemplate="<b>%{label}</b>: %{percent}<extra></extra>", showlegend=True, sort=False))
            fig_d.update_layout(title=dict(text=title, x=0.5, xanchor="center", font=dict(size=12, color="#e8edf5", family="Outfit")), height=260, **PLOT_LAYOUT, margin=dict(l=0,r=0,t=40,b=0), legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=10, color="#4a5675")), annotations=[dict(text=f"<b style='font-size:26px;color:#e8edf5;font-family:Space Mono'>{pct}%</b><br><span style='font-size:10px;color:#4a5675'>{note}</span>", x=0.5, y=0.5, showarrow=False)])
            return fig_d

        has_both = all(s in completion for s in status_options)
        has_call_status = "Call Status" in t.columns
        terminology = 'Called' if has_both and has_call_status else ('Visited' if has_both else (completion[0] if completion else ''))

        fig1 = make_donut(labels1, values1, "Data Collection", ["#00e5ff", "#1a2040"], terminology)
        fig2 = make_donut(labels2, values2, "QA Progress", ["#34d399", "#fb7185", "#fbbf24", "#2a3050"][:len(g)], "QA'ed")

        cc1, cc2 = st.columns(2)
        with cc1: st.plotly_chart(fig1, use_container_width=True)
        with cc2: st.plotly_chart(fig2, use_container_width=True)

        t = t[t['QA_Status'].isin(qastatus)]
        m_df = tari[~tari.V_ID.isin(t.V_ID)]; m_df['Type'] = 'Missing Data'
        ext = t[(~t.V_ID.isin(tari.V_ID)) & (t.QA_Status == 'Approved')][['Tool','V_ID','KEY','QA_Status']]; ext['Type'] = 'Extra data'
        dup = t[t.V_ID.duplicated(keep='first')][['Tool','V_ID','KEY','QA_Status']]; dup['Type'] = 'Duplicate Data'
        missing = pd.concat([missing, m_df, ext, dup])
        if "Call Status" in tall.columns:
            try: tall2
            except NameError: tall2 = tall
        tall = tall[~tall.KEY.isin(pd.concat([ext.KEY, dup.KEY]))]

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(label="⬇ Download Target Data", data=convert_df_to_csv(tari), file_name='Sample_Tracking.csv', mime='text/csv')

        j = project_data['notes'][0]
        if j != "-":
            st.markdown(eval(j[1:-1]), unsafe_allow_html=True)

        # ── Summary ──
        sec_header("Summary Generation", "var(--accent-purple)")
        st.info('Summaries include both "Complete" and "Incomplete" submissions by default.')

        col3, col4 = st.columns(2)
        with col3:
            disag2 = st.multiselect('SAMPLE SUMMARY', tari.columns.tolist(), def_var0)
            if disag2:
                st.markdown("**DC Progress Summary**")
                tt = tari.fillna('NAN').groupby(disag2).size()
                rd = tari.fillna('NAN')[tari['QA_Status'].isin(qastatus)].groupby(disag2).size()
                sm = pd.DataFrame({'Total_Target': tt, 'Received_Data': rd}).fillna(0).astype(int)
                sm['Remaining'] = sm['Total_Target'] - sm['Received_Data']
                sm['Done'] = (sm['Received_Data'] == sm['Total_Target']).apply(lambda x: '✅' if x else '❌')
                st.dataframe(sm)
        with col4:
            disag = st.multiselect('DATASET SUMMARY', tall.columns.tolist(), default=def_var1)
            if disag:
                st.markdown("**Summary**")
                if len(disag) == 1:
                    dt = tall.groupby(disag).size().reset_index().rename(columns={0: 'N'})
                    dt.loc[len(dt)] = ['Total', dt['N'].sum()]
                else:
                    dt = tall.groupby(disag).size().unstack(disag[-1], fill_value=0).reset_index()
                    dt.loc['Total'] = dt.sum(numeric_only=True)
                st.dataframe(dt)
        if 'tall2' in locals():
            disag_raw = st.multiselect('TRYOUTS SUMMARY', tall2.columns.tolist(), def_var2)
            if disag_raw:
                st.markdown("**Raw Data (Tryouts)**")
                if len(disag_raw) == 1:
                    dr = tall2.groupby(disag_raw).size().reset_index().rename(columns={0: 'N'})
                    dr.loc[len(dr)] = ['Total', dr['N'].sum()]
                else:
                    dr = tall2.groupby(disag_raw).size().unstack(disag_raw[-1], fill_value=0).reset_index()
                    dr.loc['Total'] = dr.sum(numeric_only=True)
                st.dataframe(dr)

    # ── LOGS ──
    def parse_log(log_text):
        log_text = log_text if isinstance(log_text, str) else ""
        parts = [p.strip() for p in re.split(r";;\s*", log_text.strip()) if p.strip()]
        rows_l = []
        for p in parts:
            if ":" not in p: continue
            ds, msg = p.split(":", 1)
            rows_l.append((datetime.strptime(ds.strip(), "%d/%m/%Y").date(), msg.strip()))
        rows_l.sort(key=lambda x: x[0])
        return rows_l

    log_text = project_data.loc[0, "Logs"]
    rows_l = parse_log(log_text)
    by_day = {}
    for d, msg in rows_l:
        by_day.setdefault(d, []).append(msg)
    dates = list(by_day.keys())
    total_logs = sum(len(v) for v in by_day.values())
    s_d, e_d = (min(dates), max(dates)) if dates else (None, None)
    hdr = f"◈ Project Updates · {total_logs} entries"
    if s_d: hdr += f" · {s_d.strftime('%d %b %Y')} → {e_d.strftime('%d %b %Y')}"

    with st.expander(hdr, expanded=False):
        days = list(by_day.items())
        for i, (d, msgs) in enumerate(days):
            st.markdown(f'''<div class="upd-day"><div class="upd-date">{d.strftime('%d %b %Y')}</div>{''.join([f"<div class='upd-item'><span class='upd-dot'>›</span>{mi}</div>" for mi in msgs])}</div>{"<div class='upd-sep'></div>" if i < len(days)-1 else ""}''', unsafe_allow_html=True)

    # ── SURVEYOR REPORT ──
    if main_project in ['ECD', 'EFSP']:
        sr = st.button("Generate Surveyor Performance Report", key="create_report_btn", type="primary")
        if sr:
            qalog2 = pd.merge(tall, qalog[['Issue_Type','Issue_Description','surveyor_notified','surveyor_response','issue_resolved','KEY_Unique']], on='KEY_Unique', how='left')
            qalog2['severity'] = qalog2['QA_Status'].map({'Rejected': 'High', 'Approved': 'Low', 'Pending': 'Medium'})
            issues = qalog2[['Site_Visit_ID','Province','Village','severity','QA_Status','Surveyor_Name','KEY','Date','Issue_Type','Issue_Description','surveyor_notified','surveyor_response','issue_resolved']].copy()
            summary_sr = (qalog2.groupby('Surveyor_Name').agg(total_submissions=('Surveyor_Name','size'), rejected_count=('QA_Status', lambda x: (x=='Rejected').sum()), total_feedback_ratio=('Issue_Type', lambda x: x.notna().mean())).assign(rejection_ratio=lambda d: d.rejected_count/d.total_submissions).reset_index())
            hfcsheet = "https://docs.google.com/spreadsheets/d/16EWCV7HTEx729ILvsYa72LkJ1P1Sw7Fo2R0FzXs3GvE/export?format=csv&" + Project_QA_ID3
            hfc = pd.read_csv(hfcsheet).drop_duplicates(subset='Surveyor_Name')
            summary_sr = pd.merge(summary_sr, hfc, on='Surveyor_Name', how='left').fillna(0)
            issues = issues[issues.Issue_Type.notna()].copy()
            issues["issue_resolved"] = issues["issue_resolved"].fillna("No").replace("", "No")
            for c in ["Issue_Description","surveyor_response","Province","Village","Site_Visit_ID","Surveyor_Name","Issue_Type","KEY"]:
                issues[c] = issues[c].fillna("")
            issues['Location'] = issues['Province'] + "-" + issues['Village']
            qalog2['Date'] = pd.to_datetime(qalog2['Date'], errors='coerce')
            chart_source = qalog2[['Date','QA_Status','Surveyor_Name','Issue_Type','Issue_Description','surveyor_response','KEY','Site_Visit_ID','Province','Village','issue_resolved']].copy()
            chart_source['Date'] = chart_source['Date'].dt.strftime('%Y-%m-%d')
            chart_source = chart_source.dropna(subset=['Date'])
            for c in ['Issue_Type','Issue_Description','surveyor_response','KEY','Site_Visit_ID','Province','Village']:
                chart_source[c] = chart_source[c].fillna('')
            chart_source['issue_resolved'] = chart_source['issue_resolved'].fillna('No').replace('','No')
            chart_source['Location'] = chart_source['Province'] + "-" + chart_source['Village']
            chart_source_json = chart_source.to_json(orient='records')

            def score_surveyors(df_s, w_rej=0.5, w_out=0.10, w_out2=0.2, w_fb=0.2):
                df_s = df_s.copy()
                score = 100 - (df_s["rejection_ratio"]*100*w_rej + df_s["hfc_outliers_ratio"]*100*w_out + df_s["ta_outliers"]*100*w_out2 + df_s["total_feedback_ratio"]*100*w_fb)
                df_s["score"] = score.round(1).clip(0,100)
                conds = [df_s["score"]>=85, df_s["score"]>=70, df_s["score"]>=55]
                df_s["band"] = np.select(conds, ["Excellent","Good","Watch"], default="Critical")
                df_s["band_color"] = np.select(conds, ["#10b981","#3b82f6","#f59e0b"], default="#ef4444")
                df_s["recommendation"] = np.select(conds, ["Maintain monitoring","Minor coaching","Verify records"], default="Urgent Retraining")
                return df_s

            def build_html_report(pn, mt, sdf, idf, csj):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                sdf=sdf.copy(); idf=idf.copy()
                for c in ["Site_Visit_ID","Location"]:
                    if c not in idf.columns: idf[c]=""
                ti=len(idf); rc=int((idf.get("issue_resolved")=="Yes").sum()) if ti else 0; pc=ti-rc
                nc=int((idf.get("surveyor_notified")=="Yes").sum()) if ti else 0; nnc=int(idf["surveyor_response"].fillna("").eq("").sum())
                hs=int((idf.get("severity")=="High").sum()) if ti else 0; avs=float(sdf["score"].mean()) if len(sdf) else 0.0
                mdf=sdf.sort_values("score",ascending=True).head(10)
                mr="".join(f"<tr><td><div class='name'>{r.Surveyor_Name}</div></td><td class='c'><div class='score'>{r.score}</div><div class='bar'><span style='width:{r.score}%;background:{r.band_color}'></span></div></td><td><span class='pill' style='background:{r.band_color}'>{r.band}</span></td><td class='c mono'>{int(r.total_submissions)}</td><td class='c mono'>{int(r.rejected_count)}</td><td class='c mono red'>{(r.rejection_ratio*100):.1f}%</td><td class='c mono blue'>{(r.total_feedback_ratio*100):.1f}%</td><td class='c mono blue'>{(r.hfc_outliers_ratio*100):.1f}%</td><td class='c mono'>{(float(getattr(r,'ta_outliers',0.0))*100):.1f}%</td><td class='rec'>{r.recommendation}</td></tr>" for r in mdf.itertuples(index=False))
                ij=idf.to_json(orient="records")
                return f"""<!doctype html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{pn} - QA Report</title><script src="https://cdn.jsdelivr.net/npm/chart.js"></script><style>:root{{--bg:#f6f7fb;--card:#fff;--text:#0f172a;--muted:#64748b;--line:#e5e7eb;--issue-bg:#fff7ed;--issue-bd:#fed7aa;--issue-date:#9a3412;--issue-txt:#7c2d12;--resp-bg:#f8fafc;--resp-bd:#e2e8f0;--resp-date:#0f766e;--resp-txt:#334155;}}*{{box-sizing:border-box}}body{{margin:0;font-family:system-ui,sans-serif;background:var(--bg);color:var(--text)}}.wrap{{max-width:1100px;margin:0 auto;padding:18px}}.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px}}.top{{display:flex;gap:14px;align-items:flex-start;justify-content:space-between}}.badge{{display:inline-block;padding:6px 10px;border-radius:999px;background:#111827;color:#fff;font-size:11px;font-weight:800}}.muted{{color:var(--muted);font-size:12px}}h1{{margin:8px 0 2px;font-size:26px}}.btn{{border:0;border-radius:14px;padding:12px 14px;background:#111827;color:#fff;font-weight:800;cursor:pointer}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}}.kpi .label{{font-size:11px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}}.kpi .val{{font-size:28px;font-weight:900;margin-top:6px}}.bar{{height:7px;background:#eef2f7;border-radius:999px;overflow:hidden;margin-top:8px}}.bar span{{display:block;height:100%}}.tablecard{{margin-top:12px;padding:0;overflow:hidden}}.thead{{padding:14px 18px;border-bottom:1px solid var(--line);background:#fafafa}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px 14px;border-bottom:1px solid #f1f5f9;vertical-align:top;font-size:13px}}th{{text-align:left;font-size:11px;color:var(--muted);text-transform:uppercase;background:#fafafa}}.c{{text-align:center}}.mono{{font-family:monospace}}.name{{font-weight:900}}.score{{font-weight:900}}.pill{{display:inline-block;padding:4px 8px;border-radius:999px;color:#fff;font-size:11px;font-weight:900}}.rec{{color:var(--muted);font-style:italic;font-size:12px}}.red{{color:#dc2626}}.blue{{color:#2563eb}}.filters{{display:grid;grid-template-columns:1fr 180px 220px 140px;gap:10px;margin-top:12px}}input,select{{padding:10px 12px;border:1px solid var(--line);border-radius:12px;font-size:13px;background:#fff}}.ghost{{background:#f1f5f9;color:#0f172a}}.ticker tbody tr{{border-bottom:1px dashed #e5e7eb}}.ticker tbody tr td{{padding:18px 14px}}.comment{{margin-top:8px;padding:10px 12px;border-radius:12px;border:1px solid}}.comment-date{{font-weight:900;font-size:12px}}.comment-body{{margin-top:4px;line-height:1.35}}.comment-divider{{height:1px;margin:10px 2px;background:linear-gradient(90deg,rgba(148,163,184,0),rgba(148,163,184,.85),rgba(148,163,184,0))}}.issue-comments .comment{{background:var(--issue-bg);border-color:var(--issue-bd);border-left:4px solid #fb923c}}.issue-comments .comment-date{{color:var(--issue-date)}}.issue-comments .comment-body{{color:var(--issue-txt)}}.response-comments .comment{{background:var(--resp-bg);border-color:var(--resp-bd);border-left:4px solid #14b8a6}}.response-comments .comment-date{{color:var(--resp-date)}}.response-comments .comment-body{{color:var(--resp-txt);font-style:italic}}.awaiting-response{{color:#b91c1c;opacity:.45;font-style:italic}}.charts-row{{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;padding:18px}}.chart-box{{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px}}.chart-box canvas{{width:100%!important}}@media print{{.no-print{{display:none!important}}body{{background:#fff}}}}</style></head><body><div class="wrap"><div class="card top"><div><span class="badge">{mt}</span><span class="muted" style="margin-left:10px">Generated: {now}</span><h1>{pn}</h1></div><button class="btn no-print" onclick="window.print()">Export PDF</button></div><div class="grid"><div class="card kpi"><div class="label">Quality Score</div><div class="val">{avs:.1f}/100</div><div class="bar"><span style="width:{avs}%;background:#6366f1"></span></div></div><div class="card kpi"><div class="label">Total Cases</div><div class="val" style="color:#4f46e5">{ti}</div><div class="muted">{rc} Resolved · {pc} Open</div></div><div class="card kpi"><div class="label">Notifications</div><div class="val">{nc}</div><div class="muted">{nnc} awaiting</div></div><div class="card kpi"><div class="label">Critical</div><div class="val" style="color:#dc2626">{hs}</div></div></div><div class="card tablecard"><div class="thead"><div style="font-weight:900">Performance Matrix (Worst 10)</div></div><div style="overflow:auto"><table><thead><tr><th>Surveyor</th><th class="c">Score</th><th>Band</th><th class="c">Subs</th><th class="c">Rej#</th><th class="c">Rej%</th><th class="c">FB%</th><th class="c">Incons%</th><th class="c">Speed%</th><th>Action</th></tr></thead><tbody>{mr}</tbody></table></div></div><div class="card tablecard" style="margin-top:12px"><div class="thead"><div style="font-weight:900;text-align:center">Detailed Feedback Log</div><div class="filters no-print"><input id="q" placeholder="Search..."/><select id="fResolved"><option value="">All</option><option value="Yes">Resolved</option><option value="No">Pending</option></select><select id="fSurveyor"><option value="">All</option></select><button class="btn ghost" id="reset">Clear</button></div></div><div class="charts-row"><div class="chart-box"><canvas id="trendChart"></canvas></div><div class="chart-box"><canvas id="issueTypeChart"></canvas></div></div><div style="overflow:auto"><table class="ticker"><thead><tr><th>Detail</th><th>Response</th><th class="c">Severity</th><th class="c">Status</th></tr></thead><tbody id="tbody"></tbody></table></div></div></div><script>const data={ij};const chartSource={csj};const tbody=document.getElementById('tbody');const sSelect=document.getElementById('fSurveyor');const uniq=Array.from(new Set(data.map(x=>x.Surveyor_Name))).filter(Boolean).sort();for(const s of uniq){{const o=document.createElement('option');o.value=s;o.textContent=s;sSelect.appendChild(o);}}function esc(x){{return String(x??"").replace(/[&<>"']/g,m=>({{'"':"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}})[m]);}}function formatComments(raw){{const s=String(raw??"").trim();if(!s)return"";const re=/\\[(\\d{{1,2}}\\/\\d{{1,2}}\\/\\d{{4}})\\]\\s*:?:?\\s*/g;let match,lastIndex=0,lastDate=null;const blocks=[];while((match=re.exec(s))!==null){{if(lastDate!==null)blocks.push({{date:lastDate,body:s.slice(lastIndex,match.index).trim()}});lastDate=match[1];lastIndex=re.lastIndex;}}if(lastDate!==null)blocks.push({{date:lastDate,body:s.slice(lastIndex).trim()}});if(!blocks.length)return esc(s);let html="";for(let i=0;i<blocks.length;i++){{if(i>0)html+='<div class="comment-divider"></div>';html+=`<div class="comment"><div class="comment-date">[${{esc(blocks[i].date)}}]</div><div class="comment-body">${{esc(blocks[i].body)}}</div></div>`;}}return html;}}const barColors=['#6366f1','#f59e0b','#ef4444','#10b981','#3b82f6','#ec4899','#8b5cf6','#14b8a6','#f97316','#64748b'];const ctx1=document.getElementById('trendChart').getContext('2d');const trendChart=new Chart(ctx1,{{type:'line',data:{{labels:[],datasets:[{{label:'Total',data:[],borderColor:'#4f46e5',backgroundColor:'rgba(79,70,229,.08)',borderWidth:2.5,tension:.3,fill:true,pointRadius:3}},{{label:'Rejected',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,.08)',borderWidth:2.5,tension:.3,fill:true,pointRadius:3}}]}},options:{{responsive:true,plugins:{{title:{{display:true,text:'Total vs Rejected',font:{{size:14,weight:'900'}}}},legend:{{position:'top',labels:{{usePointStyle:true,padding:14}}}}}},scales:{{x:{{ticks:{{maxRotation:45,maxTicksLimit:15}},grid:{{display:false}}}},y:{{beginAtZero:true,grid:{{color:'#f1f5f9'}}}}}}}}}});const ctx2=document.getElementById('issueTypeChart').getContext('2d');const issueTypeChart=new Chart(ctx2,{{type:'bar',data:{{labels:[],datasets:[{{data:[],backgroundColor:[],borderRadius:6,barPercentage:.7}}]}},options:{{responsive:true,indexAxis:'y',plugins:{{title:{{display:true,text:'Issues by Type',font:{{size:14,weight:'900'}}}},legend:{{display:false}}}},scales:{{x:{{beginAtZero:true,ticks:{{stepSize:1}}}},y:{{ticks:{{font:{{size:11}}}},grid:{{display:false}}}}}}}}}});function updateCharts(sf,qf,rf){{let f=chartSource;if(sf)f=f.filter(r=>r.Surveyor_Name===sf);if(rf)f=f.filter(r=>r.issue_resolved===rf);if(qf){{const q=qf.toLowerCase();f=f.filter(r=>((r.Surveyor_Name||'')+(r.KEY||'')+(r.Issue_Type||'')+(r.Issue_Description||'')).toLowerCase().includes(q));}}const dm={{}};for(const r of f){{if(!r.Date)continue;if(!dm[r.Date])dm[r.Date]={{t:0,r:0}};dm[r.Date].t++;if(r.QA_Status==='Rejected')dm[r.Date].r++;}}const sd=Object.keys(dm).sort();trendChart.data.labels=sd;trendChart.data.datasets[0].data=sd.map(d=>dm[d].t);trendChart.data.datasets[1].data=sd.map(d=>dm[d].r);trendChart.update();const tm={{}};for(const r of f){{if(!r.Issue_Type)continue;tm[r.Issue_Type]=(tm[r.Issue_Type]||0)+1;}}const st=Object.entries(tm).sort((a,b)=>b[1]-a[1]);issueTypeChart.data.labels=st.map(e=>e[0]);issueTypeChart.data.datasets[0].data=st.map(e=>e[1]);issueTypeChart.data.datasets[0].backgroundColor=st.map((_,i)=>barColors[i%barColors.length]+'cc');issueTypeChart.update();}}function render(){{const q=document.getElementById('q').value.toLowerCase();const res=document.getElementById('fResolved').value;const sur=document.getElementById('fSurveyor').value;updateCharts(sur,q,res);const out=[];for(const i of data){{if(res&&i.issue_resolved!==res)continue;if(sur&&i.Surveyor_Name!==sur)continue;if(q){{const blob=((i.Surveyor_Name||"")+" "+(i.KEY||"")+" "+(i.Issue_Type||"")+" "+(i.Issue_Description||"")).toLowerCase();if(!blob.includes(q))continue;}}out.push(`<tr><td><div class="muted" style="font-weight:900;text-transform:uppercase;color:#4f46e5">${{esc(i.Surveyor_Name)}}</div><div class="muted">KEY: ${{esc(i.KEY)}}</div><div class="muted">Loc: ${{esc(i.Location)}}</div><div style="font-weight:700;margin-top:8px">Type: <span style="text-decoration:underline">${{esc(i.Issue_Type)}}</span></div><div class="muted">QA: <span style="font-weight:900;color:${{i.QA_Status==='Rejected'?'#ef4444':'#10b981'}}">${{esc(i.QA_Status)}}</span></div><div class="muted" style="margin-top:10px"><span style="color:#dc2626;font-weight:900">ISSUE:</span><div class="issue-comments">${{formatComments(i.Issue_Description)}}</div></div></td><td><div class="response-comments">${{i.surveyor_response?formatComments(i.surveyor_response):'<div class="awaiting-response">Awaiting...</div>'}}</div></td><td class="c"><span class="pill" style="background:#e2e8f0;color:#0f172a">${{esc(i.severity)}}</span></td><td class="c"><span class="pill" style="background:${{i.issue_resolved==="Yes"?"#dcfce7":"#ffe4e6"}};color:${{i.issue_resolved==="Yes"?"#166534":"#9f1239"}}">${{i.issue_resolved==="Yes"?"Closed":"Pending"}}</span></td></tr>`);}}tbody.innerHTML=out.join("");}}document.getElementById('q').addEventListener('input',render);document.getElementById('fResolved').addEventListener('input',render);document.getElementById('fSurveyor').addEventListener('input',render);document.getElementById('reset').addEventListener('click',()=>{{document.getElementById('q').value="";document.getElementById('fResolved').value="";document.getElementById('fSurveyor').value="";render();}});render();</script></body></html>"""

            summary_scored = score_surveyors(summary_sr, w_rej=0.35, w_out=0.1, w_out2=0.2, w_fb=0.35)
            report_html = build_html_report(selected_project, "ATR-QA Department", summary_scored, issues, chart_source_json)
            st.download_button(label="⬇ Download Surveyor Report", data=report_html, file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html", mime="text/html", use_container_width=True, type="primary", key="download_report_btn")

    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    if st.button("◈ Sign Out"):
        st.session_state.logged_in = False
        st.rerun()
