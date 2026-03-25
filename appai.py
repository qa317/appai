import copy
import json
import re
from datetime import datetime
from io import StringIO
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import folium
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="QA and DC Progress Tracker", page_icon="📊", layout="wide")

# =========================================================
# STYLES
# =========================================================
st.markdown(
    """
    <style>
        .block-container {padding-top: 1rem; padding-bottom: 2rem;}
        .hero-title {font-size: 2rem; font-weight: 800; color: #7c1636; margin: 0;}
        .hero-sub {color: #64748b; font-size: 0.95rem; margin-top: 4px;}
        .section-title {color: #7c1636; font-size: 1.2rem; font-weight: 700; margin: 0 0 .8rem 0;}
        .app-card {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 4px 14px rgba(15,23,42,.05);
            margin-top: 12px;
        }
        .mini-kpi {
            background: #fff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 14px;
            text-align: center;
        }
        .mini-kpi .label {
            color: #64748b;
            font-size: .78rem;
            font-weight: 700;
            text-transform: uppercase;
        }
        .mini-kpi .value {
            font-size: 1.35rem;
            font-weight: 800;
            color: #0f172a;
            margin-top: 6px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================
def init_state():
    defaults = {
        "logged_in": False,
        "username": None,
        "raw_data_loaded": False,
        "project_cache": {},   # selected_project -> expensive loaded bundle
        "applied_main_project": None,
        "applied_selected_project": None,
        "applied_selected_tool": [],
        "applied_qastatus": ["Not QA'ed Yet", "Pending", "Approved", "Rejected"],
        "applied_completion": ["Complete", "Incomplete"],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# =========================================================
# SAFE LOADERS
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def load_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

def load_csv_url_safe(url: str) -> pd.DataFrame:
    try:
        with urlopen(url) as response:
            content = response.read().decode("utf-8")
        return pd.read_csv(StringIO(content))
    except HTTPError as e:
        raise RuntimeError(f"HTTP error while loading URL: {url} | {e}")
    except URLError as e:
        raise RuntimeError(f"Network error while loading URL: {url} | {e}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error while loading URL: {url} | {e}")

@st.cache_data(show_spinner=False)
def load_geojson(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data(ttl=300, show_spinner=False)
def load_base_tables():
    csv_url_main = st.secrets["CSV_URL_MAIN"]
    csv_url_tools = st.secrets["CSV_URL_TOOLS"]
    csv_url_users = st.secrets["CSV_URL_USERS"]
    df = load_csv(csv_url_main)
    df_tools = load_csv(csv_url_tools)
    df_users = load_csv(csv_url_users)
    return df, df_tools, df_users

# =========================================================
# HELPERS
# =========================================================
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def safe_text(x, default=""):
    return default if pd.isna(x) else str(x)

def to_dt(x):
    return pd.to_datetime(x, dayfirst=True, errors="coerce")

def delay_days(plan_end, actual_end):
    if pd.notna(plan_end) and pd.notna(actual_end):
        d = (actual_end - plan_end).days
        return d if d > 0 else 0
    return 0

def parse_default_vars(def_var: str):
    if not isinstance(def_var, str) or def_var.strip() == "-":
        return [], [], []
    parts = def_var.split(";")
    def_var0 = [item.strip() for item in parts[0].split(",")] if len(parts) > 0 else []
    def_var1 = [item.strip() for item in parts[1].split(",")] if len(parts) > 1 else []
    def_var2 = [item.strip() for item in parts[2].split(",")] if len(parts) > 2 else []
    return def_var0, def_var1, def_var2

def parse_log(log_text: str):
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
        except Exception:
            continue
    rows.sort(key=lambda x: x[0])
    return rows

# =========================================================
# AUTH
# =========================================================
df, df_tools, df_users = load_base_tables()
user_dict = df_users.set_index("users")[["password", "project"]].to_dict(orient="index")

def full_logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.cache_data.clear()
    st.rerun()

if not st.session_state.logged_in:
    with st.container():
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("### ATR Consulting - Data Collection / QA Progress Tracker")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")
        if submit:
            if username in user_dict and password == user_dict[username]["password"]:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Incorrect username or password.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

username = st.session_state.username

# =========================================================
# HEADER
# =========================================================
c1, c2 = st.columns([8, 2])
with c1:
    st.markdown("<p class='hero-title'>QA and DC Progress Tracker</p>", unsafe_allow_html=True)
    st.markdown(
        "<p class='hero-sub'>Expensive data loading happens only on Refresh. Filters only work on data already in memory.</p>",
        unsafe_allow_html=True,
    )
with c2:
    a, b = st.columns(2)
    with a:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.project_cache = {}
            st.session_state.raw_data_loaded = False
            st.cache_data.clear()
            st.rerun()
    with b:
        if st.button("Logout", use_container_width=True):
            full_logout()

# =========================================================
# PROJECT CHOICES
# =========================================================
if user_dict[username]["project"].split(",")[0] == "All":
    main_project_names = sorted(df["Main Project"].dropna().unique().tolist())
else:
    allowed = user_dict[username]["project"].split(",")
    main_project_names = sorted(df[df["Main Project"].isin(allowed)]["Main Project"].dropna().unique().tolist())

if st.session_state.applied_main_project is None and main_project_names:
    st.session_state.applied_main_project = main_project_names[0]

if st.session_state.applied_selected_project is None:
    default_projects = sorted(
        df[df["Main Project"] == st.session_state.applied_main_project]["Project Name"].dropna().unique().tolist()
    )
    st.session_state.applied_selected_project = default_projects[0] if default_projects else None

# =========================================================
# CONTROLS
# =========================================================
st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<p class='section-title'>Control Panel</p>", unsafe_allow_html=True)

with st.form("filters_form"):
    form_main_project = st.selectbox(
        "Main Project",
        main_project_names,
        index=main_project_names.index(st.session_state.applied_main_project)
        if st.session_state.applied_main_project in main_project_names else 0,
    )

    available_projects = sorted(
        df[df["Main Project"] == form_main_project]["Project Name"].dropna().unique().tolist()
    )

    form_selected_project = st.selectbox(
        "Round / Sub-Project",
        available_projects,
        index=available_projects.index(st.session_state.applied_selected_project)
        if st.session_state.applied_selected_project in available_projects else 0,
    )

    available_tools = sorted(
        df_tools[df_tools["Project Name"] == form_selected_project]["Tool"].dropna().unique().tolist()
    )

    f1, f2, f3 = st.columns(3)
    with f1:
        form_selected_tool = st.multiselect(
            "Tool",
            available_tools,
            default=[x for x in st.session_state.applied_selected_tool if x in available_tools],
        )
    with f2:
        qa_options = ["Not QA'ed Yet", "Pending", "Approved", "Rejected", "Rejected_paused"]
        form_qastatus = st.multiselect(
            "QA Status",
            qa_options,
            default=st.session_state.applied_qastatus,
        )
    with f3:
        form_completion = st.multiselect(
            "Completion Status",
            ["Complete", "Incomplete"],
            default=st.session_state.applied_completion,
        )

    apply_btn = st.form_submit_button("Apply filters", type="primary", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

if apply_btn:
    st.session_state.applied_main_project = form_main_project
    st.session_state.applied_selected_project = form_selected_project
    st.session_state.applied_selected_tool = form_selected_tool
    st.session_state.applied_qastatus = form_qastatus if form_qastatus else qa_options
    st.session_state.applied_completion = form_completion if form_completion else ["Complete", "Incomplete"]
    st.rerun()

main_project = st.session_state.applied_main_project
selected_project = st.session_state.applied_selected_project
selected_tool = st.session_state.applied_selected_tool
qastatus = st.session_state.applied_qastatus
completion = st.session_state.applied_completion

# =========================================================
# TIMELINE FIGURE
# =========================================================
def build_project_timeline(project_data: pd.DataFrame):
    PHASES = [
        ("DC", "Planned Data Collection-Start", "Planned Data Collection-End", "Data Collection-Start", "Data Collection-End"),
        ("QA", "Planned data QA-Start", "Planned data QA-End", "data QA-Start", "data QA-End"),
        ("DM", "Planned DM-Start", "Planned DM-End", "DM-Start", "DM-End"),
        ("A&R", "Planned Reporting-Start", "Planned Reporting-End", "Reporting-Start", "Reporting-End"),
    ]

    PLANNED_COLOR = "rgba(88,101,242,0.9)"
    ACTUAL_COLOR = "rgba(59,130,246,0.30)"
    RUNNING_COLOR = "rgba(59,130,246,0.45)"
    CURRENT_PLANNED_COLOR = "rgba(0,144,118,1.0)"
    CURRENT_ACTUAL_COLOR = "rgba(0,144,118,0.45)"
    ONTIME_COLOR = "#22c55e"
    DELAY_COLOR = "#ef4444"
    PLANNED_W = 3
    ACTUAL_W = 10
    GAP = 1.1
    today = pd.Timestamp.today().normalize()

    project_data = project_data.copy()
    for _, ps, pe, a_s, a_e in PHASES:
        for c in (ps, pe, a_s, a_e):
            if c in project_data.columns:
                project_data[c] = pd.to_datetime(project_data[c], dayfirst=True, errors="coerce")

    fig = go.Figure()
    y_vals, y_labels = [], []
    y = 0

    for _, row in project_data.iterrows():
        project = safe_text(row.get("Project Name", "—"))
        responsible = safe_text(row.get("Responsible", "")).strip().lower()
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
                actual_color = CURRENT_ACTUAL_COLOR if is_current else (ACTUAL_COLOR if not is_running else RUNNING_COLOR)

                fig.add_trace(go.Scatter(
                    x=[a_s, actual_end], y=[y, y], mode="lines",
                    line=dict(color=actual_color, width=ACTUAL_W),
                    showlegend=False,
                    hovertemplate=f"<b>{project}</b><br>{phase}<br>Actual: {a_s:%d-%b-%Y} → {actual_end:%d-%b-%Y}{' (running)' if is_running else ''}<extra></extra>",
                ))

                if is_running:
                    fig.add_annotation(
                        x=actual_end, y=y, text="<b>↝</b>", showarrow=False,
                        xanchor="left", yanchor="middle",
                        font=dict(size=22, color="#7f1d1d"),
                        bgcolor="rgba(255,255,255,0.6)",
                    )

                if not is_running:
                    d = delay_days(pe, a_e)
                    if d > 0:
                        fig.add_trace(go.Scatter(
                            x=[a_e], y=[y], mode="markers+text",
                            marker=dict(size=8, color=DELAY_COLOR),
                            text=[f"+{d}d"], textposition="top center",
                            textfont=dict(size=9, color=DELAY_COLOR),
                            showlegend=False,
                        ))
                    else:
                        fig.add_annotation(
                            x=a_e, y=y, text="<b>🗹</b>", showarrow=False,
                            font=dict(size=18, color=ONTIME_COLOR), xshift=8,
                        )
            y += 1

        if project_y and responsible:
            fig.add_annotation(
                xref="paper", x=0.90, xanchor="left",
                y=sum(project_y) / len(project_y), yanchor="middle",
                text=f"<span style='color:#7c3aed;font-size:12px;'>● Now with: <b>{row.get('Responsible')}</b></span>",
                showarrow=False,
            )
        y += GAP

    fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.4)
    fig.add_annotation(
        x=today, y=0.99, xref="x", yref="paper",
        text="<b><i>Today</i></b>", showarrow=False,
        xanchor="center", yanchor="bottom",
        font=dict(size=12, color="#0F5448"),
    )

    fig.update_yaxes(
        tickmode="array", tickvals=y_vals, ticktext=y_labels,
        autorange="reversed", title="",
    )

    start_cols = [ps for _, ps, _, _, _ in PHASES if ps in project_data.columns]
    end_cols = [pe for _, _, pe, _, _ in PHASES if pe in project_data.columns]
    min_x = project_data[start_cols].min().min() if start_cols else pd.Timestamp.today()
    max_x = project_data[end_cols].max().max() if end_cols else pd.Timestamp.today()

    fig.update_xaxes(
        range=[min_x, max_x + pd.Timedelta(days=20)],
        showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False,
    )
    fig.update_layout(
        height=max(380, 20 * len(y_vals)),
        margin=dict(l=95, r=80, t=20, b=10),
        plot_bgcolor="white", paper_bgcolor="white", hovermode="closest",
    )
    return fig

# =========================================================
# EXPENSIVE PROJECT LOAD - ONLY ONCE PER PROJECT
# =========================================================
def expensive_load_project_bundle(selected_project: str):
    project_data = df[df["Project Name"] == selected_project].reset_index(drop=True)
    if project_data.empty:
        raise RuntimeError(f"No project data found for project: {selected_project}")

    project_data_tools = df_tools[df_tools["Project Name"] == selected_project].reset_index(drop=True)
    tool_col_map = project_data_tools.set_index("Tool")["main_cols"].to_dict() if not project_data_tools.empty else {}

    rawsheet = project_data.loc[0, "raw_sheet"]
    sampling_id = project_data.loc[0, "Sampling_ID"]
    qalog_id = project_data.loc[0, "QAlog_ID"]
    hfc_id = project_data.loc[0, "HFC_ID"]

    raw_sheet_id = rawsheet.split("/d/")[1].split("/")[0]
    raw_csv_url = f"https://docs.google.com/spreadsheets/d/{raw_sheet_id}/export?format=csv&id={raw_sheet_id}&gid=0"
    t_raw = load_csv_url_safe(raw_csv_url).copy()
    t_raw["KEY_Unique"] = t_raw["KEY"]

    qalog_url = f"https://docs.google.com/spreadsheets/d/1V1SfBZUwHN0NtXFIoiXEh7JGkpTUOLZnGAfFN8QVXYQ/export?format=csv&{qalog_id}"
    qalog = load_csv_url_safe(qalog_url).copy()

    if "KEY_Unique" in qalog.columns and "QA_Status" in qalog.columns:
        t_raw = pd.merge(
            t_raw,
            qalog[["QA_Status", "KEY_Unique"]].drop_duplicates("KEY_Unique"),
            on="KEY_Unique",
            how="left",
        )

    t_raw["QA_Status"] = t_raw["QA_Status"].replace("", "Not QA'ed Yet")
    t_raw["QA_Status"] = t_raw["QA_Status"].fillna("Not QA'ed Yet")
    t_raw["Completion_status"] = "Complete"

    extra_code = safe_text(project_data.loc[0, "extra_code"], "-")
    if extra_code != "-":
        local_scope = {"t": t_raw, "pd": pd, "np": np}
        try:
            exec(extra_code, {"__builtins__": {}}, local_scope)
            t_raw = local_scope.get("t", t_raw)
        except Exception as e:
            st.warning(f"extra_code failed for {selected_project}: {e}")

    t_raw = t_raw.sort_values(by=["QA_Status", "Completion_status"], ascending=True)

    t_raw["occurance"] = None
    for tool, cols in tool_col_map.items():
        group_cols = [c for c in cols.split("-") if c and c != "occurance" and c in t_raw.columns]
        if not group_cols:
            continue
        mask = t_raw["Tool"] == tool
        t_raw.loc[mask, "occurance"] = t_raw.loc[mask].groupby(group_cols).cumcount() + 1

    t_raw["occurance"] = t_raw["occurance"].fillna(9999).astype(int)

    def compute_vid(row):
        cols_str = tool_col_map.get(row["Tool"], "")
        cols = [c.strip() for c in cols_str.split("-") if c.strip()]
        parts = []
        for col in cols:
            if col in row.index:
                parts.append(str(row[col]).removesuffix(".0"))
            else:
                parts.append("NA")
        return f"{row['Tool']}/{'-'.join(parts)}"

    t_raw["V_ID"] = t_raw.apply(compute_vid, axis=1)

    sampling_url = f"https://docs.google.com/spreadsheets/d/1U0Y7TQnTFEg1edMb0IHejOxv9S2YLY2UH-tp1qzXyBg/export?format=csv&{sampling_id}"
    tari_raw = load_csv_url_safe(sampling_url).copy()
    tari_raw["V_ID"] = tari_raw["Tool"] + "/" + tari_raw["V_ID"].astype(str)
    tari_raw = tari_raw[tari_raw["Skipped"] != "Yes"]

    if not project_data_tools.empty and "Tool" in project_data_tools.columns:
        tari_raw = tari_raw[
            (tari_raw["Tool"].isin(t_raw["Tool"].unique())) &
            (tari_raw["Tool"].isin(project_data_tools["Tool"]))
        ]

    df_free = t_raw[t_raw["Tool"].isin(project_data_tools["Tool"]) & ~t_raw["Tool"].isin(tari_raw["Tool"])].copy()
    df_free = df_free.drop(columns=["KEY", "QA_Status"], errors="ignore")
    df_free = df_free[tari_raw.columns.intersection(df_free.columns)]
    tari_raw = pd.concat([tari_raw, df_free], ignore_index=True)

    hfc_url = f"https://docs.google.com/spreadsheets/d/16EWCV7HTEx729ILvsYa72LkJ1P1Sw7Fo2R0FzXs3GvE/export?format=csv&{hfc_id}"
    hfc = load_csv_url_safe(hfc_url).copy()

    return {
        "project_data": project_data,
        "project_data_tools": project_data_tools,
        "tool_col_map": tool_col_map,
        "t_raw": t_raw,
        "tari_raw": tari_raw,
        "qalog": qalog,
        "hfc": hfc,
    }

# only expensive load when not cached in session
if selected_project not in st.session_state.project_cache:
    with st.spinner(f"Loading data for {selected_project}..."):
        try:
            st.session_state.project_cache[selected_project] = expensive_load_project_bundle(selected_project)
            st.session_state.raw_data_loaded = True
        except Exception as e:
            st.error(f"Failed to load project data: {e}")
            st.stop()

bundle = st.session_state.project_cache[selected_project]

project_data = bundle["project_data"]
project_data_tools = bundle["project_data_tools"]
tool_col_map = bundle["tool_col_map"]
t_raw = bundle["t_raw"]
tari_raw = bundle["tari_raw"]
qalog = bundle["qalog"]
hfc = bundle["hfc"]

# =========================================================
# CHEAP FILTERING ONLY
# =========================================================
def apply_filters_in_memory(t_raw, tari_raw, selected_tool, qastatus, completion):
    t = t_raw.copy()
    tari = tari_raw.copy()

    if selected_tool:
        t = t[t["Tool"].isin(selected_tool)]
        tari = tari[tari["Tool"].isin(selected_tool)]

    t = t[(t["QA_Status"].isin(qastatus)) & (t["Completion_status"].isin(completion))].copy()

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

    tall = t[t["V_ID"].isin(tari["V_ID"])].copy()

    if "SubmissionDate" in tall.columns:
        tall["d1"] = pd.to_datetime(tall["SubmissionDate"], format="%b %d, %Y %H:%M:%S", errors="coerce").dt.date
        tall["d2"] = pd.to_datetime(tall["SubmissionDate"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors="coerce").dt.date
        tall["Date"] = tall["d1"].fillna(tall["d2"])
        tall["Date"] = pd.to_datetime(tall["Date"])
        tall["Date"] = tall["Date"].dt.strftime("%Y-%m-%d")
        tall = tall.drop(columns=["SubmissionDate", "occurance", "d1", "d2"], errors="ignore")

    tall2 = None
    if len(tool_col_map) > 0 and list(tool_col_map.values())[0].rsplit("-", 1)[-1] == "occurance":
        base_ids = tari["V_ID"].str.rsplit("-", n=1).str[0].dropna().unique()
        tall2 = t[t["V_ID"].str.startswith(tuple(base_ids), na=False)]

    missing = pd.DataFrame(columns=["Tool", "V_ID", "KEY", "Type", "QA_Status"])
    m = tari[~tari.V_ID.isin(t["V_ID"])].copy()
    m["Type"] = "Missing Data"

    ext = t[(~t.V_ID.isin(tari["V_ID"])) & (t.QA_Status == "Approved")][["Tool", "V_ID", "KEY", "QA_Status"]].copy()
    ext["Type"] = "Extra data"

    dup = t[t.V_ID.duplicated(keep="first")][["Tool", "V_ID", "KEY", "QA_Status"]].copy()
    dup["Type"] = "Duplicate Data"

    missing = pd.concat([missing, m, ext, dup], ignore_index=True)

    if "KEY" in tall.columns:
        bad_keys = pd.concat([ext["KEY"], dup["KEY"]], ignore_index=True).dropna().unique().tolist()
        if bad_keys:
            tall = tall[~tall["KEY"].isin(bad_keys)]

    return t, tari, tall, tall2, missing

t, tari, tall, tall2, missing = apply_filters_in_memory(
    t_raw, tari_raw, selected_tool, qastatus, completion
)

# =========================================================
# TOP KPIs
# =========================================================
main_project_df = df[df["Main Project"] == main_project]
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(f"<div class='mini-kpi'><div class='label'>Main Project</div><div class='value'>{main_project}</div></div>", unsafe_allow_html=True)
with k2:
    st.markdown(f"<div class='mini-kpi'><div class='label'>Sub-Project</div><div class='value'>{selected_project}</div></div>", unsafe_allow_html=True)
with k3:
    st.markdown(f"<div class='mini-kpi'><div class='label'>Rounds</div><div class='value'>{main_project_df['Project Name'].nunique()}</div></div>", unsafe_allow_html=True)

# =========================================================
# TIMELINE
# =========================================================
st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<p class='section-title'>Project Timeline</p>", unsafe_allow_html=True)
main_project_data = df[df["Main Project"] == main_project].reset_index(drop=True)
timeline_fig = build_project_timeline(main_project_data)
st.plotly_chart(timeline_fig, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# LINKS
# =========================================================
st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<p class='section-title'>Project Links</p>", unsafe_allow_html=True)

links_row = project_data[["Tool link", "XLSForm link", "QA-Notes link", "Tracker link", "DC Tracker", "Document folder link"]].iloc[0]
link_labels = {
    "Tool link": "🛠 Tool",
    "XLSForm link": "📄 XLSForm",
    "QA-Notes link": "📊 QA Notes",
    "Tracker link": "📈 QA Tracker",
    "DC Tracker": "📍 DC Tracker",
    "Document folder link": "📁 Docs",
}
cols = st.columns(6)
for i, (col_name, label) in enumerate(link_labels.items()):
    value = links_row[col_name]
    with cols[i]:
        if pd.notna(value) and str(value).strip():
            st.markdown(f"<div class='mini-kpi'><div class='label'>{label}</div><div class='value' style='font-size:1rem;'><a href='{value}' target='_blank'>Open</a></div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='mini-kpi'><div class='label'>{label}</div><div class='value' style='font-size:1rem;color:#94a3b8;'>N/A</div></div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

proj_completed = safe_text(project_data.loc[0, "Completed"])
def_var0, def_var1, def_var2 = parse_default_vars(safe_text(project_data.loc[0, "Summary_defualt_var"], "-"))

if proj_completed != "Yes":
    # =====================================================
    # DATA METRICS
    # =====================================================
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Data Metrics</p>", unsafe_allow_html=True)

    dff = tall["Date"].value_counts().reset_index() if "Date" in tall.columns else pd.DataFrame(columns=["Date", "count"])
    if not dff.empty:
        dff.columns = ["Date", "N"]
        dff = dff.sort_values(by="Date", ascending=False)
        fig = px.line(dff, x="Date", y="N", title="Timeline of Data")
        fig.update_traces(mode="lines+markers", marker=dict(size=9))
        fig.update_layout(template="plotly_white", height=320, margin=dict(l=20, r=20, t=40, b=20))
    else:
        fig = go.Figure()
        fig.update_layout(template="plotly_white", height=320, title="Timeline of Data")

    counts = t.groupby("Province").size().reset_index(name="count") if "Province" in t.columns else pd.DataFrame(columns=["Province", "count"])
    if not counts.empty:
        counts["Province"] = counts["Province"].astype(str).str.strip()

    geo_raw = load_geojson("afghanistan_provinces.geojson")

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
            fill_opacity=0.8,
            line_opacity=0.25,
            nan_fill_color="#EAEAEA",
            nan_fill_opacity=0.65,
            legend_name="Visits",
        ).add_to(m)

        folium.GeoJson(
            geo,
            style_function=lambda f: {"color": "#777", "weight": 0.7, "fillOpacity": 0},
            highlight_function=lambda f: {"color": "#111", "weight": 2},
            tooltip=folium.GeoJsonTooltip(fields=["NAME_1", "VISITS"], aliases=["Province:", "Visits:"], sticky=True),
        ).add_to(m)
        return m

    my_map = build_map(geo_raw, counts)
    c1, c2 = st.columns(2)
    with c1:
        st_folium(my_map, height=320, use_container_width=True, returned_objects=[], key="afg_map")
    with c2:
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # SAMPLE TRACKING
    # =====================================================
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Sample Tracking</p>", unsafe_allow_html=True)

    target = tari.groupby("Tool").size()
    received = tari[tari.QA_Status.notna()].groupby("Tool").size()
    approved = tari[tari.QA_Status == "Approved"].groupby("Tool").size()
    rejected = tari[tari.QA_Status == "Rejected"].groupby("Tool").size()
    awaiting = tari[tari.QA_Status.isin(["Not QA'ed Yet", "Pending"])].groupby("Tool").size()

    data_metrics = pd.DataFrame({
        "Target": target,
        "Received data": received,
        "Approved data": approved,
        "Rejected data": rejected,
        "Awaiting review": awaiting,
    }).fillna(0).astype(int).reset_index()

    data_metrics["Completion %"] = ((data_metrics["Received data"] / data_metrics["Target"]) * 100).round(2)
    data_metrics["Completed ✅"] = np.where(data_metrics["Target"] == data_metrics["Approved data"], "✅", "❌")
    st.dataframe(data_metrics, use_container_width=True)

    labels1 = ["Received", "Remaining"]
    values1 = [
        tari[tari.QA_Status.isin(qastatus)].shape[0],
        max(0, tari.shape[0] - tari[tari.QA_Status.isin(qastatus)].shape[0]),
    ]
    g = tari[tari.QA_Status.isin(qastatus)].QA_Status.value_counts().reset_index()
    g.columns = ["QA_Status", "count"]

    fig1 = go.Figure(data=[go.Pie(labels=labels1, values=values1, hole=0.6, textinfo="label+percent")])
    fig1.update_layout(title_text="Data Collection Progress", template="plotly_white")

    fig2 = go.Figure(data=[go.Pie(labels=g["QA_Status"], values=g["count"], hole=0.6, textinfo="label+percent")])
    fig2.update_layout(title_text="Data QA Progress", template="plotly_white")

    p1, p2 = st.columns(2)
    with p1:
        st.plotly_chart(fig1, use_container_width=True)
    with p2:
        st.plotly_chart(fig2, use_container_width=True)

    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "Download Target Data Details",
            data=convert_df_to_csv(tari),
            file_name="Sample_Tracking.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Download Missing / Extra / Duplicate",
            data=convert_df_to_csv(missing),
            file_name="Missing_Extra_Duplicate.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # SUMMARY
    # =====================================================
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Summary Generation</p>", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        disag2 = st.multiselect(
            "Create Sample Summary",
            tari.columns.tolist(),
            default=[x for x in def_var0 if x in tari.columns],
        )
        if disag2:
            total_target = tari.groupby(disag2).size()
            received_data = tari[tari["QA_Status"].isin(qastatus)].groupby(disag2).size()
            summary = pd.DataFrame({"Total_Target": total_target, "Received_Data": received_data}).fillna(0).astype(int)
            summary["Remaining"] = summary["Total_Target"] - summary["Received_Data"]
            summary["Completed ✅"] = np.where(summary["Received_Data"] == summary["Total_Target"], "✅", "❌")
            st.dataframe(summary, use_container_width=True)

    with s2:
        disag = st.multiselect(
            "Create Dataset Summary",
            tall.columns.tolist(),
            default=[x for x in def_var1 if x in tall.columns],
        )
        if disag:
            if len(disag) == 1:
                disag_t = tall.groupby(disag).size().reset_index().rename(columns={0: "N"})
                disag_t.loc[len(disag_t)] = ["Total", disag_t["N"].sum()]
            else:
                disag_t = tall.groupby(disag).size().unstack(disag[-1], fill_value=0).reset_index()
                disag_t.loc["Total"] = disag_t.sum(numeric_only=True)
            st.dataframe(disag_t, use_container_width=True)

    if tall2 is not None:
        disag_raw = st.multiselect(
            "Tryouts Summary",
            tall2.columns.tolist(),
            default=[x for x in def_var2 if x in tall2.columns],
        )
        if disag_raw:
            if len(disag_raw) == 1:
                disag_traw = tall2.groupby(disag_raw).size().reset_index().rename(columns={0: "N"})
                disag_traw.loc[len(disag_traw)] = ["Total", disag_traw["N"].sum()]
            else:
                disag_traw = tall2.groupby(disag_raw).size().unstack(disag_raw[-1], fill_value=0).reset_index()
                disag_traw.loc["Total"] = disag_traw.sum(numeric_only=True)
            st.dataframe(disag_traw, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# LOGS
# =========================================================
log_text = safe_text(project_data.loc[0, "Logs"], "")
rows = parse_log(log_text)
by_day = {}
for d, msg in rows:
    by_day.setdefault(d, []).append(msg)

dates = list(by_day.keys())
total_logs = sum(len(v) for v in by_day.values())
start, end = (min(dates), max(dates)) if dates else (None, None)
header = f"Project updates · {total_logs} update{'s' if total_logs != 1 else ''}"
if start:
    header += f" · {start.strftime('%d %b %Y')} → {end.strftime('%d %b %Y')}"

with st.expander(header, expanded=False):
    for d, msgs in by_day.items():
        st.markdown(f"**{d.strftime('%d %b %Y')}**")
        for m in msgs:
            st.markdown(f"- {m}")

# =========================================================
# SURVEYOR REPORT
# =========================================================
st.markdown("<div class='app-card'>", unsafe_allow_html=True)
st.markdown("<p class='section-title'>Surveyor Performance Report</p>", unsafe_allow_html=True)

if st.button("Generate Surveyor Performance Report", type="primary"):
    try:
        qalog2 = pd.merge(
            tall,
            qalog[[
                "Issue_Type", "Issue_Description", "surveyor_notified",
                "surveyor_response", "issue_resolved", "KEY_Unique"
            ]],
            on="KEY_Unique",
            how="left"
        )

        qalog2["severity"] = qalog2["QA_Status"].map({"Rejected": "High", "Approved": "Low", "Pending": "Medium"}).fillna("Low")

        issues = qalog2[[
            "Site_Visit_ID", "Province", "Village", "severity", "QA_Status", "Surveyor_Name", "KEY",
            "Issue_Type", "Issue_Description", "surveyor_notified", "surveyor_response", "issue_resolved"
        ]].copy()

        summary = (
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
            hfc = hfc.drop_duplicates(subset="Surveyor_Name")
            summary = pd.merge(summary, hfc, on="Surveyor_Name", how="left").fillna(0)

        for col in ["hfc_outliers_ratio", "ta_outliers"]:
            if col not in summary.columns:
                summary[col] = 0

        def score_surveyors(df: pd.DataFrame):
            df = df.copy()
            score = 100 - (
                df["rejection_ratio"] * 100 * 0.35
                + df["hfc_outliers_ratio"] * 100 * 0.1
                + df["ta_outliers"] * 100 * 0.2
                + df["total_feedback_ratio"] * 100 * 0.35
            )
            df["score"] = score.round(1).clip(0, 100)
            return df

        summary_scored = score_surveyors(summary)
        report_html = summary_scored.to_html(index=False)

        st.download_button(
            "Download Surveyor Report (HTML)",
            data=report_html,
            file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html",
            mime="text/html",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Could not generate surveyor report: {e}")

st.markdown("</div>", unsafe_allow_html=True)
