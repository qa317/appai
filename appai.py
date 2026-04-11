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

st.set_page_config(layout="wide", page_title="ATR Dashboard", page_icon="📊")

# ──────────────────────────────────────────────
# GLOBAL THEME CSS
# ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700;0,9..40,900;1,9..40,400&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
  --brand: #7f1d1d;
  --brand-light: #fef2f2;
  --accent: #0d9488;
  --accent2: #4f46e5;
  --surface: #ffffff;
  --surface-alt: #f8fafc;
  --border: #e2e8f0;
  --text: #0f172a;
  --text-muted: #64748b;
  --radius: 16px;
  --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.06);
  --shadow-lg: 0 4px 24px rgba(0,0,0,0.08);
}

html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header {visibility: hidden;}
.block-container {padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 1280px;}

/* Section headers */
.section-title {
  font-size: 15px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  color: var(--brand); margin: 28px 0 10px; padding-bottom: 6px;
  border-bottom: 2px solid var(--brand);
  display: inline-block;
}

/* Cards */
.dash-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  padding: 18px 20px; box-shadow: var(--shadow); transition: box-shadow .2s;
}
.dash-card:hover { box-shadow: var(--shadow-lg); }

/* KPI mini cards */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px,1fr)); gap: 12px; }
.kpi-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  padding: 16px 18px; text-align: center; box-shadow: var(--shadow);
}
.kpi-card .kpi-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em; color: var(--text-muted); }
.kpi-card .kpi-value { font-size: 32px; font-weight: 900; margin: 4px 0 2px; font-family: 'JetBrains Mono', monospace; }
.kpi-card .kpi-sub { font-size: 12px; color: var(--text-muted); }

/* Link cards */
.link-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 10px; }
@media (max-width: 900px) { .link-grid { grid-template-columns: repeat(3,1fr); } }
.link-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 14px;
  padding: 14px; text-align: center; box-shadow: var(--shadow); transition: transform .15s, box-shadow .15s;
}
.link-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-lg); }
.link-card .link-label { font-size: 12px; font-weight: 700; color: var(--text-muted); margin-bottom: 6px; text-transform: uppercase; letter-spacing: .04em; }
.link-card a { color: var(--accent2); font-weight: 600; text-decoration: none; font-size: 13px; }
.link-card a:hover { text-decoration: underline; }
.link-card.na { border-style: dashed; opacity: .55; }

/* Legend bar */
.legend-bar {
  display: flex; gap: 16px; flex-wrap: wrap; align-items: center;
  background: var(--surface-alt); border: 1px solid var(--border); border-radius: 10px;
  padding: 8px 16px; font-size: 12px; color: var(--text-muted); margin-bottom: 6px;
}
.legend-bar b { font-weight: 700; }

/* Archived banner */
.archived-banner {
  background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
  border-left: 5px solid var(--accent2); border-radius: var(--radius);
  padding: 22px 26px; margin: 16px 0;
}
.archived-banner h3 { color: var(--accent2); margin: 0 0 6px; font-size: 18px; }
.archived-banner p { color: var(--text); font-size: 14px; line-height: 1.6; margin: 0; }

