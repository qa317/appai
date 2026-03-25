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
from streamlit_folium import st_folium

# =========================================================
# PAGE SETUP
# =========================================================
st.set_page_config(
    page_title="QA and DC Progress Tracker",
    page_icon="📊",
    layout="wide",
)

# =========================================================
# GLOBAL STYLES
# =========================================================
st.markdown(
    """
    <style>
        :root {
            --brand:#7c1636;
            --brand-2:#0f766e;
            --muted:#64748b;
            --card:#ffffff;
            --border:#e2e8f0;
            --bg-soft:#f8fafc;
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        .app-card {
            background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px 18px;
            box-shadow: 0 6px 18px rgba(15, 23, 42, 0.05);
        }

        .soft-card {
            background: var(--bg-soft);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px 16px;
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            color: var(--brand);
            margin: 0;
            line-height: 1.1;
        }

        .hero-sub {
            color: var(--muted);
            font-size: 0.98rem;
            margin-top: 4px;
        }

        .section-title {
            color: var(--brand);
            font-size: 1.2rem;
            font-weight: 700;
            margin: 0 0 0.6rem 0;
        }

        .mini-kpi {
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        }

        .mini-kpi .label {
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }

        .mini-kpi .value {
            font-size: 1.5rem;
            font-weight: 800;
            margin-top: 6px;
            color: #0f172a;
        }

        .link-box {
            padding: 12px;
            border-radius: 14px;
            border: 1px solid #e2e8f0;
            background: rgba(255,255,255,0.9);
            text-align: center;
            font-size: 14px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        }

        .link-box .title {
            margin-bottom: 6px;
            font-weight: 700;
            color: #64748b;
        }

        .link-box-na {
            padding: 12px;
            border-radius: 14px;
            border: 1px dashed #cbd5e1;
            background: rgba(248,250,252,0.8);
            text-align: center;
            font-size: 14px;
            color: #94a3b8;
        }

        .stDataFrame, div[data-testid="stDataFrame"] {
            border-radius: 12px !important;
            overflow: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# CACHED LOADERS
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def load_csv(url: str) -> pd.DataFrame:
    return pd.read_csv(url)


@st.cache_data(show_spinner=False)
def load_geojson(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=300, show_spinner=False)
def load_main_data():
    csv_url_main = st.secrets["CSV_URL_MAIN"]
    csv_url_tools = st.secrets["CSV_URL_TOOLS"]
    csv_url_users = st.secrets["CSV_URL_USERS"]

    df_main = load_csv(csv_url_main)
    df_tools = load_csv(csv_url_tools)
    df_users = load_csv(csv_url_users)
    return df_main, df_tools, df_users


@st.cache_data(ttl=300, show_spinner=False)
def load_external_sheet(url: str) -> pd.DataFrame:
    return pd.read_csv(url)


# =========================================================
# UTILS
# =========================================================
def convert_df_to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def to_dt(x):
    return pd.to_datetime(x, dayfirst=True, errors="coerce")


def delay_days(plan_end, actual_end):
    if pd.notna(plan_end) and pd.notna(actual_end):
        d = (actual_end - plan_end).days
        return d if d > 0 else 0
    return 0


def safe_text(x, default=""):
    return default if pd.isna(x) else str(x)


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
        tooltip=folium.GeoJsonTooltip(
            fields=["NAME_1", "VISITS"],
            aliases=["Province:", "Visits:"],
            sticky=True,
        ),
    ).add_to(m)

    return m


def generate_stylish_horizontal_roadmap_html(steps, current_step_label):
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

    css_styles = """
    <style>
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 10px #2563eb, 0 0 20px #2563eb; }
            50% { box-shadow: 0 0 15px #3b82f6, 0 0 30px #3b82f6; }
        }
        @keyframes pulse-dot {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.5); opacity: 0.7; }
        }
        @keyframes flow-gradient {
            0% { background-position: 200% 0; }
            100% { background-position: -200% 0; }
        }
        body { font-family: Inter, sans-serif; background: transparent; }
        .track-main { background-color: #e2e8f0; }
        .track-progress {
            background: linear-gradient(90deg, #0d9488, #2dd4bf, #0d9488);
            background-size: 200% 100%;
            animation: flow-gradient 3s linear infinite;
        }
        .progress-comet {
            position:absolute; top:50%; transform:translateY(-50%);
            width:12px; height:12px; border-radius:50%;
            background-color:#5eead4;
            box-shadow:0 0 10px #2dd4bf, 0 0 20px #2dd4bf, -20px 0 30px #0d9488;
        }
        .node-ring-bg { background-color:#f8fafc; }
        .text-completed { color:#0d9488; }
        .text-ongoing { color:#2563eb; font-weight:700; }
        .text-upcoming { color:#64748b; }
        .node-ongoing .node-ring { animation: glow 2.5s ease-in-out infinite; }
        .node-ongoing .pulsing-dot { animation: pulse-dot 2s ease-in-out infinite; }
    </style>
    """

    num_steps = len(processed_steps)
    completed_steps = sum(1 for s in processed_steps if s["status"] == "completed")
    progress_percentage = (completed_steps / (num_steps - 1)) * 100 if num_steps > 1 else 0
    progress_width = f"calc({progress_percentage}% - {50 / (num_steps - 1)}%)" if num_steps > 1 else "0%"
    comet_position = f"calc({progress_percentage}% - {50 / (num_steps - 1)}% - 6px)" if num_steps > 1 else "-6px"

    html_content = f"""
    <head>
        <script src="https://cdn.tailwindcss.com"></script>
        {css_styles}
    </head>
    <body>
        <div class="w-full max-w-7xl mx-auto py-6 px-2">
            <div class="relative w-full">
                <div class="track-main absolute top-1/2 -translate-y-1/2 w-full h-2 rounded-full"></div>
                <div class="track-progress absolute top-1/2 -translate-y-1/2 h-2 rounded-full" style="width:{progress_width};"></div>
                <div class="progress-comet" style="left:{comet_position};"></div>
                <div class="relative flex justify-between items-start w-full">
    """

    for step in processed_steps:
        status = step["status"]
        label = step["label"]

        node_class, ring_color, icon_content, text_class = "", "", "", ""
        ring_size_class = "w-8 h-8"

        if status == "completed":
            ring_color = "border-teal-500"
            icon_content = '<div class="w-3 h-3 bg-teal-500 rounded-full shadow-lg"></div>'
            text_class = "text-completed"
        elif status == "ongoing":
            node_class = "node-ongoing"
            ring_color = "border-blue-500"
            icon_content = '<div class="pulsing-dot w-3 h-3 bg-blue-500 rounded-full"></div>'
            text_class = "text-ongoing"
            ring_size_class = "w-10 h-10"
        else:
            ring_color = "border-slate-400"
            icon_content = '<div class="w-3 h-3 bg-slate-400 rounded-full"></div>'
            text_class = "text-upcoming"

        html_content += f"""
        <div class="flex flex-col items-center text-center {node_class}" style="width:{100 / num_steps}%;">
            <div class="node-ring node-ring-bg {ring_size_class} rounded-full border-4 {ring_color} flex items-center justify-center z-10">
                {icon_content}
            </div>
            <p class="mt-10 text-sm font-medium {text_class} w-28">{label}</p>
        </div>
        """

    html_content += """
                </div>
            </div>
        </div>
    </body>
    """
    return html_content


# =========================================================
# TIMELINE CHART
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

            fig.add_trace(
                go.Scatter(
                    x=[ps, pe],
                    y=[y, y],
                    mode="lines",
                    line=dict(color=planned_color, width=PLANNED_W, dash="dash"),
                    showlegend=False,
                    hovertemplate=f"<b>{project}</b><br>{phase}<br>Planned: {ps:%d-%b-%Y} → {pe:%d-%b-%Y}<extra></extra>",
                )
            )

            if pd.notna(a_s):
                is_running = pd.isna(a_e)
                actual_end = a_e if pd.notna(a_e) else today
                actual_color = CURRENT_ACTUAL_COLOR if is_current else (ACTUAL_COLOR if not is_running else RUNNING_COLOR)

                fig.add_trace(
                    go.Scatter(
                        x=[a_s, actual_end],
                        y=[y, y],
                        mode="lines",
                        line=dict(color=actual_color, width=ACTUAL_W),
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
                        font=dict(size=22, color="#7f1d1d"),
                        bgcolor="rgba(255,255,255,0.6)",
                    )

                if not is_running:
                    d = delay_days(pe, a_e)
                    if d > 0:
                        fig.add_trace(
                            go.Scatter(
                                x=[a_e],
                                y=[y],
                                mode="markers+text",
                                marker=dict(size=8, color=DELAY_COLOR),
                                text=[f"+{d}d"],
                                textposition="top center",
                                textfont=dict(size=9, color=DELAY_COLOR),
                                showlegend=False,
                            )
                        )
                    else:
                        fig.add_annotation(
                            x=a_e,
                            y=y,
                            text="<b>🗹</b>",
                            showarrow=False,
                            font=dict(size=18, color=ONTIME_COLOR),
                            xshift=8,
                        )

            y += 1

        if project_y and responsible:
            fig.add_annotation(
                xref="paper",
                x=0.90,
                xanchor="left",
                y=sum(project_y) / len(project_y),
                yanchor="middle",
                text=f"<span style='color:#7c3aed;font-size:12px;'>● Now with: <b>{row.get('Responsible')}</b></span>",
                showarrow=False,
            )

        y += GAP

    fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.4)
    fig.add_annotation(
        x=today,
        y=0.99,
        xref="x",
        yref="paper",
        text="<b><i>Today</i></b>",
        showarrow=False,
        xanchor="center",
        yanchor="bottom",
        font=dict(size=12, color="#0F5448"),
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=y_vals,
        ticktext=y_labels,
        autorange="reversed",
        title="",
    )

    start_candidates = [ps_c for _, ps_c, _, _, _ in PHASES if ps_c in project_data.columns]
    end_candidates = [pe_c for _, _, pe_c, _, _ in PHASES if pe_c in project_data.columns]

    min_x = project_data[start_candidates].min().min() if start_candidates else today - pd.Timedelta(days=30)
    max_x = project_data[end_candidates].max().max() if end_candidates else today + pd.Timedelta(days=30)

    fig.update_xaxes(
        range=[min_x, max_x + pd.Timedelta(days=20)],
        showgrid=True,
        gridcolor="rgba(0,0,0,0.05)",
        zeroline=False,
    )

    fig.update_layout(
        height=max(380, 20 * len(y_vals)),
        margin=dict(l=95, r=80, t=20, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        hovermode="closest",
    )
    return fig


# =========================================================
# PROJECT DATA PREP
# =========================================================
@st.cache_data(ttl=300, show_spinner=False)
def prepare_project_dataset(selected_project, selected_tool_tuple, qastatus_tuple, completion_tuple):
    df, df_tools, _ = load_main_data()

    project_data = df[df["Project Name"] == selected_project].reset_index(drop=True)
    if project_data.empty:
        return None

    project_data_tools = df_tools[df_tools["Project Name"] == selected_project].reset_index(drop=True)
    tool_col_map = project_data_tools.set_index("Tool")["main_cols"].to_dict()

    rawsheet = project_data.loc[0, "raw_sheet"]
    Project_QA_ID = project_data.loc[0, "Sampling_ID"]
    Project_QA_ID2 = project_data.loc[0, "QAlog_ID"]
    Project_QA_ID3 = project_data.loc[0, "HFC_ID"]

    raw_sheet_id = rawsheet.split("/d/")[1].split("/")[0]
    raw_csv_url = f"https://docs.google.com/spreadsheets/d/{raw_sheet_id}/export?format=csv&id={raw_sheet_id}&gid=0"
    t = load_external_sheet(raw_csv_url).copy()

    t["KEY_Unique"] = t["KEY"]

    qasheet = f"https://docs.google.com/spreadsheets/d/1V1SfBZUwHN0NtXFIoiXEh7JGkpTUOLZnGAfFN8QVXYQ/export?format=csv&{Project_QA_ID2}"
    qalog = load_external_sheet(qasheet).copy()

    merge_cols = [c for c in ["QA_Status", "KEY_Unique", "Issue_Type", "Issue_Description", "surveyor_notified", "surveyor_response", "issue_resolved"] if c in qalog.columns]
    qalog_merge = qalog[merge_cols].drop_duplicates("KEY_Unique") if "KEY_Unique" in qalog.columns else pd.DataFrame()

    if not qalog_merge.empty:
        t = pd.merge(t, qalog_merge[["QA_Status", "KEY_Unique"]].drop_duplicates("KEY_Unique"), on="KEY_Unique", how="left")

    t["QA_Status"] = t["QA_Status"].replace("", "Not QA'ed Yet")
    t["QA_Status"] = t["QA_Status"].fillna("Not QA'ed Yet")
    t["Completion_status"] = "Complete"

    # Optional project custom code
    extra_code = safe_text(project_data.loc[0, "extra_code"], "-")
    if extra_code and extra_code != "-":
        local_scope = {"t": t, "pd": pd, "np": np}
        try:
            exec(extra_code, {"__builtins__": {}}, local_scope)
            t = local_scope.get("t", t)
        except Exception as e:
            st.warning(f"extra_code could not be executed for this project: {e}")

    t = t.sort_values(by=["QA_Status", "Completion_status"], ascending=True)

    # occurance
    t["occurance"] = None
    for tool, cols in tool_col_map.items():
        group_cols = [c for c in cols.split("-") if c and c != "occurance" and c in t.columns]
        if not group_cols:
            continue
        mask = t["Tool"] == tool
        t.loc[mask, "occurance"] = t.loc[mask].groupby(group_cols).cumcount() + 1
    t["occurance"] = t["occurance"].fillna(9999).astype(int)

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

    t["V_ID"] = t.apply(compute_vid, axis=1)

    samplingsheet = f"https://docs.google.com/spreadsheets/d/1U0Y7TQnTFEg1edMb0IHejOxv9S2YLY2UH-tp1qzXyBg/export?format=csv&{Project_QA_ID}"
    tari = load_external_sheet(samplingsheet).copy()
    tari["V_ID"] = tari["Tool"] + "/" + tari["V_ID"].astype(str)
    tari = tari[tari["Skipped"] != "Yes"]

    if "Tool" in project_data_tools.columns:
        tari = tari[(tari["Tool"].isin(t["Tool"].unique())) & (tari["Tool"].isin(project_data_tools["Tool"]))]

    df_free = t[t["Tool"].isin(project_data_tools["Tool"]) & ~t["Tool"].isin(tari["Tool"])].copy()
    df_free = df_free.drop(columns=["KEY", "QA_Status"], errors="ignore")
    df_free = df_free[tari.columns.intersection(df_free.columns)]
    tari = pd.concat([tari, df_free], ignore_index=True)

    selected_tool = list(selected_tool_tuple)
    qastatus = list(qastatus_tuple)
    completion = list(completion_tuple)

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

    tall["d1"] = pd.to_datetime(tall["SubmissionDate"], format="%b %d, %Y %H:%M:%S", errors="coerce").dt.date if "SubmissionDate" in tall.columns else pd.NaT
    tall["d2"] = pd.to_datetime(tall["SubmissionDate"], format="%Y-%m-%dT%H:%M:%S.%fZ", errors="coerce").dt.date if "SubmissionDate" in tall.columns else pd.NaT
    tall["Date"] = tall["d1"].fillna(tall["d2"])
    tall["Date"] = pd.to_datetime(tall["Date"], errors="coerce")
    tall["Date"] = tall["Date"].dt.strftime("%Y-%m-%d")
    tall = tall.drop(columns=["SubmissionDate", "occurance", "d1", "d2"], errors="ignore")

    tall2 = None
    first_tool_map = list(tool_col_map.values())[0] if len(tool_col_map) > 0 else ""
    if first_tool_map.rsplit("-", 1)[-1] == "occurance":
        base_ids = tari["V_ID"].str.rsplit("-", n=1).str[0].dropna().unique()
        tall2 = t[t["V_ID"].str.startswith(tuple(base_ids), na=False)]

    # Missing / extra / duplicate
    missing = pd.DataFrame(columns=["Tool", "V_ID", "KEY", "Type", "QA_Status"])
    m = tari[~tari.V_ID.isin(t["V_ID"])].copy()
    m["Type"] = "Missing Data"

    ext = t[(~t.V_ID.isin(tari["V_ID"])) & (t.QA_Status == "Approved")][["Tool", "V_ID", "KEY", "QA_Status"]].copy()
    ext["Type"] = "Extra data"

    dup = t[t.V_ID.duplicated(keep="first")][["Tool", "V_ID", "KEY", "QA_Status"]].copy()
    dup["Type"] = "Duplicate Data"

    missing = pd.concat([missing, m, ext, dup], ignore_index=True)

    # Exclude extra + duplicate from tall
    bad_keys = pd.concat([ext["KEY"], dup["KEY"]], ignore_index=True).dropna().unique().tolist() if "KEY" in t.columns else []
    if "KEY" in tall.columns and bad_keys:
        tall = tall[~tall["KEY"].isin(bad_keys)]

    # HFC for report
    hfcsheet = f"https://docs.google.com/spreadsheets/d/16EWCV7HTEx729ILvsYa72LkJ1P1Sw7Fo2R0FzXs3GvE/export?format=csv&{Project_QA_ID3}"
    hfc = load_external_sheet(hfcsheet).copy()

    return {
        "project_data": project_data,
        "project_data_tools": project_data_tools,
        "tool_col_map": tool_col_map,
        "t": t,
        "tari": tari,
        "tall": tall,
        "tall2": tall2,
        "qalog": qalog,
        "hfc": hfc,
        "missing": missing,
    }


# =========================================================
# SURVEYOR REPORT
# =========================================================
def score_surveyors(df: pd.DataFrame, w_rej=0.35, w_out=0.10, w_out2=0.2, w_fb=0.35) -> pd.DataFrame:
    df = df.copy()
    score = 100 - (
        df["rejection_ratio"] * 100 * w_rej
        + df["hfc_outliers_ratio"] * 100 * w_out
        + df["ta_outliers"] * 100 * w_out2
        + df["total_feedback_ratio"] * 100 * w_fb
    )
    df["score"] = score.round(1).clip(0, 100)

    conds = [df["score"] >= 85, df["score"] >= 70, df["score"] >= 55]
    df["band"] = np.select(conds, ["Excellent", "Good", "Watch"], default="Critical")
    df["band_color"] = np.select(conds, ["#10b981", "#3b82f6", "#f59e0b"], default="#ef4444")
    df["recommendation"] = np.select(
        conds,
        ["Maintain monitoring", "Minor coaching", "Verify records"],
        default="Urgent Retraining",
    )
    return df


def build_html_report(project: str, meta: str, summary_df: pd.DataFrame, issues_df: pd.DataFrame) -> str:
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
    not_notified_count = int(issues_df["surveyor_response"].fillna("").eq("").sum()) if "surveyor_response" in issues_df.columns else 0
    high_severity = int((issues_df.get("severity") == "High").sum()) if total_issues else 0
    avg_score = float(summary_df["score"].mean()) if len(summary_df) else 0.0

    matrix_df = summary_df.sort_values("score", ascending=True).head(10)
    matrix_rows = "".join(
        f"""
        <tr>
          <td>
            <div class="name">{r.Surveyor_Name}</div>
            <div class="muted">ID: SURV-{abs(hash(r.Surveyor_Name)) % 1000}</div>
          </td>
          <td class="c">
            <div class="score">{r.score}</div>
            <div class="bar"><span style="width:{r.score}%;background:{r.band_color}"></span></div>
          </td>
          <td><span class="pill" style="background:{r.band_color}">{r.band}</span></td>
          <td class="c mono">{int(r.total_submissions)}</td>
          <td class="c mono">{int(r.rejected_count)}</td>
          <td class="c mono red">{(r.rejection_ratio*100):.1f}%</td>
          <td class="c mono blue">{(r.total_feedback_ratio*100):.1f}%</td>
          <td class="c mono blue">{(r.hfc_outliers_ratio*100):.1f}%</td>
          <td class="c mono">{(float(getattr(r, "ta_outliers", 0.0))*100):.1f}%</td>
          <td class="rec">{r.recommendation}</td>
        </tr>
        """
        for r in matrix_df.itertuples(index=False)
    )

    issues_json = issues_df.to_json(orient="records")

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>{project} - QA Report</title>
<style>
  :root {{
    --bg:#f6f7fb; --card:#fff; --text:#0f172a; --muted:#64748b; --line:#e5e7eb;
    --issue-bg:#fff7ed; --issue-bd:#fed7aa; --issue-date:#9a3412; --issue-txt:#7c2d12;
    --resp-bg:#f8fafc;  --resp-bd:#e2e8f0;  --resp-date:#0f766e;  --resp-txt:#334155;
  }}
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
  .c{{text-align:center}}
  .mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}}
  .name{{font-weight:900}}
  .score{{font-weight:900}}
  .pill{{display:inline-block;padding:4px 8px;border-radius:999px;color:#fff;font-size:11px;font-weight:900}}
  .rec{{color:var(--muted);font-style:italic;font-size:12px}}
  .red{{color:#dc2626}} .blue{{color:#2563eb}}
  .filters{{display:grid;grid-template-columns:1fr 180px 220px 140px;gap:10px;margin-top:12px}}
  input,select{{padding:10px 12px;border:1px solid var(--line);border-radius:12px;font-size:13px;background:#fff}}
  .ghost{{background:#f1f5f9;color:#0f172a}}
  .ticker tbody tr{{border-bottom:1px dashed #e5e7eb}}
  .ticker tbody tr:last-child{{border-bottom:none}}
  .ticker tbody tr td{{padding-top:18px;padding-bottom:18px}}
  .comment {{ margin-top:8px; padding:10px 12px; border-radius:12px; border:1px solid; }}
  .comment-date {{ font-weight:900; font-size:12px; letter-spacing:.02em; }}
  .comment-body {{ margin-top:4px; line-height:1.35; }}
  .comment-divider {{ height:1px; margin:10px 2px; background: linear-gradient(90deg, rgba(148,163,184,0), rgba(148,163,184,0.85), rgba(148,163,184,0)); }}
  .issue-comments .comment {{ background:var(--issue-bg); border-color:var(--issue-bd); border-left:4px solid #fb923c; }}
  .issue-comments .comment-date {{ color:var(--issue-date); }}
  .issue-comments .comment-body {{ color:var(--issue-txt); }}
  .response-comments .comment {{ background:var(--resp-bg); border-color:var(--resp-bd); border-left:4px solid #14b8a6; }}
  .response-comments .comment-date {{ color:var(--resp-date); }}
  .response-comments .comment-body {{ color:var(--resp-txt); font-style:italic; }}
  .awaiting-response{{color:#b91c1c;opacity:0.45;font-style:italic;font-weight:300;}}
  @media print {{
    .no-print{{display:none!important}}
    body{{background:#fff}}
    .wrap{{padding:0}}
    .card{{border:0}}
  }}
  @media (max-width: 900px){{
    .grid{{grid-template-columns:repeat(2,1fr)}}
    .filters{{grid-template-columns:1fr}}
  }}
</style>
</head>
<body>
  <div class="wrap">
    <div class="card top">
      <div>
        <span class="badge">{meta}</span>
        <span class="muted" style="margin-left:10px">Report Generated: {now}</span>
        <h1>{project}</h1>
        <div class="muted">Surveyor Quality Matrix + Detailed Feedback Log</div>
      </div>
      <button class="btn no-print" onclick="window.print()">Export PDF</button>
    </div>

    <div class="grid">
      <div class="card kpi">
        <div class="label">Overall Quality Score</div>
        <div class="val">{avg_score:.1f} <span class="muted">/ 100</span></div>
        <div class="bar"><span style="width:{avg_score}%;background:#6366f1"></span></div>
      </div>
      <div class="card kpi">
        <div class="label">Total Recorded Cases (QA Dept.)</div>
        <div class="val" style="color:#4f46e5">{total_issues}</div>
        <div class="muted">{resolved_count} Resolved • {pending_count} Open</div>
      </div>
      <div class="card kpi">
        <div class="label">Surveyor Notifications (DC Dept.)</div>
        <div class="val">{notified_count}</div>
        <div class="muted">Awaiting field responses for {not_notified_count} cases.</div>
      </div>
      <div class="card kpi">
        <div class="label">Critical (High severity)</div>
        <div class="val" style="color:#dc2626">{high_severity}</div>
        <div class="muted">Immediate coaching required</div>
      </div>
    </div>

    <div class="card tablecard">
      <div class="thead">
        <div style="font-weight:900">Surveyor Performance Matrix (Worst 10)</div>
        <div class="muted">Lowest quality score surveyors [SCORE=0.35 x Rej + 0.35 x Feedbacks + 0.3 x Outliers]</div>
      </div>
      <div style="overflow:auto">
        <table>
          <thead>
            <tr>
              <th>Surveyor</th>
              <th class="c">Score</th>
              <th>Band</th>
              <th class="c">Total Subs</th>
              <th class="c">Rej #</th>
              <th class="c">Rej %</th>
              <th class="c">Feedback %</th>
              <th class="c">Data incons. %</th>
              <th class="c">Speed Vio. %</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>{matrix_rows}</tbody>
        </table>
      </div>
    </div>

    <div class="card tablecard" style="margin-top:12px">
      <div class="thead">
        <div style="font-weight:900;text-align:center">Detailed Feedback Log</div>

        <div class="filters no-print">
          <input id="q" placeholder="Search logs..." />
          <select id="fResolved">
            <option value="">Status: All</option>
            <option value="Yes">Resolved</option>
            <option value="No">Pending</option>
          </select>
          <select id="fSurveyor">
            <option value="">Surveyor: All</option>
          </select>
          <button class="btn ghost" id="reset" type="button">Clear</button>
        </div>
      </div>

      <div style="overflow:auto">
        <table class="ticker">
          <thead>
            <tr>
              <th>Verification Detail</th>
              <th>Surveyor Response</th>
              <th class="c">Severity</th>
              <th class="c">Status</th>
            </tr>
          </thead>
          <tbody id="tbody"></tbody>
        </table>
      </div>
    </div>
  </div>

<script>
  const data = {issues_json};
  const tbody = document.getElementById('tbody');
  const sSelect = document.getElementById('fSurveyor');

  const uniq = Array.from(new Set(data.map(x => x.Surveyor_Name))).filter(Boolean).sort();
  for (const s of uniq) {{
    const o = document.createElement('option');
    o.value = s; o.textContent = s;
    sSelect.appendChild(o);
  }}

  function esc(x) {{
    return String(x ?? "").replace(/[&<>"']/g, m => ({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}})[m]);
  }}

  function formatComments(raw) {{
    const s = String(raw ?? "").trim();
    if (!s) return "";

    const re = /\\[(\\d{{1,2}}\\/\\d{{1,2}}\\/\\d{{4}})\\]\\s*:?:?\\s*/g;
    let match, lastIndex = 0, lastDate = null;
    const blocks = [];

    while ((match = re.exec(s)) !== null) {{
      if (lastDate !== null) {{
        blocks.push({{ date:lastDate, body: s.slice(lastIndex, match.index).trim() }});
      }}
      lastDate = match[1];
      lastIndex = re.lastIndex;
    }}
    if (lastDate !== null) {{
      blocks.push({{ date:lastDate, body: s.slice(lastIndex).trim() }});
    }}
    if (!blocks.length) return esc(s);

    let html = "";
    for (let i = 0; i < blocks.length; i++) {{
      if (i > 0) html += '<div class="comment-divider"></div>';
      html += `
        <div class="comment">
          <div class="comment-date">[${{esc(blocks[i].date)}}]</div>
          <div class="comment-body">${{esc(blocks[i].body)}}</div>
        </div>`;
    }}
    return html;
  }}

  function render() {{
    const q = document.getElementById('q').value.toLowerCase();
    const res = document.getElementById('fResolved').value;
    const sur = document.getElementById('fSurveyor').value;
    const out = [];

    for (const i of data) {{
      if (res && i.issue_resolved !== res) continue;
      if (sur && i.Surveyor_Name !== sur) continue;

      if (q) {{
        const blob = (
          (i.Surveyor_Name||"") + " " + (i.KEY||"") + " " + (i.Site_Visit_ID||"") + " " +
          (i.QA_Status||"") + " " + (i.Location||"") + " " + (i.Issue_Type||"") + " " +
          (i.Issue_Description||"") + " " + (i.surveyor_response||"")
        ).toLowerCase();
        if (!blob.includes(q)) continue;
      }}

      out.push(`
        <tr>
          <td>
            <div class="muted" style="font-weight:900;letter-spacing:.08em;text-transform:uppercase;color:#4f46e5">
              ${{esc(i.Surveyor_Name)}}
            </div>
            <div class="muted">KEY: ${{esc(i.KEY)}}</div>
            <div class="muted">Site_Visit_ID: ${{esc(i.Site_Visit_ID)}}</div>
            <div class="muted">Location: ${{esc(i.Location)}}</div>
            <div style="margin-top:8px;"></div>
            <div style="font-weight:700;font-size:0.9rem;margin-top:4px"><span style="font-weight:900;">Issue Type:</span> <span style="font-weight:400;text-decoration:underline;">${{esc(i.Issue_Type)}}</span></div>
            <div class="muted">QA Status: <span style="font-weight:900;text-decoration:underline;color:${{i.QA_Status==='Rejected' ? '#ef4444' : (i.QA_Status==='Approved' ? '#10b981' : '#94a3b8')}};">${{esc(i.QA_Status)}}</span></div>
            <div class="muted" style="margin-top:10px">
              <span style="color:#dc2626;font-weight:900">ISSUE:</span>
              <div class="issue-comments">${{formatComments(i.Issue_Description)}}</div>
            </div>
          </td>
          <td>
            <div class="response-comments">
              ${{ i.surveyor_response ? formatComments(i.surveyor_response) : '<div class="awaiting-response">Awaiting response from DC/field...</div>'}}
            </div>
          </td>
          <td class="c">
            <span class="pill" style="background:#e2e8f0;color:#0f172a">${{esc(i.severity)}}</span>
          </td>
          <td class="c">
            <span class="pill" style="background:${{i.issue_resolved === "Yes" ? "#dcfce7" : "#ffe4e6"}};color:${{i.issue_resolved === "Yes" ? "#166534" : "#9f1239"}}">
              ${{i.issue_resolved === "Yes" ? "Closed" : "Pending"}}
            </span>
          </td>
        </tr>
      `);
    }}
    tbody.innerHTML = out.join("");
  }}

  document.getElementById('q').addEventListener('input', render);
  document.getElementById('fResolved').addEventListener('input', render);
  document.getElementById('fSurveyor').addEventListener('input', render);
  document.getElementById('reset').addEventListener('click', () => {{
    document.getElementById('q').value = "";
    document.getElementById('fResolved').value = "";
    document.getElementById('fSurveyor').value = "";
    render();
  }});

  render();
</script>
</body>
</html>"""


# =========================================================
# AUTH
# =========================================================
def init_state():
    defaults = {
        "logged_in": False,
        "username": None,
        "filters_initialized": False,
        "applied_main_project": None,
        "applied_selected_project": None,
        "applied_selected_tool": [],
        "applied_qastatus": [],
        "applied_completion": ["Complete", "Incomplete"],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def logout():
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    st.cache_data.clear()
    st.rerun()


# =========================================================
# APP
# =========================================================
init_state()
df, df_tools, df_users = load_main_data()
user_dict = df_users.set_index("users")[["password", "project"]].to_dict(orient="index")

if not st.session_state.logged_in:
    with st.container():
        st.markdown("<div class='app-card'>", unsafe_allow_html=True)
        st.markdown("### ATR Consulting - Data Collection / QA Progress Tracker")
        st.markdown(
            """
            <div class="soft-card" style="margin-bottom:16px;">
                <b>About this app</b><br>
                Track data collection, QA progress, project status, summaries, and downloadable reports in one place.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True, type="primary")

        if submit:
            if username in user_dict and password == user_dict[username]["password"]:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Incorrect username or password.")
        st.markdown("</div>", unsafe_allow_html=True)

else:
    username = st.session_state.username

    # --------------------------------------------
    # Header
    # --------------------------------------------
    c1, c2 = st.columns([8, 2])
    with c1:
        st.markdown("<p class='hero-title'>QA and DC Progress Tracker</p>", unsafe_allow_html=True)
        st.markdown(
            "<p class='hero-sub'>Fast mode enabled: data reload happens only when you click <b>Apply filters</b> or <b>Refresh data</b>.</p>",
            unsafe_allow_html=True,
        )
    with c2:
        top_a, top_b = st.columns(2)
        with top_a:
            if st.button("🔄 Refresh data", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        with top_b:
            if st.button("Logout", use_container_width=True):
                logout()

    st.toast(
        "Use Apply filters to update the dashboard.\n"
        "Refresh data clears cache and reloads all sources."
    )

    # --------------------------------------------
    # Available main projects
    # --------------------------------------------
    user_projects = user_dict[username]["project"].split(",")
    if user_projects[0] == "All":
        main_project_names = sorted(df["Main Project"].dropna().unique().tolist())
    else:
        main_project_names = sorted(
            df[df["Main Project"].isin(user_projects)]["Main Project"].dropna().unique().tolist()
        )

    # --------------------------------------------
    # Initial filter state
    # --------------------------------------------
    if not st.session_state.filters_initialized:
        default_main = main_project_names[0] if main_project_names else None
        project_names_default = (
            sorted(df[df["Main Project"] == default_main]["Project Name"].dropna().unique().tolist())
            if default_main is not None else []
        )
        default_project = project_names_default[0] if project_names_default else None

        default_tool_names = (
            sorted(df_tools[df_tools["Project Name"] == default_project]["Tool"].dropna().unique().tolist())
            if default_project is not None else []
        )

        st.session_state.applied_main_project = default_main
        st.session_state.applied_selected_project = default_project
        st.session_state.applied_selected_tool = []
        st.session_state.applied_qastatus = ["Not QA'ed Yet", "Pending", "Approved", "Rejected"]
        st.session_state.applied_completion = ["Complete", "Incomplete"]
        st.session_state.filters_initialized = True

    # --------------------------------------------
    # CONTROL PANEL (FORM = no rerun until submit)
    # --------------------------------------------
    st.markdown("<div class='app-card'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Control panel</p>", unsafe_allow_html=True)

    with st.form("filter_form", clear_on_submit=False):
        selected_main_project_form = st.selectbox(
            "Main Project",
            options=main_project_names,
            index=main_project_names.index(st.session_state.applied_main_project) if st.session_state.applied_main_project in main_project_names else 0,
        )

        project_names = sorted(
            df[df["Main Project"] == selected_main_project_form]["Project Name"].dropna().unique().tolist()
        )

        selected_project_form = st.selectbox(
            "Round / Sub-Project",
            options=project_names,
            index=project_names.index(st.session_state.applied_selected_project) if st.session_state.applied_selected_project in project_names else 0,
        )

        tool_names = sorted(
            df_tools[df_tools["Project Name"] == selected_project_form]["Tool"].dropna().unique().tolist()
        )

        cfa, cfb, cfc = st.columns(3)
        with cfa:
            selected_tool_form = st.multiselect(
                "Tool",
                options=tool_names,
                default=[x for x in st.session_state.applied_selected_tool if x in tool_names],
            )
        with cfb:
            qastatus_options = ["Not QA'ed Yet", "Pending", "Approved", "Rejected", "Rejected_paused"]
            qastatus_form = st.multiselect(
                "QA Status",
                options=qastatus_options,
                default=st.session_state.applied_qastatus or ["Not QA'ed Yet", "Pending", "Approved", "Rejected"],
            )
        with cfc:
            completion_form = st.multiselect(
                "Completion Status",
                options=["Complete", "Incomplete"],
                default=st.session_state.applied_completion or ["Complete", "Incomplete"],
            )

        apply_filters = st.form_submit_button("Apply filters", use_container_width=True, type="primary")

    st.markdown("</div>", unsafe_allow_html=True)

    if apply_filters:
        st.session_state.applied_main_project = selected_main_project_form
        st.session_state.applied_selected_project = selected_project_form
        st.session_state.applied_selected_tool = selected_tool_form
        st.session_state.applied_qastatus = qastatus_form if qastatus_form else qastatus_options
        st.session_state.applied_completion = completion_form if completion_form else ["Complete", "Incomplete"]
        st.rerun()

    main_project = st.session_state.applied_main_project
    selected_project = st.session_state.applied_selected_project
    selected_tool = st.session_state.applied_selected_tool
    qastatus = st.session_state.applied_qastatus
    completion = st.session_state.applied_completion

    # --------------------------------------------
    # Header metrics
    # --------------------------------------------
    current_main_df = df[df["Main Project"] == main_project]
    mk1, mk2, mk3 = st.columns(3)
    with mk1:
        st.markdown(
            f"<div class='mini-kpi'><div class='label'>Main project</div><div class='value'>{main_project}</div></div>",
            unsafe_allow_html=True,
        )
    with mk2:
        st.markdown(
            f"<div class='mini-kpi'><div class='label'>Sub-project</div><div class='value'>{selected_project}</div></div>",
            unsafe_allow_html=True,
        )
    with mk3:
        st.markdown(
            f"<div class='mini-kpi'><div class='label'>Rounds in main project</div><div class='value'>{current_main_df['Project Name'].nunique()}</div></div>",
            unsafe_allow_html=True,
        )

    # --------------------------------------------
    # Timeline
    # --------------------------------------------
    st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Project Timeline</p>", unsafe_allow_html=True)

    main_project_data = df[df["Main Project"] == main_project].reset_index(drop=True)
    timeline_fig = build_project_timeline(main_project_data)

    st.markdown(
        "<div style='font-size:12px;color:#555;margin-bottom:8px;'>"
        "<b>— — —</b> Planned &nbsp;&nbsp;"
        "<b>▬</b> Actual &nbsp;&nbsp;"
        "<span style='color:#3b82f6'><b>↝</b></span> Ongoing &nbsp;&nbsp;"
        "<span style='color:#22c55e'><b>🗹</b></span> On time &nbsp;&nbsp;"
        "<span style='color:#ef4444'><b>●</b></span> Delayed"
        "</div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(timeline_fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------
    # Project dataset
    # --------------------------------------------
    with st.spinner("Preparing project data..."):
        data_bundle = prepare_project_dataset(
            selected_project,
            tuple(selected_tool),
            tuple(qastatus),
            tuple(completion),
        )

    if data_bundle is None:
        st.error("No data found for selected project.")
        st.stop()

    project_data = data_bundle["project_data"]
    project_data_tools = data_bundle["project_data_tools"]
    t = data_bundle["t"]
    tari = data_bundle["tari"]
    tall = data_bundle["tall"]
    tall2 = data_bundle["tall2"]
    qalog = data_bundle["qalog"]
    hfc = data_bundle["hfc"]
    missing = data_bundle["missing"]

    proj_completed = safe_text(project_data.loc[0, "Completed"])
    def_var0, def_var1, def_var2 = parse_default_vars(safe_text(project_data.loc[0, "Summary_defualt_var"], "-"))

    # --------------------------------------------
    # Workflow roadmap
    # --------------------------------------------
    st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Workflow Progress</p>", unsafe_allow_html=True)

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
    current_step = safe_text(project_data.loc[0, "current_step"], "")
    roadmap_html = generate_stylish_horizontal_roadmap_html(steps_data, current_step)
    st.components.v1.html(roadmap_html, height=180)
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------
    # Links
    # --------------------------------------------
    st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Project Links</p>", unsafe_allow_html=True)

    link_labels = {
        "Tool link": "🛠 Tool",
        "XLSForm link": "📄 XLSForm",
        "QA-Notes link": "📊 QA Notes",
        "Tracker link": "📈 QA Tracker",
        "DC Tracker": "📍 DC Tracker",
        "Document folder link": "📁 Docs",
    }
    links_row = project_data[list(link_labels.keys())].iloc[0]
    link_cols = st.columns(6)

    for i, (col_name, label) in enumerate(link_labels.items()):
        value = links_row[col_name]
        with link_cols[i]:
            if pd.notna(value) and str(value).strip():
                st.markdown(
                    f"""
                    <div class="link-box">
                        <div class="title">{label}</div>
                        <a href="{value}" target="_blank" style="color:#0ea5e9;text-decoration:none;font-weight:600;">🔗 Open</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="link-box-na">
                        <div style="margin-bottom:6px;font-weight:700;">{label}</div>
                        <span style="font-style:italic;">N/A</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    st.markdown("</div>", unsafe_allow_html=True)

    # --------------------------------------------
    # Archived notice
    # --------------------------------------------
    if proj_completed == "Yes":
        st.info(
            "This project is archived. For complete information on sampling and site visits, please check the document links and trackers above."
        )

    # --------------------------------------------
    # Data Metrics
    # --------------------------------------------
    if proj_completed != "Yes":
        st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Data Metrics</p>", unsafe_allow_html=True)

        # timeline counts
        dff = tall["Date"].value_counts().reset_index()
        dff.columns = ["Date", "N"]
        dff = dff.sort_values(by="Date", ascending=False)

        fig_line = px.line(dff, x="Date", y="N", title="Timeline of Data")
        fig_line.update_traces(mode="lines+markers", marker=dict(size=9))
        fig_line.update_layout(
            xaxis_title="Date",
            yaxis_title="N",
            template="plotly_white",
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
        )

        counts = t.groupby("Province").size().reset_index(name="count") if "Province" in t.columns else pd.DataFrame(columns=["Province", "count"])
        counts["Province"] = counts["Province"].astype(str).str.strip()
        geo_raw = load_geojson("afghanistan_provinces.geojson")
        my_map = build_map(geo_raw, counts)

        cm1, cm2 = st.columns(2)
        with cm1:
            st_folium(my_map, height=320, use_container_width=True, returned_objects=[], key="afg_map")
        with cm2:
            st.plotly_chart(fig_line, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # --------------------------------------------
        # Sample Tracking
        # --------------------------------------------
        st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
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
        fig1.update_layout(title_text="Data Collection Progress", template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))

        fig2 = go.Figure(data=[go.Pie(labels=g["QA_Status"], values=g["count"], hole=0.6, textinfo="label+percent")])
        fig2.update_layout(title_text="Data QA Progress", template="plotly_white", margin=dict(l=20, r=20, t=50, b=20))

        cc1, cc2 = st.columns(2)
        with cc1:
            st.plotly_chart(fig1, use_container_width=True)
        with cc2:
            st.plotly_chart(fig2, use_container_width=True)

        d1, d2 = st.columns([1, 1])
        with d1:
            tari_csv = convert_df_to_csv(tari)
            st.download_button(
                label="Download Target Data Details",
                data=tari_csv,
                file_name="Sample_Tracking.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with d2:
            missing_csv = convert_df_to_csv(missing)
            st.download_button(
                label="Download Missing / Extra / Duplicate Data",
                data=missing_csv,
                file_name="Missing_Extra_Duplicate.csv",
                mime="text/csv",
                use_container_width=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # --------------------------------------------
        # Notes
        # --------------------------------------------
        project_notes = safe_text(project_data.loc[0, "notes"], "-")
        if project_notes != "-":
            st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
            st.markdown("<p class='section-title'>Project Notes</p>", unsafe_allow_html=True)
            try:
                st.markdown(eval(project_notes[1:-1]), unsafe_allow_html=True)
            except Exception:
                st.markdown(project_notes)
            st.markdown("</div>", unsafe_allow_html=True)

        # --------------------------------------------
        # Summary Generation
        # --------------------------------------------
        st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
        st.markdown("<p class='section-title'>Summary Generation</p>", unsafe_allow_html=True)
        st.info(
            'Summaries include both "Complete" and "Incomplete" submissions by default. '
            'For accurate tracking, select only "Complete" in the Control panel.'
        )

        s1, s2 = st.columns(2)
        with s1:
            disag2 = st.multiselect(
                "Create Sample Summary",
                tari.columns.tolist(),
                default=[x for x in def_var0 if x in tari.columns],
                help="Create summaries from selected sample tracking columns.",
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
                help="Create summaries from selected dataset columns.",
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
                "Tryouts Summary (Phone Surveys)",
                tall2.columns.tolist(),
                default=[x for x in def_var2 if x in tall2.columns],
                help="Useful for phone surveys and repeated call attempts.",
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

    # --------------------------------------------
    # Project Updates
    # --------------------------------------------
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
        st.markdown(
            """
            <style>
              .upd-day {margin: 10px 0 14px 0; padding-left: 14px; border-left: 3px solid #e8eef7;}
              .upd-date {font-weight: 700; margin-bottom: 6px; color: #7a1f1f;}
              .upd-item {margin: 4px 0; color: #0f172a;}
              .upd-dot {color: #94a3b8; margin-right: 8px;}
              .upd-sep {height: 1px; background: #eef2f7; margin: 12px 0;}
            </style>
            """,
            unsafe_allow_html=True,
        )

        days = list(by_day.items())
        for i, (d, msgs) in enumerate(days):
            st.markdown(
                f"""
                <div class="upd-day">
                  <div class="upd-date">{d.strftime('%d %b %Y')}</div>
                  {''.join([f"<div class='upd-item'><span class='upd-dot'>•</span>{m}</div>" for m in msgs])}
                </div>
                {"<div class='upd-sep'></div>" if i < len(days)-1 else ""}
                """,
                unsafe_allow_html=True,
            )

    # --------------------------------------------
    # Surveyor Report
    # --------------------------------------------
    st.markdown("<div class='app-card' style='margin-top:14px;'>", unsafe_allow_html=True)
    st.markdown("<p class='section-title'>Surveyor Performance Report</p>", unsafe_allow_html=True)
    create_report = st.button("Generate Surveyor Performance Report", type="primary")

    if create_report:
        if qalog.empty or tall.empty:
            st.warning("Not enough data available to generate the surveyor report.")
        else:
            merge_cols = [c for c in ["Issue_Type", "Issue_Description", "surveyor_notified", "surveyor_response", "issue_resolved", "KEY_Unique"] if c in qalog.columns]
            qalog2 = pd.merge(
                tall,
                qalog[merge_cols],
                on="KEY_Unique",
                how="left",
            )

            qalog2["severity"] = qalog2["QA_Status"].map({"Rejected": "High", "Approved": "Low", "Pending": "Medium"}).fillna("Low")

            issues_cols = [c for c in [
                "Site_Visit_ID", "Province", "Village", "severity", "QA_Status", "Surveyor_Name", "KEY",
                "Issue_Type", "Issue_Description", "surveyor_notified", "surveyor_response", "issue_resolved"
            ] if c in qalog2.columns]
            issues = qalog2[issues_cols].copy()

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

            issues = issues[issues["Issue_Type"].notna()].copy() if "Issue_Type" in issues.columns else issues.copy()

            for col in ["issue_resolved", "Issue_Description", "surveyor_response", "Province", "Village", "Site_Visit_ID", "Surveyor_Name", "Issue_Type", "KEY"]:
                if col in issues.columns:
                    issues[col] = issues[col].fillna("")
            if "issue_resolved" in issues.columns:
                issues["issue_resolved"] = issues["issue_resolved"].replace("", "No")
            if {"Province", "Village"}.issubset(issues.columns):
                issues["Location"] = issues["Province"] + "-" + issues["Village"]
            else:
                issues["Location"] = ""

            summary_scored = score_surveyors(summary)
            report_html = build_html_report(selected_project, "ATR-QA Department", summary_scored, issues)

            st.download_button(
                label="Download Surveyor Report (HTML)",
                data=report_html,
                file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)
