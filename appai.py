
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
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(layout="wide")

csv_url = st.secrets["CSV_URL_MAIN"]
csv_url_tools = st.secrets["CSV_URL_TOOLS"]
csv_url_users = st.secrets["CSV_URL_USERS"]

df = pd.read_csv(csv_url)
df_tools = pd.read_csv(csv_url_tools)
df_users = pd.read_csv(csv_url_users)


user_dict = df_users.set_index("users")[["password", "project"]].to_dict(orient="index")


def convert_df_to_csv(df):
    return df.to_csv(index=False, encoding='utf-8')

# Check if 'logged_in' exists in session_state, if not, initialize it
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# If not logged in, show login form
if not st.session_state.logged_in:
    placeholder = st.empty()
    with placeholder.form("login"):
        st.markdown("#### ATR Consulting - Data Collection/QA Progress Tracker")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        st.markdown("""
  <br><br>
  
  <div style="background-color:#f0f8ff; padding:20px; border-radius:10px; border-left:6px solid #3399ff;">
    <h3 style="color:#005c99; margin-bottom:10px;">📘 About This App</h3>
    <p style="color:#00334d; font-size:15px;">
      Welcome to our interactive Streamlit application! <br>
      This tool provides insightful features, real-time data collection, and user-friendly visualizations designed to help you <strong>track data collection</strong>, monitor <strong>QA progress</strong>, and generate clear, user-friendly <strong>data summaries</strong>.
    </p>
  </div>
  """, unsafe_allow_html=True)
  
    if submit:
        if username in user_dict and password == user_dict[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.username = username
            placeholder.empty()
            st.success("Login successful")
        else:
                  st.markdown("""
  <div style="background-color:#ffe6e6; padding:20px; border-left:6px solid #ff4d4d; border-radius:10px;">
    <h2 style="color:#cc0000; margin-bottom:10px;">🔒 Access Denied</h2>
    <p style="color:#4d0000; font-size:16px;">
      You've entered an <strong>empty</strong> or <strong>incorrect password</strong>. <br>
      Please double-check and try again to continue.
    </p>
  </div>
  """, unsafe_allow_html=True)

# If already logged in
if st.session_state.logged_in:
  # Streamlit app
  #st.markdown("**⚠️ The app is currently under maintenance. Some figures could be incorrect (in some projects).**")
  #st.title("QA and DC Progress Tracker")   
  st.markdown("""
      <style>
          .banner { background: #921111; border-radius: 16px; padding: 6px 28px; margin-bottom: 8px; }
          .banner h1 { color: #fff !important; font-size: 22px !important; font-weight: 700 !important; margin: 0 0 2px !important; letter-spacing: -0.3px; }
          .banner p { color: #A7F3D0; font-size: 12px; margin: 0; }
      </style>
      <div class="banner">
          <h1>Data Collection & QA Dashboard</h1>
          <p>ATR Consulting | Progress Tracker</p>
      </div>
  """, unsafe_allow_html=True)
  st.toast(
    "Press the 'R' key to refresh the page!\n"
    "The figures/numbers include both complete and incomplete data by default. "
    "Please check the 'Completion Status' option accordingly.")

  # Dropdown for project selection
  if user_dict[st.session_state.username]["project"].split(',')[0]=='All':
    main_project_names = df['Main Project'].unique()
  else:
    main_project_names = df[df['Main Project'].isin(user_dict[st.session_state.username]["project"].split(','))]['Main Project'].unique()


#########new
  
  cols1, cols2, cols3 = st.columns([1, 1, 1])  # Equal thirds
  with cols1:  # Center column
    st.markdown(f"<h2 style='color:#900C3F; font-size: 24px;'>Project:</h2>", unsafe_allow_html=True)
    main_project = st.selectbox("", main_project_names,key="selectbox_1")
  # Filter data based on selected project
  project_data = df[df['Main Project'] == main_project].reset_index()  
  project_names = df[df['Main Project']==main_project]['Project Name'].unique()

  # Display project name
  st.markdown(f"<h2 style='color:#900C3F; font-size: 22px;'>Project Timeline</h2>", unsafe_allow_html=True)
            
  # ---------------- CONFIG ----------------
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
  
  # Base colors
  PLANNED_COLOR = "rgba(88,101,242,0.9)"
  ACTUAL_COLOR  = "rgba(59,130,246,0.30)"
  RUNNING_COLOR = "rgba(59,130,246,0.45)"
  
  # Current phase accent
  CURRENT_PLANNED_COLOR = "rgba(0,144,118,1.0)"
  CURRENT_ACTUAL_COLOR  = "rgba(0,144,118,0.45)"
  
  # Status markers
  ONTIME_COLOR = "#22c55e"
  DELAY_COLOR  = "#ef4444"
  
  PLANNED_W = 3
  ACTUAL_W  = 10
  GAP = 1.1
  
  today = pd.Timestamp.today().normalize()
  
  # ---------------- HELPERS ----------------
  def to_dt(x):
      return pd.to_datetime(x, dayfirst=True, errors="coerce")
  
  def delay_days(plan_end, actual_end):
      if pd.notna(plan_end) and pd.notna(actual_end):
          d = (actual_end - plan_end).days
          return d if d > 0 else 0
      return 0
  
  # Parse required columns
  for _, ps, pe, a_s, a_e in PHASES:
      for c in (ps, pe, a_s, a_e):
          if c in project_data.columns:
              project_data[c] = to_dt(project_data[c])
  
  # ---------------- FIGURE ----------------
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
  
          # ---- Planned (dashed) ----
          planned_color = CURRENT_PLANNED_COLOR if is_current else PLANNED_COLOR
  
          fig.add_trace(go.Scatter(
              x=[ps, pe], y=[y, y],
              mode="lines",
              line=dict(color=planned_color, width=PLANNED_W, dash="dash"),
              showlegend=False,
              hovertemplate=f"<b>{project}</b><br>{phase}<br>"
                            f"Planned: {ps:%d-%b-%Y} → {pe:%d-%b-%Y}<extra></extra>",
          ))
  
          # ---- Actual (solid, transparent) ----
          if pd.notna(a_s):
              is_running = pd.isna(a_e)
              actual_end = a_e if pd.notna(a_e) else today
          
              actual_color = (
                  CURRENT_ACTUAL_COLOR if is_current
                  else ACTUAL_COLOR if not is_running
                  else RUNNING_COLOR
              )
          
              fig.add_trace(go.Scatter(
                  x=[a_s, actual_end], y=[y, y],
                  mode="lines",
                  line=dict(color=actual_color, width=ACTUAL_W),
                  showlegend=False,
                  hovertemplate=f"<b>{project}</b><br>{phase}<br>"
                                f"Actual: {a_s:%d-%b-%Y} → {actual_end:%d-%b-%Y}"
                                f"{' (running)' if is_running else ''}<extra></extra>",
              ))
          
              # ✅ Ongoing marker: ellipsis at the bar end
              if is_running:
                  fig.add_annotation(
                      x=actual_end, y=y,
                      text="<b>↝</b>",
                      showarrow=False,
                      xanchor="left",
                      yanchor="middle",
                      font=dict(
                          size=22,            # ⬅ bigger
                          color="#7f1d1d",     # ⬅ dark red (tailwind red-900)
                      ),
                      bgcolor="rgba(255,255,255,0.6)",  # optional readability
                  )
          
              # ---- Status markers (only if finished) ----
              if not is_running:
                  d = delay_days(pe, a_e)
                  if d > 0:
                      fig.add_trace(go.Scatter(
                          x=[a_e], y=[y],
                          mode="markers+text",
                          marker=dict(size=8, color=DELAY_COLOR),
                          text=[f"+{d}d"],
                          textposition="top center",
                          textfont=dict(size=9, color=DELAY_COLOR),
                          showlegend=False,
                      ))
                  else:
                      fig.add_annotation(
                          x=a_e, y=y,
                          text="<b>🗹</b>",
                          showarrow=False,
                          font=dict(size=18, color=ONTIME_COLOR),
                          xshift=8,        
                      )
          y += 1
  
      # ---- Project-level Responsible label (right side) ----
      if project_y and responsible:
          fig.add_annotation(
              xref="paper",
              x=0.9,
              xanchor="left",
              y=sum(project_y) / len(project_y),
              yanchor="middle",
              text=f"<span style='color:#7c3aed;font-size:12px;'>● Now with: <b>{row.get('Responsible')}</b></span>",
              showarrow=False,
          )
  
      y += GAP
  
  # ---------------- LEGEND (compact text) ----------------
  st.markdown(
      "<div style='font-size:12px;color:#555'>"
      "<b>— — —</b> Planned &nbsp;&nbsp;"
      "<b>▬</b> Actual &nbsp;&nbsp;"
      "<span style='color:#3b82f6'><b>↝</b></span> Ongoing &nbsp;&nbsp;"
      "<span style='color:#22c55e'><b>🗹</b></span> On time &nbsp;&nbsp;"
      "<span style='color:#ef4444'><b>●</b></span> Delayed"
      "</div>",
      unsafe_allow_html=True
  )
  
  # ---------------- AXES & LAYOUT ----------------
  fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.4)


    # Label on top of the line
  fig.add_annotation(
    x=today,              # align with the vertical line
    y=0.99,                   # top of plot frame
    xref="x",              # x in data coordinates
    yref="paper",          # y in plot frame coordinates
    text="<b><i>Today</i></b>",  # bold + italic
    showarrow=False,
    xanchor="center",
    yanchor="bottom",      # text sits below this y, so it doesn't go above
    font=dict(size=12, color="#0F5448")
)

  fig.update_yaxes(
      tickmode="array",
      tickvals=y_vals,
      ticktext=y_labels,
      autorange="reversed",
      title="",
  )

  max_date = max(project_data[pe_c].max() if pe_c in project_data.columns else pd.Timestamp.today()for _, _, pe_c, _, _ in PHASES)
  
  
  fig.update_xaxes(
      range=[project_data[[ps_c for _, ps_c, _, _, _ in PHASES if ps_c in project_data.columns]].min().min(),
           max_date + pd.Timedelta(days=20)],
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
  
  st.plotly_chart(fig, use_container_width=True)

#####  
  collll1, collll2, collll3 = st.columns([1, 1, 1])  # Equal thirds
  
  with collll1:  # Center column
    st.markdown(f"<h2 style='color:#900C3F; font-size: 22px;'>Round/Sub-Project</h2>", unsafe_allow_html=True)
    selected_project = st.selectbox("", project_names,key="selectbox_2")
    

  # Filter data based on selected project
  project_data = df[df['Project Name'] == selected_project].reset_index()
  
  QA_records_link=project_data['QA-Notes link'][0]
  proj_completed=project_data['Completed'][0]

  project_data_tools = df_tools[df_tools['Project Name'] == selected_project].reset_index()
  tool_col_map = project_data_tools.set_index('Tool')['main_cols'].to_dict()


  def compute_vid(row):
    cols_str = tool_col_map.get(row['Tool'], '')
    
    # normalize column names
    cols = [c.strip() for c in cols_str.split('-') if c.strip()]

    parts = []
    for col in cols:
        if col in row:
            parts.append(str(row[col]).removesuffix('.0'))
        else:
            parts.append("NA")  # prevents crash

    return f"{row['Tool']}/{'-'.join(parts)}"  

    
  # def compute_vid(row):
  #     cols_str = tool_col_map.get(row['Tool'], '')
  #     cols = cols_str.split('-')
  #     parts = [str(row[col]).removesuffix('.0') for col in cols]
  #     return f"{row['Tool']}/{'-'.join(parts)}"

  def_var = project_data['Summary_defualt_var'][0]
  if def_var.strip() == "-":
      def_var0 = []
      def_var1 = []
      def_var2 = []
  else:
      parts = def_var.split(";")
      def_var0 = [item.strip() for item in parts[0].split(",")] if len(parts) > 0 else []
      def_var1 = [item.strip() for item in parts[1].split(",")] if len(parts) > 1 else []
      def_var2 = [item.strip() for item in parts[2].split(",")] if len(parts) > 2 else []
 
  

  
  ###delete for testing
  
  def generate_stylish_horizontal_roadmap_html(steps, current_step_label):
      """
      Generates a stylish, horizontal "metro-style" roadmap visualization.
  
      This version dynamically assigns statuses ('completed', 'ongoing', 'upcoming')
      to each step based on the provided `current_step_label`.
  
      Args:
          steps (list): A list of dictionaries, where each dictionary
                        must have a 'label' key.
          current_step_label (str): The label of the step that is currently 'ongoing'.
      """
  
      # --- 1. Dynamically determine step statuses ---
      processed_steps = []
      try:
          # Find the index of the current step
          current_index = [s['label'] for s in steps].index(current_step_label)
      except ValueError:
          # If the current step label isn't found, default to -1 (all steps upcoming)
          current_index = -1
  
      for i, step in enumerate(steps):
          status = ""
          if current_index == -1:
              status = 'upcoming' # Handle case where step is not found
          elif i < current_index:
              status = 'completed'
          elif i == current_index:
              status = 'ongoing'
          else:
              status = 'upcoming'
          processed_steps.append({'label': step['label'], 'status': status})
  
  
      # --- 2. CSS Styling (no changes needed here) ---
      # Note: Using @media (prefers-color-scheme: light) for automatic theme detection.
      css_styles = """
      <style>
          @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
  
          @keyframes glow {
              0%, 100% {
                  box-shadow: 0 0 10px #2563eb, 0 0 20px #2563eb, 0 0 30px #2563eb;
              }
              50% {
                  box-shadow: 0 0 15px #3b82f6, 0 0 30px #3b82f6, 0 0 45px #3b82f6;
              }
          }
          
          @keyframes pulse-dot {
              0%, 100% { transform: scale(1); opacity: 1; }
              50% { transform: scale(1.6); opacity: 0.7; }
          }
  
          @keyframes flow-gradient {
              0% { background-position: 200% 0; }
              100% { background-position: -200% 0; }
          }
  
          /* --- Base Styles --- */
          body {
              font-family: 'Inter', sans-serif;
              background-color: transparent;
          }
          .step-node {
              transition: transform 0.3s ease;
          }
          .step-node:hover {
              transform: scale(1.05);
          }
  
          /* --- Dark Mode (Default) --- */
          .track-main { background-color: #334155; /* Slate-700 */ }
          .track-progress {
              background: linear-gradient(90deg, #14b8a6, #5eead4, #14b8a6);
              background-size: 200% 100%;
              animation: flow-gradient 3s linear infinite;
              transition: width 0.5s ease-in-out;
          }
          .progress-comet {
              position: absolute;
              top: 50%;
              transform: translateY(-50%);
              width: 12px;
              height: 12px;
              border-radius: 50%;
              background-color: #a7f3d0; /* Teal-200 */
              box-shadow: 0 0 10px #5eead4, 0 0 20px #5eead4, -20px 0 30px #14b8a6;
              transition: left 0.5s ease-in-out;
          }
          .node-ring-bg { background-color: #1e293b; /* Slate-800 */ }
          .text-completed { color: #5eead4; /* Teal-300 */ }
          .text-ongoing { color: #93c5fd; /* Blue-300 */ font-weight: 700; }
          .text-upcoming { color: #64748b; /* Slate-500 */ }
          .node-ongoing .node-ring {
              animation: glow 2.5s ease-in-out infinite;
          }
          .node-ongoing .pulsing-dot {
              animation: pulse-dot 2s ease-in-out infinite;
          }
  
          /* --- Light Mode Overrides --- */
          @media (prefers-color-scheme: light) {
              .track-main { background-color: #e2e8f0; /* Slate-200 */ }
              .track-progress {
                  background: linear-gradient(90deg, #0d9488, #2dd4bf, #0d9488);
                  background-size: 200% 100%;
                  animation: flow-gradient 3s linear infinite;
              }
              .progress-comet {
                  background-color: #5eead4; /* Teal-300 */
                  box-shadow: 0 0 10px #2dd4bf, 0 0 20px #2dd4bf, -20px 0 30px #0d9488;
              }
              .node-ring-bg { background-color: #f1f5f9; /* Slate-100 */ }
              .text-completed { color: #0d9488; /* Teal-600 */ }
              .text-ongoing { color: #2563eb; /* Blue-600 */ font-weight: 700; }
              .text-upcoming { color: #64748b; /* Slate-500 */ }
              .node-ongoing .node-ring {
                  animation: none;
                  box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
              }
              .node-ongoing .pulsing-dot {
                  animation: pulse-dot 2s ease-in-out infinite;
              }
          }
      </style>
      """
  
      # --- 3. HTML Generation ---
      # This part now uses the `processed_steps` list
      num_steps = len(processed_steps)
      completed_steps = sum(1 for s in processed_steps if s['status'] == 'completed')
      
      # Calculate progress percentage for the progress bar
      progress_percentage = (completed_steps / (num_steps - 1)) * 100 if num_steps > 1 else 0
      
      # Adjust width and position for aesthetics
      progress_width = f"calc({progress_percentage}% - {50 / (num_steps - 1)}%)" if num_steps > 1 else "0%"
      comet_position = f"calc({progress_percentage}% - {50 / (num_steps - 1)}% - 6px)" if num_steps > 1 else "-6px" # Adjust for half comet width
  
      html_content = f"""
      <head>
          <script src="https://cdn.tailwindcss.com"></script>
          {css_styles}
      </head>
      <body>
          <div class="w-full max-w-7xl mx-auto py-8 px-4">
              <div class="relative w-full">
                  <!-- The main track/line -->
                  <div class="track-main absolute top-1/2 -translate-y-1/2 w-full h-2 rounded-full"></div>
                  
                  <!-- Progress track -->
                  <div class="track-progress absolute top-1/2 -translate-y-1/2 h-2 rounded-full" style="width: {progress_width};"></div>
                  
                  <!-- Progress Comet -->
                  <div class="progress-comet" style="left: {comet_position};"></div>
  
                  <div class="relative flex justify-between items-start w-full">
      """
  
      # --- Loop through processed_steps to build the roadmap nodes ---
      for i, step in enumerate(processed_steps):
          status = step['status']
          label = step['label']
          
          # Determine styles based on the dynamically assigned status
          node_class, ring_color, icon_content, text_class = "", "", "", ""
          ring_size_class = "w-8 h-8"
  
          if status == 'completed':
              ring_color = "border-teal-500"
              icon_content = '<div class="w-3 h-3 bg-teal-500 rounded-full shadow-lg"></div>'
              text_class = "text-completed"
          elif status == 'ongoing':
              node_class = "node-ongoing"
              ring_color = "border-blue-500"
              icon_content = '<div class="pulsing-dot w-3 h-3 bg-blue-500 rounded-full"></div>'
              text_class = "text-ongoing"
              ring_size_class = "w-10 h-10" # Make the ring larger for the ongoing step
          else: # upcoming
              ring_color = "border-slate-600"
              icon_content = '<div class="w-3 h-3 bg-slate-600 rounded-full"></div>'
              text_class = "text-upcoming"
  
          # Add the step node HTML
          html_content += f"""
          <div class="step-node flex flex-col items-center text-center {node_class}" style="width: {100 / num_steps}%;">
              <div class="node-ring node-ring-bg {ring_size_class} rounded-full border-4 {ring_color} flex items-center justify-center z-10">
                  {icon_content}
              </div>
              <p class="mt-12 text-sm font-medium {text_class} w-28">
                  {label}
              </p>
          </div>
          """
  
      # --- Close the main containers ---
      html_content += """
                  </div>
              </div>
          </div>
      </body>
      """
      return html_content
    
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
  step_labels = [step['label'] for step in steps_data]
  
  # This is where you would get your actual current step from your data source
  # For this example, we use a selectbox to let the user control it.
  # project_data = {'current_step': ['Automated Data Checks']} # Your original idea
  # current_step = project_data['current_step'][0]
  
  
  current_step = project_data['current_step'][0]
  
  # Generate the HTML for the roadmap with the selected step
  roadmap_html = generate_stylish_horizontal_roadmap_html(steps_data, current_step)
  
  # Display the roadmap in Streamlit
  st.components.v1.html(roadmap_html, height=180)

  ###########33
  st.markdown(f"<h2 style='color:#900C3F; font-size: 22px;'>Project links</h2>", unsafe_allow_html=True)
  
  # Get first row of links
  links_row = project_data[['Tool link', 'XLSForm link', 'QA-Notes link', 'Tracker link', 'DC Tracker', 'Document folder link']].iloc[0]
  
  # Friendly labels with icons
  link_labels = {
      'Tool link': '🛠 Tool',
      'XLSForm link': '📄 XLSForm',
      'QA-Notes link': '📊 QA-Notes link',
      'Tracker link': '📈 QA Tracker',
      'DC Tracker': '📈 DC Tracker',
      'Document folder link': '📁 Docs'
  }
  
  # Create 7 columns
  cols = st.columns(6)
  
  # Render each box
  for i, (col_name, label) in enumerate(link_labels.items()):
      value = links_row[col_name]
      with cols[i]:
          if pd.notna(value) and value.strip():
              st.markdown(
                            f"""
                            <div style="
                                padding: 12px;
                                border-radius: 12px;
                                border: 1px solid #e2e8f0;
                                background-color: rgba(255, 255, 255, 0.05);
                                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                                text-align: center;
                                font-size: 14px;
                                transition: all 0.3s ease;
                            ">
                                <div style="margin-bottom: 6px; font-weight: 600; color: #94a3b8;">{label}</div>
                                <a href="{value}" target="_blank" style="
                                    color: #0ea5e9;
                                    text-decoration: none;
                                    font-weight: 500;
                                ">🔗 Open</a>
                            </div>
                            """, unsafe_allow_html=True
                        )
          else:
              st.markdown(
                  f"""
                  <div style="
                      padding: 12px;
                      border-radius: 12px;
                      border: 1px dashed #cbd5e1;
                      background-color: rgba(255, 255, 255, 0.03);
                      text-align: center;
                      font-size: 14px;
                      color: #94a3b8;
                  ">
                      <div style="margin-bottom: 6px; font-weight: 600;">{label}</div>
                      <span style="font-style: italic;">N/A</span>
                  </div>
                  """, unsafe_allow_html=True
              )

      
  if proj_completed=="Yes":
    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds vertical space
    st.markdown("""
              <div style="background-color:#f0f4f8; border-left:6px solid #1f77b4; padding: 20px; border-radius: 10px;">
                <h3 style="color:#1f77b4; margin-top:0;">📁 Project Archived</h3>
                <p style="font-size:16px; color:#333;">
                  This project has been <strong>archived</strong>. For complete information on <em>sampling</em> and <em>site visits</em>, please refer to the <strong>Document</strong> field. 
                  Relevant <strong>datasets</strong> and <strong>trackers</strong> are also available for your reference.
                </p>
              </div>
              """, unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)  # Adds vertical space
  else:
    st.markdown(f"<h2 style='color:#900C3F; font-size: 22px;'>Data Metrics</h2>", unsafe_allow_html=True)
    #Tool specific
    tool_names = project_data_tools['Tool'].unique()
    # Create two columns
    coll1, coll2, coll3 = st.columns(3)
    
    # Place each multiselect inside a different column
    with coll1:
        selected_tool = st.multiselect(
            'Tool', 
            tool_names, 
            default=None  # or tool_names[0] if desired
        )
    
    
    
    missing = pd.DataFrame(columns=['Tool','V_ID','KEY','Type','QA_Status'])
    rawsheet=project_data['raw_sheet'][0]
    Project_QA_ID=project_data['Sampling_ID'][0]
    Project_QA_ID2=project_data['QAlog_ID'][0]
    Project_QA_ID3=project_data['HFC_ID'][0]
    raw_sheet_id=rawsheet.split('/d/')[1].split('/')[0]
    csv_url = f"https://docs.google.com/spreadsheets/d/{raw_sheet_id}/export?format=csv&id={raw_sheet_id}&gid=0"
    t = pd.read_csv(csv_url)
    
    # if st.session_state.username=='admin':
    #     st.dataframe(t)

    t['KEY_Unique']=t['KEY']
    qasheet = "https://docs.google.com/spreadsheets/d/1V1SfBZUwHN0NtXFIoiXEh7JGkpTUOLZnGAfFN8QVXYQ/export?format=csv&"+Project_QA_ID2
    qalog = pd.read_csv(qasheet)
    
    t=pd.merge(t,qalog[['QA_Status','KEY_Unique']].drop_duplicates('KEY_Unique'),on='KEY_Unique',how='left')
    t['QA_Status']=t['QA_Status'].replace('',"Not QA'ed Yet")
    t['QA_Status']=t['QA_Status'].fillna("Not QA'ed Yet")
    
    
    extra_code=project_data['extra_code'][0]
    Add_cols=project_data_tools['Add_columns'][0]
    t['Completion_status']='Complete'
    if extra_code !='-':
        exec(extra_code)
    
    t = t.sort_values(by=['QA_Status', 'Completion_status'], ascending=True)

        
    t['occurance'] = None  # create empty column

    for tool, cols in tool_col_map.items():
        # Split "Site_Visit_ID-Interview_Type_SV" → ['Site_Visit_ID', 'Interview_Type_SV']
        group_cols = [c for c in cols.split('-') if c != 'occurance']
        
        mask = t['Tool'] == tool
        t.loc[mask, 'occurance'] = (
            t.loc[mask].groupby(group_cols).cumcount() + 1
        )
    
    t['occurance'] = t['occurance'].fillna(9999).astype(int)
    #st.dataframe(t)
    t['V_ID'] = t.apply(compute_vid, axis=1)

    
    samplingsheet = "https://docs.google.com/spreadsheets/d/1U0Y7TQnTFEg1edMb0IHejOxv9S2YLY2UH-tp1qzXyBg/export?format=csv&"+Project_QA_ID
    tari= pd.read_csv(samplingsheet)
    tari['V_ID']=tari['Tool']+"/"+tari['V_ID']
    tari=tari[tari['Skipped']!="Yes"]
    tari = tari[(tari["Tool"].isin(t["Tool"].unique()))&(tari["Tool"].isin(project_data_tools["Tool"]))] ##### new changes
    df_free=t[t["Tool"].isin(project_data_tools["Tool"]) & ~t["Tool"].isin(tari["Tool"])].copy()
    df_free = df_free.drop(columns=["KEY", "QA_Status"], errors='ignore')
    df_free = df_free[tari.columns.intersection(df_free.columns)]
    tari = pd.concat([tari, df_free], ignore_index=True)
    

    if selected_tool:
      t=t[t.Tool.isin(selected_tool)]
      tari=tari[tari.Tool.isin(selected_tool)]
    
    
    
    

    
    with coll2:
        qastatus = st.multiselect(
            'QA Status:', 
            t.QA_Status.unique().tolist(),
            default=[x for x in t.QA_Status.unique().tolist() if x != 'Rejected_paused']
        )
    with coll3:
        status_options = ['Complete', 'Incomplete']
        completion = st.multiselect(
            'Completion Status:',
            options=status_options,
            default=['Complete', 'Incomplete']
        )
    t=t[(t.QA_Status.isin(qastatus))&(t.Completion_status.isin(completion))].copy()
    tari = tari.merge(t[['V_ID'] + [c for c in t.columns if c not in tari.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left')
    t = t.merge(tari[['V_ID'] + [c for c in tari.columns if c not in t.columns and c != 'V_ID']].drop_duplicates('V_ID'), on='V_ID', how='left') #to remvoe it misseed up

    if list(tool_col_map.values())[0].rsplit('-', 1)[-1] == 'occurance':
        tall2 = t[t["V_ID"].str.startswith(tuple(tari["V_ID"].str.rsplit("-", n=1).str[0].unique()), na=False)]

    
    tall=t[(t.V_ID.isin(tari.V_ID))].copy()  #tall=t[(t.KEY_Unique.isin(tari.KEY))].copy()
    #tari=tari[(tari.KEY.isin(tall.KEY_Unique))|(tari.KEY.isna())]
    
    tall['d1']=pd.to_datetime(tall['SubmissionDate'],format='%b %d, %Y %H:%M:%S' , errors='coerce').dt.date #format='%d-%m-%y %H:%M'
    tall['d2']=pd.to_datetime(tall['SubmissionDate'], format='%Y-%m-%dT%H:%M:%S.%fZ',errors='coerce').dt.date
    tall['Date'] = tall.d1.fillna(tall.d2)
    tall['Date'] = pd.to_datetime(tall['Date'])
    
    # Convert to string with only date
    tall['Date'] = tall['Date'].dt.strftime('%Y-%m-%d')


      
    tall = tall.drop(columns=['SubmissionDate','occurance', 'd1', 'd2'])#, 'Tool'
       
    # Count occurrences of each date
    dff = tall['Date'].value_counts().reset_index()
    dff.columns = ['Date', 'N']
    
    # Sort the dates in ascending order
    dff = dff.sort_values(by='Date', ascending=False)
    
    
    # Create a line plot using Plotly
    fig = px.line(dff, x='Date', y='N', title='Timeline of Data')
    
    # Add circle markers to the line plot
    fig.update_traces(mode='lines+markers', marker=dict(color='#AD1515', size=10))
    
    # Customize the layout: set height and remove title
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='N',
        template='plotly_dark',  # Use a fancy template
        height=300  # Set plot height to a smaller size
    )


#######3
    
    # -----------------------------
    # Cache ONLY raw geojson
    # -----------------------------
    @st.cache_data(show_spinner=False)
    def load_geojson(path: str):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # -----------------------------
    # Build folium map (NO caching)
    # -----------------------------
    def build_map(geo_raw, counts_df):
        geo = copy.deepcopy(geo_raw)  # prevent cached mutation
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
    
    # -----------------------------
    # Data prep
    # -----------------------------
    counts = t.groupby("Province").size().reset_index(name="count")
    counts["Province"] = counts["Province"].astype(str).str.strip()
  
    counts = counts[["Province", "count"]]
    
    # -----------------------------
    # Render
    # -----------------------------
    geo_raw = load_geojson("afghanistan_provinces.geojson")
    m = build_map(geo_raw, counts)
    
    colii1, colii2 = st.columns(2)
    
    with colii1:
        st_folium(
            m,
            height=300,
            use_container_width=True,
            returned_objects=[],
            key="afg_map",
        )
    
    with colii2:
        st.plotly_chart(fig, use_container_width=True)

    
########    
    st.markdown(f"<h2 style='color:#900C3F; font-size: 22px;'>Sample Tracking</h2>", unsafe_allow_html=True)
    # Grouped counts
    target = tari.groupby('Tool').size()
    received = tari[tari.QA_Status.notna()].groupby('Tool').size()#tari[tari.Completion_status=='Complete'].groupby('Tool').size()
    approved = tari[tari.QA_Status == 'Approved'].groupby('Tool').size()
    rejected = tari[tari.QA_Status == 'Rejected'].groupby('Tool').size()
    awaiting = tari[tari.QA_Status.isin(["Not QA'ed Yet", 'Pending'])].groupby('Tool').size()
    
    # Combine into one DataFrame
    data_metrics = pd.DataFrame({
        'Target': target,
        'Received data': received,
        'Approved data': approved,
        'Rejected data': rejected,
        'Awaiting review': awaiting
    }).fillna(0).astype(int).reset_index()
    
    if len(data_metrics) > 1:
        data_metrics.loc['Total'] = data_metrics.sum(numeric_only=True)
        data_metrics.loc['Total', 'Tool'] = 'All Tools'
    #st.data_editor(data_metrics, use_container_width=True)
    # Convert True/False to checkmark/X
    data_metrics['DC Completion %'] = ((data_metrics['Received data'] / data_metrics['Target']) * 100).round(2)
    
    data_metrics['Completed ✅'] = data_metrics['Target'] == data_metrics['Approved data']
    data_metrics['Completed ✅'] = data_metrics['Completed ✅'].apply(lambda x: '✅' if x else '❌')
    # Show it in Streamlit
    st.dataframe(data_metrics,hide_index=True)
    
    # Create data for the first doughnut chart
    labels1 = ['Received', 'Remaining']
    values1 = [tari[tari.QA_Status.isin(qastatus)].shape[0], max(0,tari.shape[0]-tari[tari.QA_Status.isin(qastatus)].shape[0])]
    
    # Create data for the second doughnut chart
    g=tari[tari.QA_Status.isin(qastatus)].QA_Status.value_counts().reset_index()
    labels2 = g['QA_Status'].tolist()
    values2 = g['count'].tolist()
    
    def make_donut(labels, values, title, colors, note=""):
        pct = round(100 * values[0] / sum(values))
        fig = go.Figure(go.Pie(
            labels=labels, values=values, hole=0.75,
            textinfo="percent", textfont=dict(size=12, color="#6B7280"),
            marker=dict(colors=colors, line=dict(color="#fff", width=3)),
            pull=[0.05] + [0] * (len(values) - 1),
            hovertemplate="<b>%{label}</b>: %{percent}<extra></extra>",
            showlegend=True, sort=False,
        ))
        fig.update_layout(
            title=dict(text=title, x=0.5, xanchor="center", font=dict(size=14, color="#1F2937")),
            height=260, margin=dict(l=0, r=0, t=45, b=0),
            template="plotly_white", paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=-0.08, x=0.5, xanchor="center", font=dict(size=12, color="#6B7280")),
            annotations=[dict(
                text=f"<b style='font-size:22px;color:#1F2937'>{pct}%</b><br><span style='font-size:11px;color:#9CA3AF'>{note}</span>",
                x=0.5, y=0.5, showarrow=False,
            )]
        )
        return fig
    
    
    
    
    # Create the first doughnut chart
    fig1 = make_donut(labels1, values1, "Data Collection Progress", ["#058789", "#BED6D6"], "Collected")
    
    # Create the second doughnut chart
    fig2 = make_donut(labels2, values2, "Data QA Progress",["#58AC38", "#970303", "#EE8D01", "#D1D5DB"][:len(g)], "QA'ed")

    
    
      
  
    # Create the layout dynamically
    cols = st.columns(2)
    
    # Display charts in the first two columns
    with cols[0]:
        st.plotly_chart(fig1, use_container_width=True)
    
    with cols[1]:
        st.plotly_chart(fig2, use_container_width=True)
    
      
      
    
    
    t=t[t['QA_Status'].isin(qastatus)]
    m=tari[~tari.V_ID.isin(t.V_ID)]
    m['Type']='Missing Data'
    ext=t[(~t.V_ID.isin(tari.V_ID))&(t.QA_Status=='Approved')][['Tool', 'V_ID', 'KEY', 'QA_Status']]
    ext['Type']='Extra data'
    dup=t[t.V_ID.duplicated(keep='first')][['Tool', 'V_ID', 'KEY','QA_Status']]
    dup['Type']='Duplicate Data'
    missing=pd.concat([missing,m])
    missing=pd.concat([missing,ext])
    missing=pd.concat([missing,dup])


    if "Call Status" in tall.columns:
        try:
            tall2
        except NameError:
            tall2 = tall
        
    tall = tall[~tall.KEY.isin(pd.concat([ext.KEY, dup.KEY]))]
    
    col1, col2 = st.columns(2)
        
        
    with col1:
        tari_csv = convert_df_to_csv(tari)
        st.download_button(
            label="Download Target Data Details",
            data=tari_csv,
            file_name='Sample_Tracking.csv',
            mime='text/csv'
        )
    
    # with col2:
    #     missing_csv = convert_df_to_csv(missing)
    #     st.download_button(
    #         label="Download Missing Data",
    #         data=missing_csv,
    #         file_name='missing.csv',
    #         mime='text/csv'
    #     )
        
    
    
    
    ###added on 27Aug
    j= project_data['notes'][0]
    if j!="-":
      #st.markdown("<h2 style='color:#FF5733; font-size: 24px;'>Key Insights:</h2>",unsafe_allow_html=True)
      st.markdown(eval(j[1:-1]), unsafe_allow_html=True)
    

    ################
    st.markdown(f"<h2 style='color:#900C3F; font-size: 24px;'>Summary Generation</h2>", unsafe_allow_html=True)
    st.info(
        'Please note: summaries include both "Complete" and "Incomplete" submissions by default; '
        'for accurate sample tracking and analysis, select only "Complete" submissions in the filters above.'
    )    


    
    disag = st.multiselect('Create Dataset Summary:', tall.columns.tolist(), default=def_var1,
                           help='This option is used to create summaries based on selected columns.!')  # ,default=['Date')
    if disag:
      st.markdown(f"<h2 style='color:#000000; font-size: 16px;'>Summary:</h2>", unsafe_allow_html=True)
      if len(disag) == 1:
        disag_t = tall.groupby(disag).size().reset_index().rename(columns={0: 'N'})
        disag_t.loc[len(disag_t)] = ['Total', disag_t['N'].sum()]
      else:
        disag_t = tall.groupby(disag).size().unstack(disag[-1], fill_value=0).reset_index()
        disag_t.loc['Total'] = disag_t.sum(numeric_only=True)
      st.dataframe(disag_t)
  
    disag2 = st.multiselect('Create Sample Summary:', tari.columns.tolist(), def_var0,
                            help='This option is used to create summaries based on selected columns.!')  # ,default=['Date')
    if disag2:
      st.markdown(f"<h2 style='color:#000000; font-size: 16px;'>DC Progress Summary:</h2>", unsafe_allow_html=True)
      total_target = tari.groupby(disag2).size()
      received_data = tari[tari['QA_Status'].isin(qastatus)].groupby(disag2).size()
      summary = pd.DataFrame({'Total_Target': total_target, 'Received_Data': received_data}).fillna(0).astype(int)
      summary['Remaining'] = summary['Total_Target'] - summary['Received_Data']
      summary['Completed ✅'] = summary['Received_Data'] == summary['Total_Target']
      summary['Completed ✅'] = summary['Completed ✅'].apply(lambda x: '✅' if x else '❌')
      gb = GridOptionsBuilder.from_dataframe(summary)
      gb.configure_default_column(filterable=True)  # enables filter on every column
      gb.configure_grid_options(domLayout='normal')
      grid_options = gb.build()
      AgGrid(summary, gridOptions=grid_options, height=400, fit_columns_on_grid_load=True)
  


    if 'tall2' in locals():
        disag_raw=st.multiselect('Tryouts Summary (Phone Surveys):', tall2.columns.tolist(),def_var2,help='This is intended for phone surveys and other surveys where multiple attempts to reach respondents may be necessary.!')#,default=['Date')
        if disag_raw:
            st.markdown(f"<h2 style='color:#000000; font-size: 16px;'>Raw Data (Tryouts):</h2>", unsafe_allow_html=True)
            if len(disag_raw) == 1:
                disag_traw=tall2.groupby(disag_raw).size().reset_index().rename(columns={0:'N'})
                disag_traw.loc[len(disag_traw)] = ['Total', disag_traw['N'].sum()]
            else:
                disag_traw = tall2.groupby(disag_raw).size().unstack(disag_raw[-1],fill_value=0).reset_index()
                disag_traw.loc['Total'] = disag_traw.sum(numeric_only=True)
            st.dataframe(disag_traw)


    

     
  def parse_log(log_text: str):
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
  
  # group by date
  by_day = {}
  for d, msg in rows:
      by_day.setdefault(d, []).append(msg)
  
  dates = list(by_day.keys())
  total = sum(len(v) for v in by_day.values())
  start, end = (min(dates), max(dates)) if dates else (None, None)
  
  header = f"Project updates · {total} update{'s' if total != 1 else ''}"
  if start:
      header += f" · {start.strftime('%d %b %Y')} → {end.strftime('%d %b %Y')}"
  
  with st.expander(header, expanded=False):
      st.markdown("""
      <style>
        .upd-day {margin: 10px 0 14px 0; padding-left: 14px; border-left: 3px solid #e8eef7;}
        .upd-date {font-weight: 700; margin-bottom: 6px; color: #7a1f1f;} /* dark red */
        .upd-item {margin: 4px 0; color: #0f172a;}
        .upd-dot {color: #94a3b8; margin-right: 8px;}
        .upd-sep {height: 1px; background: #eef2f7; margin: 12px 0;}
      </style>
      """, unsafe_allow_html=True)
  
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
              unsafe_allow_html=True
          )
  



####################### surveyor analysis

  sr = st.button("Generate Surveyor Performance Report", key="create_report_btn")
  
  if sr:
      qalog2 = pd.merge(
          tall,
          qalog[['Issue_Type','Issue_Description','surveyor_notified','surveyor_response','issue_resolved','KEY_Unique']],
          on='KEY_Unique',
          how='left'
      )
  
      qalog2['severity'] = qalog2['QA_Status'].map({'Rejected':'High','Approved':'Low','Pending':'Medium'})
  
      issues = qalog2[['Site_Visit_ID','Province','Village','severity','QA_Status','Surveyor_Name','KEY','Issue_Type',
                       'Issue_Description','surveyor_notified','surveyor_response','issue_resolved']].copy()
  
      summary = (
          qalog2.groupby('Surveyor_Name')
          .agg(
              total_submissions=('Surveyor_Name','size'),
              rejected_count=('QA_Status', lambda x: (x=='Rejected').sum()),
              total_feedback_ratio=('Issue_Type', lambda x: x.notna().mean())
          )
          .assign(rejection_ratio=lambda d: d.rejected_count / d.total_submissions)
          .reset_index()
      )
      hfcsheet = "https://docs.google.com/spreadsheets/d/16EWCV7HTEx729ILvsYa72LkJ1P1Sw7Fo2R0FzXs3GvE/export?format=csv&"+Project_QA_ID3
      hfc= pd.read_csv(hfcsheet)
      hfc=hfc.drop_duplicates(subset='Surveyor_Name')
      summary=pd.merge(summary,hfc,on='Surveyor_Name',how='left').fillna(0)
      #st.dataframe(summary)

  
      issues = issues[issues.Issue_Type.notna()].copy()
      issues["issue_resolved"] = issues["issue_resolved"].fillna("No").replace("", "No")
      issues["Issue_Description"] = issues["Issue_Description"].fillna("")
      issues["surveyor_response"] = issues["surveyor_response"].fillna("")
      issues["Province"] = issues["Province"].fillna("")
      issues["Village"] = issues["Village"].fillna("")
      issues["Site_Visit_ID"] = issues["Site_Visit_ID"].fillna("")
      issues["Surveyor_Name"] = issues["Surveyor_Name"].fillna("")
      issues["Issue_Type"] = issues["Issue_Type"].fillna("")
      issues["KEY"] = issues["KEY"].fillna("")
      issues['Location'] = issues['Province'] + "-" + issues['Village']
  
      # ---------------------------------------
      # SCORING (your logic)
      # ---------------------------------------
      def score_surveyors(df: pd.DataFrame, w_rej=0.5, w_out=0.10, w_out2=0.2, w_fb=0.2) -> pd.DataFrame:
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
          df["band_color"] = np.select(
              conds, ["#10b981", "#3b82f6", "#f59e0b"], default="#ef4444"
          )
          df["recommendation"] = np.select(
              conds,
              ["Maintain monitoring", "Minor coaching", "Verify records"],
              default="Urgent Retraining",
          )
          return df
  
      # ---------------------------------------
      # REPORT BUILDER (Matrix + Detailed Log)
      # ---------------------------------------
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
          #st.dataframe(issues_df)
          not_notified_count = int(issues_df["surveyor_response"].fillna("").eq("").sum())
          high_severity = int((issues_df.get("severity") == "High").sum()) if total_issues else 0
          avg_score = float(summary_df["score"].mean()) if len(summary_df) else 0.0
  
          # Worst 10 (lowest score)
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
  
    /* ✅ ticker row divider for the detailed log */
    .ticker tbody tr{{border-bottom:1px dashed #e5e7eb}}
    .ticker tbody tr:last-child{{border-bottom:none}}
    .ticker tbody tr td{{padding-top:18px;padding-bottom:18px}}
  
    /* ---- Comment blocks (shared) ---- */
    .comment {{ margin-top:8px; padding:10px 12px; border-radius:12px; border:1px solid; }}
    .comment-date {{ font-weight:900; font-size:12px; letter-spacing:.02em; }}
    .comment-body {{ margin-top:4px; line-height:1.35; }}
    .comment-divider {{
      height:1px; margin:10px 2px;
      background: linear-gradient(90deg, rgba(148,163,184,0), rgba(148,163,184,0.85), rgba(148,163,184,0));
    }}
  
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
  
      <!-- ✅ Matrix (Worst 10) -->
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
  
      <!-- ✅ Detailed Log -->
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
  
    // ✅ Fast parser for "[d/m/yyyy]: comment ..." blocks
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
              
              <!-- Blank line / spacing -->
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
                ${{ i.surveyor_response? formatComments(i.surveyor_response): '<div class="awaiting-response">Awaiting response from DC/field...</div>'}}
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
  
      # ---------------------------------------
      # STREAMLIT USAGE
      # ---------------------------------------
      p_name = selected_project
      m_text = "ATR-QA Department"
  
      summary_scored = score_surveyors(summary, w_rej=0.35, w_out=0.1, w_out2=0.2, w_fb=0.35)
      report_html = build_html_report(p_name, m_text, summary_scored, issues)
  
      st.download_button(
          label="Download Surveyor Report (HTML)",
          data=report_html,
          file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html",
          mime="text/html",
          use_container_width=True,
          type="primary",
          key="download_report_btn",
      )
  
      # Optional preview:
      # st.components.v1.html(report_html, height=1200, scrolling=True)



##############################3
    
  # Add some styling (optional)
  st.markdown("""
  <style>
      .main {
          background-color: #FFFFFF;
      }
      h1, h2, h3 {
          color: #900C3F;
      }
      h2 {
          color: #1E90FF;
          font-size: 24px; /* Adjusted font size for all section headings */
      }
      .stDataFrame {
          background-color: #FFFFFF;
          border: 1px solid #C0C0C0;
          border-radius: 5px;
          box-shadow: 2px 2px 12px #aaaaaa;
      }
      table {
          width: 100%;
          border-collapse: collapse;
      }
      th, td {
          padding: 8px;
          text-align: left;
          border-bottom: 1px solid #ddd;
      }
      th {
          font-weight: bold;
          color: black; /* Make all headers bold and black */
      }
      a {
          color: #1E90FF;
          text-decoration: none;
      }
      a:hover {
          text-decoration: underline;
      }
  </style>
  """, unsafe_allow_html=True)
  if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