/* Login */
.login-wrapper {
  max-width: 440px; margin: 8vh auto; background: var(--surface);
  border: 1px solid var(--border); border-radius: 20px;
  padding: 36px 32px; box-shadow: var(--shadow-lg); text-align: center;
}
.login-wrapper h2 { font-size: 22px; font-weight: 900; color: var(--brand); margin-bottom: 2px; }
.login-wrapper .sub { font-size: 13px; color: var(--text-muted); margin-bottom: 20px; }
.login-about {
  max-width: 440px; margin: 16px auto 0; background: var(--surface-alt);
  border: 1px solid var(--border); border-radius: 16px; padding: 20px 24px; text-align: left;
}
.login-about h4 { color: var(--accent2); margin: 0 0 6px; font-size: 14px; }
.login-about p { font-size: 13px; color: var(--text-muted); line-height: 1.55; margin: 0; }
.error-box {
  background: #fef2f2; border-left: 4px solid #ef4444; border-radius: 10px;
  padding: 14px 18px; margin-top: 10px; text-align: left;
}
.error-box strong { color: #991b1b; }
.error-box p { color: #7f1d1d; font-size: 13px; margin: 4px 0 0; }

/* Top banner */
.top-banner {
  background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 40%, #b91c1c 100%);
  border-radius: 18px; padding: 20px 28px; margin-bottom: 12px;
  display: flex; align-items: center; justify-content: space-between;
}
.top-banner h1 { color: #fff; font-size: 22px; font-weight: 900; margin: 0; letter-spacing: -.3px; }
.top-banner .sub { color: #fecaca; font-size: 12px; margin-top: 2px; }
.top-banner .badge { background: rgba(255,255,255,.15); color: #fff; padding: 5px 12px; border-radius: 999px; font-size: 11px; font-weight: 700; backdrop-filter: blur(4px); }

/* Updates expander */
.upd-day { margin: 10px 0 14px; padding-left: 14px; border-left: 3px solid #e8eef7; }
.upd-date { font-weight: 700; margin-bottom: 6px; color: var(--brand); font-size: 13px; }
.upd-item { margin: 4px 0; color: var(--text); font-size: 13px; }
.upd-dot { color: #94a3b8; margin-right: 8px; }
.upd-sep { height: 1px; background: var(--border); margin: 12px 0; }

/* Streamlit overrides */
.stSelectbox label, .stMultiSelect label { font-size: 13px !important; font-weight: 600 !important; color: var(--text-muted) !important; text-transform: uppercase; letter-spacing: .04em; }
.stDataFrame { border-radius: 12px !important; overflow: hidden; box-shadow: var(--shadow) !important; }
div[data-testid="stExpander"] { border: 1px solid var(--border) !important; border-radius: 14px !important; overflow: hidden; }
div[data-testid="stExpander"] summary { font-weight: 700 !important; }
.stDownloadButton button { border-radius: 10px !important; font-weight: 600 !important; }

/* Plotly chart containers */
.js-plotly-plot .plotly { border-radius: 12px; }
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
        st.markdown("""<div class="login-wrapper">
            <h2>ATR Consulting</h2>
            <div class="sub">Data Collection & QA Progress Tracker</div>
        </div>""", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In", use_container_width=True)
        st.markdown("""<div class="login-about">
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
            st.markdown("""<div class="error-box">
                <strong>Access Denied</strong>
                <p>Incorrect username or password. Please try again.</p>
            </div>""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# MAIN DASHBOARD
# ──────────────────────────────────────────────
if st.session_state.logged_in:

    # Top banner
    st.markdown(f"""
    <div class="top-banner">
        <div>
            <h1>Data Collection & QA Dashboard</h1>
            <div class="sub">ATR Consulting · Progress Tracker</div>
        </div>
        <div class="badge">👤 {st.session_state.username}</div>
    </div>
    """, unsafe_allow_html=True)

    st.toast("Press **R** to refresh · Figures include both complete and incomplete data by default.")

    # Project selector
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

    # ──────────────────────────────────────────
    # PROJECT TIMELINE
    # ──────────────────────────────────────────
    st.markdown('<div class="section-title">Project Timeline</div>', unsafe_allow_html=True)

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

    PLANNED_COLOR = "rgba(100,116,139,0.65)"
    ACTUAL_COLOR  = "rgba(14,165,233,0.30)"
    RUNNING_COLOR = "rgba(14,165,233,0.50)"
    CURRENT_PLANNED_COLOR = "rgba(13,148,136,1.0)"
    CURRENT_ACTUAL_COLOR  = "rgba(13,148,136,0.45)"
    ONTIME_COLOR = "#10b981"
    DELAY_COLOR  = "#ef4444"
    PLANNED_W = 3
    ACTUAL_W  = 10
    GAP = 1.1
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
            if pd.isna(ps) or pd.isna(pe):
                continue
            is_current = bool(responsible) and phase.lower() in responsible
            y_vals.append(y)
            y_labels.append(f"{project} — {phase}")
            project_y.append(y)

            planned_color = CURRENT_PLANNED_COLOR if is_current else PLANNED_COLOR
            fig.add_trace(go.Scatter(
                x=[ps, pe], y=[y, y], mode="lines",
                line=dict(color=planned_color, width=PLANNED_W, dash="dash"),
                showlegend=False,
                hovertemplate=f"<b>{project}</b><br>{phase}<br>Planned: {ps:%d-%b-%Y} → {pe:%d-%b-%Y}<extra></extra>",
            ))

            if pd.notna(a_s):
                is_running = pd.isna(a_e)
                actual_end = a_e if pd.notna(a_e) else today
                actual_color = CURRENT_ACTUAL_COLOR if is_current else (RUNNING_COLOR if is_running else ACTUAL_COLOR)

                fig.add_trace(go.Scatter(
                    x=[a_s, actual_end], y=[y, y], mode="lines",
                    line=dict(color=actual_color, width=ACTUAL_W),
                    showlegend=False,
                    hovertemplate=f"<b>{project}</b><br>{phase}<br>Actual: {a_s:%d-%b-%Y} → {actual_end:%d-%b-%Y}{' (running)' if is_running else ''}<extra></extra>",
                ))

                if is_running:
                    fig.add_annotation(x=actual_end, y=y, text="<b>↝</b>", showarrow=False,
                        xanchor="left", yanchor="middle",
                        font=dict(size=22, color="#7f1d1d"),
                        bgcolor="rgba(255,255,255,0.6)")

                if not is_running:
                    d = delay_days(pe, a_e)
                    if d > 0:
                        fig.add_trace(go.Scatter(
                            x=[a_e], y=[y], mode="markers+text",
                            marker=dict(size=8, color=DELAY_COLOR),
                            text=[f"+{d}d"], textposition="top center",
                            textfont=dict(size=9, color=DELAY_COLOR), showlegend=False,
                        ))
                    else:
                        fig.add_annotation(x=a_e, y=y, text="<b>🗹</b>", showarrow=False,
                            font=dict(size=18, color=ONTIME_COLOR), xshift=8)
            y += 1

        if project_y and responsible:
            fig.add_annotation(
                xref="paper", x=0.9, xanchor="left",
                y=sum(project_y) / len(project_y), yanchor="middle",
                text=f"<span style='color:#7c3aed;font-size:12px;'>● <b>{row.get('Responsible')}</b></span>",
                showarrow=False,
            )
        y += GAP

    st.markdown("""<div class="legend-bar">
        <span><b style="color:#94a3b8">— — —</b> Planned</span>
        <span><b style="color:#0ea5e9">▬</b> Actual</span>
        <span style="color:#0ea5e9"><b>↝</b> Ongoing</span>
        <span style="color:#10b981"><b>🗹</b> On time</span>
        <span style="color:#ef4444"><b>●</b> Delayed</span>
    </div>""", unsafe_allow_html=True)

    fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.4)
    fig.add_annotation(x=today, y=0.99, xref="x", yref="paper",
        text="<b><i>Today</i></b>", showarrow=False, xanchor="center", yanchor="bottom",
        font=dict(size=12, color="#0d9488"))

    fig.update_yaxes(tickmode="array", tickvals=y_vals, ticktext=y_labels, autorange="reversed", title="")

    max_date = max(project_data[pe_c].max() if pe_c in project_data.columns else pd.Timestamp.today() for _, _, pe_c, _, _ in PHASES)
    fig.update_xaxes(
        range=[project_data[[ps_c for _, ps_c, _, _, _ in PHASES if ps_c in project_data.columns]].min().min(),
               max_date + pd.Timedelta(days=20)],
        showgrid=True, gridcolor="rgba(0,0,0,0.04)", zeroline=False,
    )
    fig.update_layout(
        height=max(380, 20 * len(y_vals)),
        margin=dict(l=95, r=80, t=20, b=10),
        plot_bgcolor="white", paper_bgcolor="white", hovermode="closest",
        font=dict(family="DM Sans"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ──────────────────────────────────────────
    # SUB-PROJECT
    # ──────────────────────────────────────────
    st.markdown('<div class="section-title">Round / Sub-Project</div>', unsafe_allow_html=True)
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

    # ──────────────────────────────────────────
    # ROADMAP
    # ──────────────────────────────────────────
    def generate_stylish_horizontal_roadmap_html(steps, current_step_label):
        processed_steps = []
        try:
            current_index = [s['label'] for s in steps].index(current_step_label)
        except ValueError:
            current_index = -1

        for i, step in enumerate(steps):
            if current_index == -1:
                status = 'upcoming'
            elif i < current_index:
                status = 'completed'
            elif i == current_index:
                status = 'ongoing'
            else:
                status = 'upcoming'
            processed_steps.append({'label': step['label'], 'status': status})

        num_steps = len(processed_steps)
        completed_steps = sum(1 for s in processed_steps if s['status'] == 'completed')
        progress_percentage = (completed_steps / (num_steps - 1)) * 100 if num_steps > 1 else 0

        nodes_html = ""
        for i, step in enumerate(processed_steps):
            s = step['status']
            if s == 'completed':
                dot = '<div style="width:10px;height:10px;background:#0d9488;border-radius:50%;"></div>'
                ring = 'border-color:#0d9488;'
                txt_style = 'color:#0d9488;font-weight:600;'
            elif s == 'ongoing':
                dot = '<div style="width:10px;height:10px;background:#4f46e5;border-radius:50%;animation:pulse 2s ease infinite;"></div>'
                ring = 'border-color:#4f46e5;box-shadow:0 0 16px rgba(79,70,229,.35);'
                txt_style = 'color:#4f46e5;font-weight:800;'
            else:
                dot = '<div style="width:8px;height:8px;background:#cbd5e1;border-radius:50%;"></div>'
                ring = 'border-color:#cbd5e1;'
                txt_style = 'color:#94a3b8;'

            nodes_html += f"""
            <div style="display:flex;flex-direction:column;align-items:center;width:{100/num_steps}%;transition:transform .2s;">
                <div style="width:{'38px' if s=='ongoing' else '32px'};height:{'38px' if s=='ongoing' else '32px'};
                    border-radius:50%;border:3px solid;{ring}background:#fff;
                    display:flex;align-items:center;justify-content:center;z-index:2;">
                    {dot}
                </div>
                <p style="margin-top:40px;font-size:11px;{txt_style}width:90px;text-align:center;line-height:1.3;">
                    {step['label']}
                </p>
            </div>"""

        pw = f"calc({progress_percentage}%)" if num_steps > 1 else "0%"

        return f"""
        <style>@keyframes pulse{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.5);opacity:.6}}}}</style>
        <div style="max-width:100%;margin:0 auto;padding:24px 8px;">
            <div style="position:relative;width:100%;">
                <div style="position:absolute;top:50%;transform:translateY(-50%);width:100%;height:6px;background:#e2e8f0;border-radius:99px;"></div>
                <div style="position:absolute;top:50%;transform:translateY(-50%);width:{pw};height:6px;
                    background:linear-gradient(90deg,#0d9488,#14b8a6);border-radius:99px;transition:width .5s;"></div>
                <div style="position:relative;display:flex;justify-content:space-between;align-items:flex-start;width:100%;">
                    {nodes_html}
                </div>
            </div>
        </div>"""

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
    current_step = project_data['current_step'][0]
    roadmap_html = generate_stylish_horizontal_roadmap_html(steps_data, current_step)
    st.components.v1.html(roadmap_html, height=160)

    # ──────────────────────────────────────────
    # PROJECT LINKS
    # ──────────────────────────────────────────
    st.markdown('<div class="section-title">Project Links</div>', unsafe_allow_html=True)

    links_row = project_data[['Tool link', 'XLSForm link', 'QA-Notes link', 'Tracker link', 'DC Tracker', 'Document folder link']].iloc[0]
    link_labels = {
        'Tool link': ('🛠', 'Tool'),
        'XLSForm link': ('📄', 'XLSForm'),
        'QA-Notes link': ('📊', 'QA Notes'),
        'Tracker link': ('📈', 'QA Tracker'),
        'DC Tracker': ('📈', 'DC Tracker'),
        'Document folder link': ('📁', 'Docs'),
    }

    cards_html = '<div class="link-grid">'
    for col_name, (icon, label) in link_labels.items():
        value = links_row[col_name]
        if pd.notna(value) and str(value).strip():
            cards_html += f"""<div class="link-card">
                <div class="link-label">{icon} {label}</div>
                <a href="{value}" target="_blank">Open →</a>
            </div>"""
        else:
            cards_html += f"""<div class="link-card na">
                <div class="link-label">{icon} {label}</div>
                <span style="font-size:12px;color:#94a3b8;font-style:italic;">N/A</span>
            </div>"""
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # ──────────────────────────────────────────
    # ARCHIVED OR DATA METRICS
    # ──────────────────────────────────────────
    if proj_completed == "Yes":
        st.markdown("""<div class="archived-banner">
            <h3>📁 Project Archived</h3>
            <p>This project has been archived. For complete information on sampling and site visits,
            please refer to the Document field. Relevant datasets and trackers are also available.</p>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-title">Data Metrics</div>', unsafe_allow_html=True)

        tool_names = project_data_tools['Tool'].unique()
        coll1, coll2, coll3 = st.columns(3)
        with coll1:
            selected_tool = st.multiselect('Tool', tool_names, default=None)

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
        t['QA_Status'] = t['QA_Status'].replace('', "Not QA'ed Yet")
        t['QA_Status'] = t['QA_Status'].fillna("Not QA'ed Yet")

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
            qastatus = st.multiselect(
                'QA Status',
                t.QA_Status.unique().tolist(),
                default=[x for x in t.QA_Status.unique().tolist() if x != 'Rejected_paused']
            )
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

        dff = tall['Date'].value_counts().reset_index()
        dff.columns = ['Date', 'N']
        dff = dff.sort_values(by='Date', ascending=False)

        fig_timeline = px.line(dff, x='Date', y='N')
        fig_timeline.update_traces(mode='lines+markers',
            marker=dict(color='#7f1d1d', size=8),
            line=dict(color='#b91c1c', width=2))
        fig_timeline.update_layout(
            xaxis_title='', yaxis_title='Submissions',
            template='plotly_white', height=300,
            margin=dict(l=40, r=20, t=10, b=30),
            font=dict(family="DM Sans"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        )

        # Map
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
                geo_data=geo, data=counts_df, columns=["Province", "count"],
                key_on="feature.properties.NAME_1", fill_color="YlGnBu",
                fill_opacity=0.8, line_opacity=0.25, nan_fill_color="#EAEAEA",
                nan_fill_opacity=0.65, legend_name="Visits",
            ).add_to(m)
            folium.GeoJson(
                geo, style_function=lambda f: {"color": "#777", "weight": 0.7, "fillOpacity": 0},
                highlight_function=lambda f: {"color": "#111", "weight": 2},
                tooltip=folium.GeoJsonTooltip(fields=["NAME_1", "VISITS"], aliases=["Province:", "Visits:"], sticky=True),
            ).add_to(m)
            return m

        counts = t.groupby("Province").size().reset_index(name="count")
        counts["Province"] = counts["Province"].astype(str).str.strip()
        counts = counts[["Province", "count"]]
        geo_raw = load_geojson("afghanistan_provinces.geojson")
        m = build_map(geo_raw, counts)

        colii1, colii2 = st.columns(2)
        with colii1:
            st_folium(m, height=300, use_container_width=True, returned_objects=[], key="afg_map")
        with colii2:
            st.plotly_chart(fig_timeline, use_container_width=True)

        # ──────────────────────────────────────
        # SAMPLE TRACKING
        # ──────────────────────────────────────
        st.markdown('<div class="section-title">Sample Tracking</div>', unsafe_allow_html=True)

        target = tari.groupby('Tool').size()
        received = tari[tari.QA_Status.notna()].groupby('Tool').size()
        approved = tari[tari.QA_Status == 'Approved'].groupby('Tool').size()
        rejected = tari[tari.QA_Status == 'Rejected'].groupby('Tool').size()
        awaiting = tari[tari.QA_Status.isin(["Not QA'ed Yet", 'Pending'])].groupby('Tool').size()

        data_metrics = pd.DataFrame({
            'Target': target, 'Received data': received, 'Approved data': approved,
            'Rejected data': rejected, 'Awaiting review': awaiting
        }).fillna(0).astype(int).reset_index()

        if len(data_metrics) > 1:
            data_metrics.loc['Total'] = data_metrics.sum(numeric_only=True)
            data_metrics.loc['Total', 'Tool'] = 'All Tools'

        data_metrics['DC Completion %'] = ((data_metrics['Received data'] / data_metrics['Target']) * 100).round(2)
        data_metrics['Completed ✅'] = (data_metrics['Target'] == data_metrics['Approved data']).apply(lambda x: '✅' if x else '❌')
        st.dataframe(data_metrics, hide_index=True, use_container_width=True)

        # KPI cards
        total_target = tari.shape[0]
        total_received = tari[tari.QA_Status.isin(qastatus)].shape[0]
        total_remaining = max(0, total_target - total_received)
        g = tari[tari.QA_Status.isin(qastatus)].QA_Status.value_counts().reset_index()
        approved_n = int(g[g['QA_Status'] == 'Approved']['count'].sum()) if 'Approved' in g['QA_Status'].values else 0
        rejected_n = int(g[g['QA_Status'] == 'Rejected']['count'].sum()) if 'Rejected' in g['QA_Status'].values else 0

        dc_pct = round(100 * total_received / total_target) if total_target else 0
        qa_pct = round(100 * approved_n / total_received) if total_received else 0

        st.markdown(f"""<div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">DC Progress</div>
                <div class="kpi-value" style="color:#0d9488">{dc_pct}%</div>
                <div class="kpi-sub">{total_received} / {total_target} received</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">QA Approved</div>
                <div class="kpi-value" style="color:#10b981">{approved_n}</div>
                <div class="kpi-sub">{qa_pct}% approval rate</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Rejected</div>
                <div class="kpi-value" style="color:#ef4444">{rejected_n}</div>
                <div class="kpi-sub">Requires re-collection</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Remaining</div>
                <div class="kpi-value" style="color:#64748b">{total_remaining}</div>
                <div class="kpi-sub">Not yet received</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Donut charts
        labels1 = ['Received', 'Remaining']
        values1 = [total_received, total_remaining]
        labels2 = g['QA_Status'].tolist()
        values2 = g['count'].tolist()

        def make_donut(labels, values, title, colors, note=""):
            pct = round(100 * values[0] / sum(values)) if sum(values) else 0
            fig = go.Figure(go.Pie(
                labels=labels, values=values, hole=0.78,
                textinfo="percent", textfont=dict(size=11, color="#64748b"),
                marker=dict(colors=colors, line=dict(color="#fff", width=3)),
                pull=[0.04] + [0] * (len(values) - 1),
                hovertemplate="<b>%{label}</b>: %{percent}<extra></extra>",
                showlegend=True, sort=False,
            ))
            fig.update_layout(
                title=dict(text=title, x=0.5, xanchor="center", font=dict(size=13, color="#0f172a", family="DM Sans")),
                height=260, margin=dict(l=0, r=0, t=45, b=0),
                template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=11, color="#64748b")),
                annotations=[dict(
                    text=f"<b style='font-size:24px;color:#0f172a'>{pct}%</b><br><span style='font-size:10px;color:#94a3b8'>{note}</span>",
                    x=0.5, y=0.5, showarrow=False,
                )]
            )
            return fig

        has_both = all(status in completion for status in status_options)
        has_call_status = "Call Status" in t.columns
        if has_both and has_call_status:
            terminology = 'Called'
        elif has_both:
            terminology = 'Visited'
        else:
            terminology = completion[0] if completion else ''

        fig1 = make_donut(labels1, values1, "Data Collection", ["#0d9488", "#e2e8f0"], terminology)
        fig2 = make_donut(labels2, values2, "QA Progress", ["#10b981", "#ef4444", "#f59e0b", "#cbd5e1"][:len(g)], "QA'ed")

        cols_chart = st.columns(2)
        with cols_chart[0]:
            st.plotly_chart(fig1, use_container_width=True)
        with cols_chart[1]:
            st.plotly_chart(fig2, use_container_width=True)

        t = t[t['QA_Status'].isin(qastatus)]
        m_df = tari[~tari.V_ID.isin(t.V_ID)]
        m_df['Type'] = 'Missing Data'
        ext = t[(~t.V_ID.isin(tari.V_ID)) & (t.QA_Status == 'Approved')][['Tool', 'V_ID', 'KEY', 'QA_Status']]
        ext['Type'] = 'Extra data'
        dup = t[t.V_ID.duplicated(keep='first')][['Tool', 'V_ID', 'KEY', 'QA_Status']]
        dup['Type'] = 'Duplicate Data'
        missing = pd.concat([missing, m_df, ext, dup])

        if "Call Status" in tall.columns:
            try:
                tall2
            except NameError:
                tall2 = tall

        tall = tall[~tall.KEY.isin(pd.concat([ext.KEY, dup.KEY]))]

        col1, col2 = st.columns(2)
        with col1:
            tari_csv = convert_df_to_csv(tari)
            st.download_button(label="⬇ Download Target Data", data=tari_csv, file_name='Sample_Tracking.csv', mime='text/csv')

        # Notes
        j = project_data['notes'][0]
        if j != "-":
            st.markdown(eval(j[1:-1]), unsafe_allow_html=True)

        # ──────────────────────────────────────
        # SUMMARY GENERATION
        # ──────────────────────────────────────
        st.markdown('<div class="section-title">Summary Generation</div>', unsafe_allow_html=True)
        st.info('Summaries include both "Complete" and "Incomplete" submissions by default. Select only "Complete" for accurate sample tracking.')

        col3, col4 = st.columns(2)
        with col3:
            disag2 = st.multiselect('Sample Summary', tari.columns.tolist(), def_var0, help='Create summaries based on selected columns.')
            if disag2:
                st.markdown("**DC Progress Summary**")
                total_target_s = tari.fillna('NAN').groupby(disag2).size()
                received_data_s = tari.fillna('NAN')[tari['QA_Status'].isin(qastatus)].groupby(disag2).size()
                summary = pd.DataFrame({'Total_Target': total_target_s, 'Received_Data': received_data_s}).fillna(0).astype(int)
                summary['Remaining'] = summary['Total_Target'] - summary['Received_Data']
                summary['Completed ✅'] = (summary['Received_Data'] == summary['Total_Target']).apply(lambda x: '✅' if x else '❌')
                st.dataframe(summary)

        with col4:
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

    # ──────────────────────────────────────────
    # UPDATE LOGS
    # ──────────────────────────────────────────
    def parse_log(log_text):
        log_text = log_text if isinstance(log_text, str) else ""
        parts = [p.strip() for p in re.split(r";;\s*", log_text.strip()) if p.strip()]
        rows = []
        for p in parts:
            if ":" not in p:
                continue
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
            st.markdown(
                f"""<div class="upd-day">
                    <div class="upd-date">{d.strftime('%d %b %Y')}</div>
                    {''.join([f"<div class='upd-item'><span class='upd-dot'>•</span>{m_item}</div>" for m_item in msgs])}
                </div>{"<div class='upd-sep'></div>" if i < len(days)-1 else ""}""",
                unsafe_allow_html=True
            )

    # ──────────────────────────────────────────
    # SURVEYOR REPORT (ECD / EFSP)
    # ──────────────────────────────────────────
    if main_project in ['ECD', 'EFSP']:
        sr = st.button("Generate Surveyor Performance Report", key="create_report_btn", type="primary")

        if sr and main_project in ['ECD', 'EFSP']:
            qalog2 = pd.merge(
                tall,
                qalog[['Issue_Type', 'Issue_Description', 'surveyor_notified', 'surveyor_response', 'issue_resolved', 'KEY_Unique']],
                on='KEY_Unique', how='left'
            )
            qalog2['severity'] = qalog2['QA_Status'].map({'Rejected': 'High', 'Approved': 'Low', 'Pending': 'Medium'})
            issues = qalog2[['Site_Visit_ID', 'Province', 'Village', 'severity', 'QA_Status', 'Surveyor_Name', 'KEY', 'Date',
                'Issue_Type', 'Issue_Description', 'surveyor_notified', 'surveyor_response', 'issue_resolved']].copy()

            summary_sr = (
                qalog2.groupby('Surveyor_Name')
                .agg(
                    total_submissions=('Surveyor_Name', 'size'),
                    rejected_count=('QA_Status', lambda x: (x == 'Rejected').sum()),
                    total_feedback_ratio=('Issue_Type', lambda x: x.notna().mean())
                )
                .assign(rejection_ratio=lambda d: d.rejected_count / d.total_submissions)
                .reset_index()
            )
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
            chart_source = qalog2[['Date', 'QA_Status', 'Surveyor_Name', 'Issue_Type', 'Issue_Description',
                'surveyor_response', 'KEY', 'Site_Visit_ID', 'Province', 'Village', 'issue_resolved']].copy()
            chart_source['Date'] = chart_source['Date'].dt.strftime('%Y-%m-%d')
            chart_source = chart_source.dropna(subset=['Date'])
            for c in ['Issue_Type', 'Issue_Description', 'surveyor_response', 'KEY', 'Site_Visit_ID', 'Province', 'Village']:
                chart_source[c] = chart_source[c].fillna('')
            chart_source['issue_resolved'] = chart_source['issue_resolved'].fillna('No').replace('', 'No')
            chart_source['Location'] = chart_source['Province'] + "-" + chart_source['Village']
            chart_source_json = chart_source.to_json(orient='records')

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
                df_s["recommendation"] = np.select(conds, ["Maintain monitoring", "Minor coaching", "Verify records"], default="Urgent Retraining")
                return df_s

            def build_html_report(project_name, meta, summary_df, issues_df, chart_src_json):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                issues_df = issues_df.copy()
                summary_df = summary_df.copy()
                for c in ["Site_Visit_ID", "Location"]:
                    if c not in issues_df.columns:
                        issues_df[c] = ""

                total_issues = len(issues_df)
                resolved_count = int((issues_df.get("issue_resolved") == "Yes").sum()) if total_issues else 0
                pending_count = total_issues - resolved_count
                notified_count = int((issues_df.get("surveyor_notified") == "Yes").sum()) if total_issues else 0
                not_notified_count = int(issues_df["surveyor_response"].fillna("").eq("").sum())
                high_severity = int((issues_df.get("severity") == "High").sum()) if total_issues else 0
                avg_score = float(summary_df["score"].mean()) if len(summary_df) else 0.0

                matrix_df = summary_df.sort_values("score", ascending=True).head(10)
                matrix_rows = "".join(
                    f"""<tr>
                        <td><div class="name">{r.Surveyor_Name}</div><div class="muted">ID: SURV-{abs(hash(r.Surveyor_Name)) % 1000}</div></td>
                        <td class="c"><div class="score">{r.score}</div><div class="bar"><span style="width:{r.score}%;background:{r.band_color}"></span></div></td>
                        <td><span class="pill" style="background:{r.band_color}">{r.band}</span></td>
                        <td class="c mono">{int(r.total_submissions)}</td>
                        <td class="c mono">{int(r.rejected_count)}</td>
                        <td class="c mono red">{(r.rejection_ratio * 100):.1f}%</td>
                        <td class="c mono blue">{(r.total_feedback_ratio * 100):.1f}%</td>
                        <td class="c mono blue">{(r.hfc_outliers_ratio * 100):.1f}%</td>
                        <td class="c mono">{(float(getattr(r, "ta_outliers", 0.0)) * 100):.1f}%</td>
                        <td class="rec">{r.recommendation}</td>
                    </tr>"""
                    for r in matrix_df.itertuples(index=False)
                )
                issues_json = issues_df.to_json(orient="records")

                return f"""<!doctype html>
<html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{project_name} - QA Report</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
:root{{--bg:#f6f7fb;--card:#fff;--text:#0f172a;--muted:#64748b;--line:#e2e8f0;
--issue-bg:#fff7ed;--issue-bd:#fed7aa;--issue-date:#9a3412;--issue-txt:#7c2d12;
--resp-bg:#f8fafc;--resp-bd:#e2e8f0;--resp-date:#0f766e;--resp-txt:#334155;}}
*{{box-sizing:border-box}}
body{{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:var(--bg);color:var(--text)}}
.wrap{{max-width:1100px;margin:0 auto;padding:18px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px}}
.top{{display:flex;gap:14px;align-items:flex-start;justify-content:space-between}}
.badge{{display:inline-block;padding:6px 10px;border-radius:999px;background:#111827;color:#fff;font-size:11px;font-weight:800}}
.muted{{color:var(--muted);font-size:12px}}
h1{{margin:8px 0 2px;font-size:26px;line-height:1.1}}
.btn{{border:0;border-radius:14px;padding:12px 14px;background:#111827;color:#fff;font-weight:800;cursor:pointer}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}}
.kpi .label{{font-size:11px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}}
.kpi .val{{font-size:28px;font-weight:900;margin-top:6px}}
.bar{{height:7px;background:#eef2f7;border-radius:999px;overflow:hidden;margin-top:8px}}
.bar span{{display:block;height:100%}}
.tablecard{{margin-top:12px;padding:0;overflow:hidden}}
.thead{{padding:14px 18px;border-bottom:1px solid var(--line);background:#fafafa}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:12px 14px;border-bottom:1px solid #f1f5f9;vertical-align:top;font-size:13px}}
th{{text-align:left;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;background:#fafafa}}
.c{{text-align:center}}.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}
.name{{font-weight:900}}.score{{font-weight:900}}
.pill{{display:inline-block;padding:4px 8px;border-radius:999px;color:#fff;font-size:11px;font-weight:900}}
.rec{{color:var(--muted);font-style:italic;font-size:12px}}
.red{{color:#dc2626}}.blue{{color:#2563eb}}
.filters{{display:grid;grid-template-columns:1fr 180px 220px 140px;gap:10px;margin-top:12px}}
input,select{{padding:10px 12px;border:1px solid var(--line);border-radius:12px;font-size:13px;background:#fff}}
.ghost{{background:#f1f5f9;color:#0f172a}}
.ticker tbody tr{{border-bottom:1px dashed #e5e7eb}}.ticker tbody tr:last-child{{border-bottom:none}}
.ticker tbody tr td{{padding-top:18px;padding-bottom:18px}}
.comment{{margin-top:8px;padding:10px 12px;border-radius:12px;border:1px solid;}}
.comment-date{{font-weight:900;font-size:12px;letter-spacing:.02em;}}.comment-body{{margin-top:4px;line-height:1.35;}}
.comment-divider{{height:1px;margin:10px 2px;background:linear-gradient(90deg,rgba(148,163,184,0),rgba(148,163,184,0.85),rgba(148,163,184,0));}}
.issue-comments .comment{{background:var(--issue-bg);border-color:var(--issue-bd);border-left:4px solid #fb923c;}}
.issue-comments .comment-date{{color:var(--issue-date);}}.issue-comments .comment-body{{color:var(--issue-txt);}}
.response-comments .comment{{background:var(--resp-bg);border-color:var(--resp-bd);border-left:4px solid #14b8a6;}}
.response-comments .comment-date{{color:var(--resp-date);}}.response-comments .comment-body{{color:var(--resp-txt);font-style:italic;}}
.awaiting-response{{color:#b91c1c;opacity:0.45;font-style:italic;font-weight:300;}}
.charts-row{{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;padding:18px;margin-top:4px;}}
.chart-box{{background:#ffffff;border:1px solid var(--line);border-radius:14px;padding:16px;position:relative;}}
.chart-box canvas{{width:100%!important;}}
@media print{{.no-print{{display:none!important}}body{{background:#fff}}.wrap{{padding:0}}.card{{border:0}}}}
@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}.filters{{grid-template-columns:1fr}}.charts-row{{grid-template-columns:1fr}}}}
</style></head><body>
<div class="wrap">
<div class="card top"><div><span class="badge">{meta}</span><span class="muted" style="margin-left:10px">Report Generated: {now}</span>
<h1>{project_name}</h1><div class="muted">Surveyor Quality Matrix + Detailed Feedback Log</div></div>
<button class="btn no-print" onclick="window.print()">Export PDF</button></div>
<div class="grid">
<div class="card kpi"><div class="label">Overall Quality Score</div><div class="val">{avg_score:.1f} <span class="muted">/ 100</span></div><div class="bar"><span style="width:{avg_score}%;background:#6366f1"></span></div></div>
<div class="card kpi"><div class="label">Total Recorded Cases</div><div class="val" style="color:#4f46e5">{total_issues}</div><div class="muted">{resolved_count} Resolved • {pending_count} Open</div></div>
<div class="card kpi"><div class="label">Surveyor Notifications</div><div class="val">{notified_count}</div><div class="muted">Awaiting responses for {not_notified_count} cases.</div></div>
<div class="card kpi"><div class="label">Critical (High severity)</div><div class="val" style="color:#dc2626">{high_severity}</div><div class="muted">Immediate coaching required</div></div>
</div>
<div class="card tablecard"><div class="thead"><div style="font-weight:900">Surveyor Performance Matrix (Worst 10)</div><div class="muted">Lowest quality score surveyors</div></div>
<div style="overflow:auto"><table><thead><tr><th>Surveyor</th><th class="c">Score</th><th>Band</th><th class="c">Total Subs</th><th class="c">Rej #</th><th class="c">Rej %</th><th class="c">Feedback %</th><th class="c">Data incons. %</th><th class="c">Speed Vio. %</th><th>Action</th></tr></thead>
<tbody>{matrix_rows}</tbody></table></div></div>
<div class="card tablecard" style="margin-top:12px"><div class="thead"><div style="font-weight:900;text-align:center">Detailed Feedback Log</div>
<div class="filters no-print"><input id="q" placeholder="Search logs..."/><select id="fResolved"><option value="">Status: All</option><option value="Yes">Resolved</option><option value="No">Pending</option></select>
<select id="fSurveyor"><option value="">Surveyor: All</option></select><button class="btn ghost" id="reset" type="button">Clear</button></div></div>
<div class="charts-row"><div class="chart-box"><canvas id="trendChart"></canvas></div><div class="chart-box"><canvas id="issueTypeChart"></canvas></div></div>
<div style="overflow:auto"><table class="ticker"><thead><tr><th>Verification Detail</th><th>Surveyor Response</th><th class="c">Severity</th><th class="c">Status</th></tr></thead><tbody id="tbody"></tbody></table></div></div></div>
<script>
const data={issues_json};const chartSource={chart_src_json};
const tbody=document.getElementById('tbody');const sSelect=document.getElementById('fSurveyor');
const uniq=Array.from(new Set(data.map(x=>x.Surveyor_Name))).filter(Boolean).sort();
for(const s of uniq){{const o=document.createElement('option');o.value=s;o.textContent=s;sSelect.appendChild(o);}}
function esc(x){{return String(x??"").replace(/[&<>"']/g,m=>({{'"':"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}})[m]);}}
function formatComments(raw){{const s=String(raw??"").trim();if(!s)return"";const re=/\\[(\\d{{1,2}}\\/\\d{{1,2}}\\/\\d{{4}})\\]\\s*:?:?\\s*/g;let match,lastIndex=0,lastDate=null;const blocks=[];while((match=re.exec(s))!==null){{if(lastDate!==null){{blocks.push({{date:lastDate,body:s.slice(lastIndex,match.index).trim()}});}}lastDate=match[1];lastIndex=re.lastIndex;}}if(lastDate!==null){{blocks.push({{date:lastDate,body:s.slice(lastIndex).trim()}});}}if(!blocks.length)return esc(s);let html="";for(let i=0;i<blocks.length;i++){{if(i>0)html+='<div class="comment-divider"></div>';html+=`<div class="comment"><div class="comment-date">[${{esc(blocks[i].date)}}]</div><div class="comment-body">${{esc(blocks[i].body)}}</div></div>`;}}return html;}}
const barColors=['#6366f1','#f59e0b','#ef4444','#10b981','#3b82f6','#ec4899','#8b5cf6','#14b8a6','#f97316','#64748b','#a855f7','#06b6d4','#e11d48','#84cc16','#0ea5e9'];
const ctx1=document.getElementById('trendChart').getContext('2d');
const trendChart=new Chart(ctx1,{{type:'line',data:{{labels:[],datasets:[{{label:'Total Data Count',data:[],borderColor:'#4f46e5',backgroundColor:'rgba(79,70,229,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#4f46e5'}},{{label:'Rejected Count',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#ef4444'}}]}},options:{{responsive:true,maintainAspectRatio:true,plugins:{{title:{{display:true,text:'Daily Submissions: Total vs Rejected',font:{{size:14,weight:'900'}},color:'#0f172a',padding:{{bottom:10}}}},legend:{{position:'top',labels:{{usePointStyle:true,pointStyle:'circle',padding:14,font:{{size:11,weight:'700'}}}}}},tooltip:{{mode:'index',intersect:false}}}},interaction:{{mode:'nearest',axis:'x',intersect:false}},scales:{{x:{{title:{{display:true,text:'Date',font:{{size:11,weight:'800'}},color:'#64748b'}},ticks:{{maxRotation:45,font:{{size:9}},maxTicksLimit:15}},grid:{{display:false}}}},y:{{title:{{display:true,text:'Count',font:{{size:11,weight:'800'}},color:'#64748b'}},beginAtZero:true,grid:{{color:'#f1f5f9'}}}}}}}}}});
const ctx2=document.getElementById('issueTypeChart').getContext('2d');
const issueTypeChart=new Chart(ctx2,{{type:'bar',data:{{labels:[],datasets:[{{label:'Issue Count',data:[],backgroundColor:[],borderColor:[],borderWidth:1.5,borderRadius:6,barPercentage:0.7}}]}},options:{{responsive:true,maintainAspectRatio:true,indexAxis:'y',plugins:{{title:{{display:true,text:'Issues by Type',font:{{size:14,weight:'900'}},color:'#0f172a',padding:{{bottom:10}}}},legend:{{display:false}},tooltip:{{callbacks:{{label:function(ctx){{return' Count: '+ctx.parsed.x;}}}}}}}},scales:{{x:{{title:{{display:true,text:'Count',font:{{size:11,weight:'800'}},color:'#64748b'}},beginAtZero:true,grid:{{color:'#f1f5f9'}},ticks:{{stepSize:1}}}},y:{{ticks:{{font:{{size:11,weight:'600'}},color:'#334155'}},grid:{{display:false}}}}}}}}}});
function updateCharts(surveyorFilter,searchFilter,resolvedFilter){{let filtered=chartSource;if(surveyorFilter){{filtered=filtered.filter(r=>r.Surveyor_Name===surveyorFilter);}}if(resolvedFilter){{filtered=filtered.filter(r=>r.issue_resolved===resolvedFilter);}}if(searchFilter){{const q=searchFilter.toLowerCase();filtered=filtered.filter(r=>{{const blob=((r.Surveyor_Name||'')+' '+(r.KEY||'')+' '+(r.Site_Visit_ID||'')+' '+(r.QA_Status||'')+' '+(r.Location||'')+' '+(r.Issue_Type||'')+' '+(r.Issue_Description||'')+' '+(r.surveyor_response||'')).toLowerCase();return blob.includes(q);}});}}const dateMap={{}};for(const r of filtered){{if(!r.Date)continue;if(!dateMap[r.Date])dateMap[r.Date]={{total:0,rejected:0}};dateMap[r.Date].total+=1;if(r.QA_Status==='Rejected')dateMap[r.Date].rejected+=1;}}const sortedDates=Object.keys(dateMap).sort();const filterLabel=surveyorFilter?' — '+surveyorFilter:(searchFilter?' — "'+searchFilter+'"':' (All Surveyors)');trendChart.options.plugins.title.text='Daily Submissions: Total vs Rejected'+filterLabel;trendChart.data.labels=sortedDates;trendChart.data.datasets[0].data=sortedDates.map(d=>dateMap[d].total);trendChart.data.datasets[1].data=sortedDates.map(d=>dateMap[d].rejected);trendChart.update();const typeMap={{}};for(const r of filtered){{const t=r.Issue_Type;if(!t)continue;typeMap[t]=(typeMap[t]||0)+1;}}const sortedTypes=Object.entries(typeMap).sort((a,b)=>b[1]-a[1]);const typeLabels=sortedTypes.map(e=>e[0]);const typeCounts=sortedTypes.map(e=>e[1]);const typeBg=typeLabels.map((_,i)=>barColors[i%barColors.length]+'cc');const typeBd=typeLabels.map((_,i)=>barColors[i%barColors.length]);issueTypeChart.options.plugins.title.text='Issues by Type'+filterLabel;issueTypeChart.data.labels=typeLabels;issueTypeChart.data.datasets[0].data=typeCounts;issueTypeChart.data.datasets[0].backgroundColor=typeBg;issueTypeChart.data.datasets[0].borderColor=typeBd;issueTypeChart.update();}}
function render(){{const q=document.getElementById('q').value.toLowerCase();const res=document.getElementById('fResolved').value;const sur=document.getElementById('fSurveyor').value;updateCharts(sur,q,res);const out=[];for(const i of data){{if(res&&i.issue_resolved!==res)continue;if(sur&&i.Surveyor_Name!==sur)continue;if(q){{const blob=((i.Surveyor_Name||"")+' '+(i.KEY||"")+' '+(i.Site_Visit_ID||"")+' '+(i.QA_Status||"")+' '+(i.Location||"")+' '+(i.Issue_Type||"")+' '+(i.Issue_Description||"")+' '+(i.surveyor_response||"")).toLowerCase();if(!blob.includes(q))continue;}}out.push(`<tr><td><div class="muted" style="font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:#4f46e5">${{esc(i.Surveyor_Name)}}</div><div class="muted">KEY: ${{esc(i.KEY)}}</div><div class="muted">Site_Visit_ID: ${{esc(i.Site_Visit_ID)}}</div><div class="muted">Location: ${{esc(i.Location)}}</div><div style="margin-top:8px;"></div><div style="font-weight:700;font-size:0.9rem;margin-top:4px"><span style="font-weight:900;">Issue Type:</span> <span style="font-weight:400;text-decoration:underline;">${{esc(i.Issue_Type)}}</span></div><div class="muted">QA Status: <span style="font-weight:900;text-decoration:underline;color:${{i.QA_Status==='Rejected'?'#ef4444':(i.QA_Status==='Approved'?'#10b981':'#94a3b8')}};">${{esc(i.QA_Status)}}</span></div><div class="muted" style="margin-top:10px"><span style="color:#dc2626;font-weight:900">ISSUE:</span><div class="issue-comments">${{formatComments(i.Issue_Description)}}</div></div></td><td><div class="response-comments">${{i.surveyor_response?formatComments(i.surveyor_response):'<div class="awaiting-response">Awaiting response from DC/field...</div>'}}</div></td><td class="c"><span class="pill" style="background:#e2e8f0;color:#0f172a">${{esc(i.severity)}}</span></td><td class="c"><span class="pill" style="background:${{i.issue_resolved==="Yes"?"#dcfce7":"#ffe4e6"}};color:${{i.issue_resolved==="Yes"?"#166534":"#9f1239"}}">${{i.issue_resolved==="Yes"?"Closed":"Pending"}}</span></td></tr>`);}}tbody.innerHTML=out.join("");}}
document.getElementById('q').addEventListener('input',render);document.getElementById('fResolved').addEventListener('input',render);document.getElementById('fSurveyor').addEventListener('input',render);document.getElementById('reset').addEventListener('click',()=>{{document.getElementById('q').value="";document.getElementById('fResolved').value="";document.getElementById('fSurveyor').value="";render();}});render();
</script></body></html>"""

            p_name = selected_project
            m_text = "ATR-QA Department"
            summary_scored = score_surveyors(summary_sr, w_rej=0.35, w_out=0.1, w_out2=0.2, w_fb=0.35)
            report_html = build_html_report(p_name, m_text, summary_scored, issues, chart_source_json)

            st.download_button(
                label="⬇ Download Surveyor Report (HTML)",
                data=report_html,
                file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True,
                type="primary",
                key="download_report_btn",
            )

    # ──────────────────────────────────────────
    # FOOTER / LOGOUT
    # ──────────────────────────────────────────
    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()
