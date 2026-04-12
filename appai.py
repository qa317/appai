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

# Minimal CSS for just the Hero Banner, Roadmap, and Links grid
st.markdown("""
<style>
/* Hero Banner */
.hero-banner {
  background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f766e 100%);
  border-radius: 18px; padding: 32px 40px; margin-bottom: 24px;
  display: flex; align-items: center; justify-content: space-between;
  position: relative; overflow: hidden;
  box-shadow: 0 4px 20px rgba(15,23,42,0.15);
}
.hero-banner::before {
  content: ''; position: absolute; top: -60%; right: -8%;
  width: 350px; height: 350px;
  background: radial-gradient(circle, rgba(255,255,255,0.07) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-banner h1 { color: #fff; font-size: 28px; font-weight: 800; margin: 0; position: relative; z-index: 1; }
.hero-banner .hero-sub { color: rgba(255,255,255,0.7); font-size: 14px; margin-top: 4px; position: relative; z-index: 1; }
.hero-badge {
  background: rgba(255,255,255,0.15); backdrop-filter: blur(12px);
  color: #fff; padding: 8px 16px; border-radius: 999px;
  font-size: 14px; font-weight: 600; border: 1px solid rgba(255,255,255,0.2);
  position: relative; z-index: 1; display: flex; align-items: center; gap: 8px;
}

/* Link Grid */
.links-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin-bottom: 1rem; }
.link-tile {
  background: #ffffff; border: 1px solid #e7e3e4; border-radius: 12px;
  padding: 16px; text-align: center; transition: box-shadow 0.2s, border-color 0.2s;
}
.link-tile:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: #0f766e; }
.link-tile .tile-icon { font-size: 24px; margin-bottom: 8px; }
.link-tile .tile-label { font-size: 11px; font-weight: 600; text-transform: uppercase; color: #64748b; margin-bottom: 8px; }
.link-tile a { color: #0f766e; font-weight: 600; text-decoration: none; font-size: 14px; }
.link-tile.na { border-style: dashed; opacity: 0.6; }

/* Updates Log */
.upd-day { margin: 10px 0; padding-left: 14px; border-left: 3px solid #e2e8f0; }
.upd-date { font-weight: 600; color: #0f766e; font-size: 14px; margin-bottom: 4px; }
.upd-item { margin: 4px 0; font-size: 14px; }
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
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center;'>📊 ATR Consulting</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: gray;'>Data Collection & QA Progress Tracker</p>", unsafe_allow_html=True)
            st.divider()
            
            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
            
            if submit:
                if username in user_dict and password == user_dict[username]["password"]:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Incorrect username or password. Please try again.")

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
            👤 {st.session_state.username}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if user_dict[st.session_state.username]["project"].split(',')[0] == 'All':
        main_project_names = df['Main Project'].unique()
    else:
        main_project_names = df[df['Main Project'].isin(
            user_dict[st.session_state.username]["project"].split(',')
        )]['Main Project'].unique()

    # --- Project Controls ---
    st.subheader("Project Overview")
    cols1, cols2 = st.columns(2)
    with cols1:
        main_project = st.selectbox("Select Project", main_project_names, key="selectbox_1")
    
    project_data = df[df['Main Project'] == main_project].reset_index()
    project_names = df[df['Main Project'] == main_project]['Project Name'].unique()

    # ── PROJECT TIMELINE ──
    with st.container(border=True):
        st.markdown("#### Project Timeline")

        PHASES = [
            ("DC",  "Planned Data Collection-Start", "Planned Data Collection-End", "Data Collection-Start", "Data Collection-End"),
            ("QA",  "Planned data QA-Start", "Planned data QA-End", "data QA-Start", "data QA-End"),
            ("DM",  "Planned DM-Start", "Planned DM-End", "DM-Start", "DM-End"),
            ("A&R", "Planned Reporting-Start", "Planned Reporting-End", "Reporting-Start", "Reporting-End"),
        ]
        
        today = pd.Timestamp.today().normalize()
        def to_dt(x): return pd.to_datetime(x, dayfirst=True, errors="coerce")

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
                y_vals.append(y)
                y_labels.append(f"{project} — {phase}")
                project_y.append(y)
                
                planned_color = "#0f766e" if is_current else "rgba(100,116,139,0.5)"
                fig.add_trace(go.Scatter(x=[ps, pe], y=[y, y], mode="lines",
                    line=dict(color=planned_color, width=3, dash="dash"), showlegend=False,
                    hovertemplate=f"<b>{project}</b><br>{phase}<br>Planned: {ps:%d-%b-%Y} → {pe:%d-%b-%Y}<extra></extra>"))
                
                if pd.notna(a_s):
                    is_running = pd.isna(a_e)
                    actual_end = a_e if pd.notna(a_e) else today
                    actual_color = "rgba(15,118,110,0.5)" if is_current else ("rgba(14,165,233,0.5)" if is_running else "rgba(14,165,233,0.3)")
                    fig.add_trace(go.Scatter(x=[a_s, actual_end], y=[y, y], mode="lines",
                        line=dict(color=actual_color, width=10), showlegend=False,
                        hovertemplate=f"<b>{project}</b><br>{phase}<br>Actual: {a_s:%d-%b-%Y} → {actual_end:%d-%b-%Y}<extra></extra>"))
                y += 1
            y += 1

        fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.35)
        fig.update_yaxes(tickmode="array", tickvals=y_vals, ticktext=y_labels, autorange="reversed", title="")
        fig.update_layout(
            height=max(380, 20 * len(y_vals)), margin=dict(l=10, r=20, t=10, b=10),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", hovermode="closest")
        st.plotly_chart(fig, use_container_width=True)


    # ── SUB-PROJECT ──
    st.divider()
    st.subheader("Round / Sub-Project Details")
    collll1, _ = st.columns(2)
    with collll1:
        selected_project = st.selectbox("Select Sub-project", project_names, key="selectbox_2")

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
        try: current_index = [s['label'] for s in steps].index(current_step_label)
        except ValueError: current_index = -1
        
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
                ring_bg, ring_border, txt_color, txt_weight, size = '#fff', '#e2e8f0', '#94a3b8', '400', '28px'
            nodes_html += f"""<div style="display:flex;flex-direction:column;align-items:center;width:{100/num_steps}%;">
                <div style="width:{size};height:{size};border-radius:50%;background:{ring_bg};border:2px solid {ring_border};
                    display:flex;align-items:center;justify-content:center;z-index:2;">{inner}</div>
                <p style="margin-top:16px;font-size:11px;font-family:sans-serif;font-weight:{txt_weight};color:{txt_color};text-align:center;">{step['label']}</p>
            </div>"""
        
        return f"""
        <style>@keyframes pulse-dot{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.5);opacity:.5}}}}</style>
        <div style="padding:20px 10px;"><div style="position:relative;width:100%;">
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:100%;height:4px;background:#e2e8f0;border-radius:99px;"></div>
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:{progress_pct}%;height:4px;background:#0f766e;border-radius:99px;transition:width .5s;"></div>
            <div style="position:relative;display:flex;justify-content:space-between;align-items:flex-start;width:100%;">{nodes_html}</div>
        </div></div>"""

    with st.container(border=True):
        st.markdown("#### Progress Roadmap")
        steps_data = [{"label": "Form Coding"}, {"label": "Training"}, {"label": "QA-Manual Checks"},
            {"label": "QA-Automated Checks"}, {"label": "QA-Dataset Finalization"}, {"label": "DM-Dataset Finalization"},
            {"label": "QA Report"}, {"label": "QA Completion"}]
        current_step = project_data['current_step'][0]
        st.components.v1.html(generate_roadmap_html(steps_data, current_step), height=120)

    # ── PROJECT LINKS ──
    st.markdown("#### Project Links")
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

    # ── DATA METRICS ──
    if proj_completed == "Yes":
        st.success("📁 **Project Archived:** This project has been archived. For complete information, refer to the Document field.")
    else:
        st.divider()
        st.subheader("Data Metrics")
        with st.spinner('Fetching live tracking data...'):
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
            t['Completion_status'] = 'Complete'
            if extra_code != '-': exec(extra_code)
            
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

        tool_names = project_data_tools['Tool'].unique()
        
        # Filtering using Pills for a modern look (Requires Streamlit 1.48+)
        st.markdown("##### Filter Data")
        selected_tool = st.multiselect('Select Tool(s)', tool_names, default=None)
        
        if selected_tool:
            t = t[t.Tool.isin(selected_tool)]
            tari = tari[tari.Tool.isin(selected_tool)]
            
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            qastatus = st.pills('QA Status', t.QA_Status.unique().tolist(), 
                default=[x for x in t.QA_Status.unique().tolist() if x != 'Rejected_paused'], selection_mode="multi")
        with col_f2:
            completion = st.pills('Completion Status', options=['Complete', 'Incomplete'], 
                default=['Complete', 'Incomplete'], selection_mode="multi")

        # Fallbacks if pills are cleared
        if not qastatus: qastatus = t.QA_Status.unique().tolist()
        if not completion: completion = ['Complete', 'Incomplete']

        t = t[(t.QA_Status.isin(qastatus)) & (t.Completion_status.isin(completion))].copy()
        tari = tari.merge(t[['V_ID'] + [c for c in t.columns if c not in tari.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left')
        t = t.merge(tari[['V_ID'] + [c for c in tari.columns if c not in t.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left')

        tall = t[(t.V_ID.isin(tari.V_ID))].copy()
        tall['d1'] = pd.to_datetime(tall['SubmissionDate'], format='%b %d, %Y %H:%M:%S', errors='coerce').dt.date
        tall['d2'] = pd.to_datetime(tall['SubmissionDate'], format='%Y-%m-%dT%H:%M:%S.%fZ', errors='coerce').dt.date
        tall['Date'] = tall.d1.fillna(tall.d2)
        tall['Date'] = pd.to_datetime(tall['Date']).dt.strftime('%Y-%m-%d')
        tall = tall.drop(columns=['SubmissionDate', 'occurance', 'd1', 'd2'])

        # Maps & Timelines
        dff = tall['Date'].value_counts().reset_index()
        dff.columns = ['Date', 'N']
        dff = dff.sort_values(by='Date', ascending=False)

        fig_timeline = px.area(dff, x='Date', y='N')
        fig_timeline.update_traces(line=dict(color='#0f766e', width=2), fillcolor='rgba(15,118,110,0.1)', mode='lines+markers')
        fig_timeline.update_layout(xaxis_title='', yaxis_title='Submissions', template='plotly_white', height=300,
            margin=dict(l=0, r=0, t=10, b=0))

        @st.cache_data(show_spinner=False)
        def load_geojson(path):
            with open(path, "r", encoding="utf-8") as f: return json.load(f)
            
        counts = t.groupby("Province").size().reset_index(name="count")
        counts["Province"] = counts["Province"].astype(str).str.strip()
        geo_raw = load_geojson("afghanistan_provinces.geojson")
        
        geo = copy.deepcopy(geo_raw)
        count_map = dict(zip(counts["Province"], counts["count"]))
        for feat in geo["features"]:
            name = feat["properties"].get("NAME_1")
            feat["properties"]["VISITS"] = int(count_map.get(name, 0))
            
        m = folium.Map(location=[34.5, 66.0], zoom_start=5, tiles="CartoDB positron")
        folium.Choropleth(geo_data=geo, data=counts, columns=["Province", "count"],
            key_on="feature.properties.NAME_1", fill_color="YlGnBu",
            fill_opacity=0.8, line_opacity=0.25).add_to(m)

        colii1, colii2 = st.columns(2)
        with colii1.container(border=True, height="stretch"):
            st.markdown("#### Geographic Coverage")
            st_folium(m, height=300, use_container_width=True, returned_objects=[])
        with colii2.container(border=True, height="stretch"):
            st.markdown("#### Submission Timeline")
            st.plotly_chart(fig_timeline, use_container_width=True)

        # ── KPI METRICS & DONUTS ──
        total_target = tari.shape[0]
        total_received = tari[tari.QA_Status.isin(qastatus)].shape[0]
        total_remaining = max(0, total_target - total_received)
        g = tari[tari.QA_Status.isin(qastatus)].QA_Status.value_counts().reset_index()
        approved_n = int(g[g['QA_Status'] == 'Approved']['count'].sum()) if 'Approved' in g['QA_Status'].values else 0
        rejected_n = int(g[g['QA_Status'] == 'Rejected']['count'].sum()) if 'Rejected' in g['QA_Status'].values else 0
        
        dc_pct = round(100 * total_received / total_target) if total_target else 0
        qa_pct = round(100 * approved_n / total_received) if total_received else 0

        st.markdown("#### Progress Indicators")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1.container(border=True):
            st.metric("DC Progress", f"{dc_pct}%", f"{total_received} / {total_target} Received", delta_color="off")
        with kpi2.container(border=True):
            st.metric("QA Approved", f"{approved_n}", f"{qa_pct}% Approval Rate", delta_color="normal")
        with kpi3.container(border=True):
            st.metric("Rejected", f"{rejected_n}", "- Needs review", delta_color="inverse")
        with kpi4.container(border=True):
            st.metric("Remaining", f"{total_remaining}", "Not yet received", delta_color="off")

        # Donuts
        labels1, values1 = ['Received', 'Remaining'], [total_received, total_remaining]
        labels2, values2 = g['QA_Status'].tolist(), g['count'].tolist()

        def make_donut(labels, values, title, colors):
            fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.75,
                marker=dict(colors=colors, line=dict(color="#ffffff", width=2)), textinfo="none"))
            fig.update_layout(title=dict(text=title, x=0.5), height=250, margin=dict(l=0, r=0, t=40, b=0),
                showlegend=True, legend=dict(orientation="h", y=-0.1, x=0.5, xanchor="center"))
            return fig

        d_col1, d_col2 = st.columns(2)
        with d_col1.container(border=True):
            st.plotly_chart(make_donut(labels1, values1, "Data Collection Ratio", ["#0f766e", "#e2e8f0"]), use_container_width=True)
        with d_col2.container(border=True):
            st.plotly_chart(make_donut(labels2, values2, "QA Status Breakdown", ["#10b981", "#ef4444", "#f59e0b", "#cbd5e1"]), use_container_width=True)

        # ── SAMPLE TRACKING DATAFRAME ──
        st.markdown("#### Sample Tracking Detail")
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
        data_metrics['Status'] = (data_metrics['Target'] == data_metrics['Approved data']).apply(lambda x: '✅' if x else '⏳')
        
        st.dataframe(data_metrics, hide_index=True, use_container_width=True)

        col1, col2 = st.columns([1, 4])
        with col1:
            st.download_button("⬇ Download Target Data (CSV)", data=convert_df_to_csv(tari), file_name='Sample_Tracking.csv', mime='text/csv')

        # ── SUMMARY GENERATION ──
        st.divider()
        st.subheader("Summary Generation")
        col3, col4 = st.columns(2)
        
        with col3.container(border=True, height="stretch"):
            st.markdown("#### DC Progress Summary")
            disag2 = st.multiselect('Group Sample Tracking by:', tari.columns.tolist(), def_var0)
            if disag2:
                total_target_s = tari.fillna('NAN').groupby(disag2).size()
                received_data_s = tari.fillna('NAN')[tari['QA_Status'].isin(qastatus)].groupby(disag2).size()
                summary = pd.DataFrame({'Total_Target': total_target_s, 'Received_Data': received_data_s}).fillna(0).astype(int)
                summary['Remaining'] = summary['Total_Target'] - summary['Received_Data']
                st.dataframe(summary)
                
        with col4.container(border=True, height="stretch"):
            st.markdown("#### Dataset Summary")
            disag = st.multiselect('Group Completed Data by:', tall.columns.tolist(), default=def_var1)
            if disag:
                if len(disag) == 1:
                    disag_t = tall.groupby(disag).size().reset_index().rename(columns={0: 'N'})
                else:
                    disag_t = tall.groupby(disag).size().unstack(disag[-1], fill_value=0).reset_index()
                st.dataframe(disag_t)

    # ── UPDATE LOGS ──
    st.divider()
    st.subheader("Project Updates")
    def parse_log(log_text):
        log_text = log_text if isinstance(log_text, str) else ""
        parts = [p.strip() for p in re.split(r";;\s*", log_text.strip()) if p.strip()]
        rows = []
        for p in parts:
            if ":" not in p: continue
            ds, msg = p.split(":", 1)
            d = datetime.strptime(ds.strip(), "%d/%m/%Y").date()
            rows.append((d, msg.strip()))
        rows.sort(key=lambda x: x[0], reverse=True)
        return rows

    log_text = project_data.loc[0, "Logs"]
    rows = parse_log(log_text)
    
    with st.expander(f"View Log History ({len(rows)} updates)", expanded=False):
        for d, msg in rows:
            st.markdown(f"<div class='upd-day'><div class='upd-date'>{d.strftime('%d %b %Y')}</div><div class='upd-item'>{msg}</div></div>", unsafe_allow_html=True)

    # ── FOOTER ──
    st.divider()
    col_foot1, col_foot2, col_foot3 = st.columns([1, 3, 1])
    with col_foot1:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    with col_foot3:
        st.caption(f"ATR Dashboard · {datetime.now().year}")
