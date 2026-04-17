"""
ATR Consulting — Data Collection & QA Dashboard
Professional data platform for project tracking, QA workflows, and reporting.
"""
import streamlit as st
import folium
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import streamlit.components.v1 as components
from streamlit_folium import st_folium
import copy
import re
import numpy as np

# ══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════════
st.set_page_config(
    layout="wide",
    page_title="ATR · Data Collection & QA",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════
#  DESIGN SYSTEM  (CSS)
# ══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
  /* Surfaces */
  --bg:            #f8fafc;
  --bg-alt:        #f1f5f9;
  --surface:       #ffffff;
  --surface-soft:  rgba(255,255,255,0.72);
  --glass:         rgba(255,255,255,0.60);
  --glass-border:  rgba(226,232,240,0.85);
  --border:        #e2e8f0;
  --border-soft:   #eef2f7;

  /* Text */
  --text:          #0f172a;
  --text-muted:    #64748b;
  --text-soft:     #94a3b8;

  /* Brand */
  --brand-50:      #f0fdfa;
  --brand-100:     #ccfbf1;
  --brand-400:     #2dd4bf;
  --brand-500:     #14b8a6;
  --brand-600:     #0d9488;
  --brand-700:     #0f766e;
  --brand-800:     #115e59;
  --brand-900:     #134e4a;

  /* Semantic */
  --success:       #10b981;
  --success-soft:  #d1fae5;
  --warning:       #f59e0b;
  --warning-soft:  #fef3c7;
  --danger:        #ef4444;
  --danger-soft:   #fee2e2;
  --info:          #3b82f6;
  --info-soft:     #dbeafe;

  /* Radii & shadows */
  --radius-sm:     10px;
  --radius:        14px;
  --radius-lg:     18px;
  --radius-xl:     22px;
  --shadow-xs:     0 1px 2px rgba(15,23,42,0.04);
  --shadow-sm:     0 1px 3px rgba(15,23,42,0.06), 0 1px 2px rgba(15,23,42,0.03);
  --shadow:        0 2px 6px rgba(15,23,42,0.05), 0 4px 14px rgba(15,23,42,0.05);
  --shadow-lg:     0 8px 28px rgba(15,23,42,0.10);
  --shadow-xl:     0 14px 40px rgba(15,23,42,0.14);

  /* Gradients */
  --g-brand:       linear-gradient(135deg, #0f172a 0%, #1e3a5f 45%, #0f766e 100%);
  --g-brand-soft:  linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
  --g-success:     linear-gradient(135deg, #10b981 0%, #34d399 100%);
  --g-warning:     linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%);
  --g-danger:      linear-gradient(135deg, #ef4444 0%, #f87171 100%);
}

/* ── Global ── */
html, body, [class*="css"] { font-family: 'Outfit', system-ui, sans-serif !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.2rem !important; padding-bottom: 2rem !important; max-width: 1400px; }

/* Kill stock Streamlit backgrounds on bordered blocks */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stHorizontalBlock"],
div[data-testid="stMetric"],
.stDataFrame { background: transparent !important; }

/* Bordered containers → glass cards */
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div[data-testid="stVerticalBlock"]) {
  background: var(--surface-soft) !important;
  backdrop-filter: blur(10px) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-xs);
}

/* ══════════════ SIDEBAR ══════════════ */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

.sb-brand {
  display: flex; align-items: center; gap: 12px;
  padding: 14px 8px 18px; border-bottom: 1px solid var(--border-soft);
  margin-bottom: 14px;
}
.sb-brand .logo {
  width: 40px; height: 40px; border-radius: 12px;
  background: var(--g-brand); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 800;
  box-shadow: 0 4px 14px rgba(15,118,110,0.25);
}
.sb-brand .title { font-size: 15px; font-weight: 800; color: var(--text); letter-spacing: -0.2px; }
.sb-brand .subtitle { font-size: 11px; color: var(--text-muted); font-weight: 500; }

.sb-user {
  background: linear-gradient(135deg, var(--brand-50), #fff);
  border: 1px solid var(--brand-100);
  border-radius: var(--radius);
  padding: 14px; display: flex; align-items: center; gap: 12px;
  margin-bottom: 14px;
}
.sb-user .avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--g-brand-soft); color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 800; font-size: 15px; text-transform: uppercase;
  box-shadow: 0 2px 8px rgba(15,118,110,0.30);
}
.sb-user .info .name { font-size: 13px; font-weight: 700; color: var(--text); line-height: 1.1; }
.sb-user .info .role {
  font-size: 10px; color: var(--brand-700); font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px;
}

.sb-section-label {
  font-size: 10px; font-weight: 700; color: var(--text-soft);
  text-transform: uppercase; letter-spacing: 0.1em;
  margin: 18px 0 8px; padding: 0 4px;
}

.sb-stat {
  background: var(--surface); border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm); padding: 10px 12px;
  margin-bottom: 6px; display: flex; align-items: center; justify-content: space-between;
}
.sb-stat .lbl { font-size: 11px; color: var(--text-muted); font-weight: 600; }
.sb-stat .val { font-size: 14px; color: var(--text); font-weight: 800; font-family: 'JetBrains Mono', monospace; }
.sb-stat .val.ok { color: var(--success); }
.sb-stat .val.warn { color: var(--warning); }
.sb-stat .val.bad { color: var(--danger); }

.sb-footer {
  margin-top: 18px; padding-top: 14px; border-top: 1px solid var(--border-soft);
  font-size: 10px; color: var(--text-soft); text-align: center; line-height: 1.5;
}

/* ══════════════ HERO ══════════════ */
.hero {
  background: var(--g-brand);
  border-radius: var(--radius-xl);
  padding: 28px 36px;
  margin-bottom: 20px;
  position: relative; overflow: hidden;
  box-shadow: 0 10px 34px rgba(15,23,42,0.22);
  display: flex; justify-content: space-between; align-items: center; gap: 24px;
}
.hero::before {
  content: ''; position: absolute; top: -55%; right: -6%;
  width: 380px; height: 380px;
  background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
  border-radius: 50%;
}
.hero::after {
  content: ''; position: absolute; bottom: -45%; left: 12%;
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(20,184,166,0.14) 0%, transparent 70%);
  border-radius: 50%;
}
.hero-text { position: relative; z-index: 1; }
.hero-eyebrow {
  display: inline-block;
  font-size: 10px; font-weight: 700; letter-spacing: 0.18em;
  color: rgba(255,255,255,0.55); text-transform: uppercase;
  padding: 4px 10px; border-radius: 999px;
  background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.08);
  margin-bottom: 12px;
}
.hero h1 {
  color: #fff; font-size: 30px; font-weight: 800;
  margin: 0; letter-spacing: -0.6px; line-height: 1.1;
}
.hero-sub {
  color: rgba(255,255,255,0.62); font-size: 13px;
  font-weight: 400; margin-top: 6px;
}
.hero-meta {
  display: flex; flex-direction: column; gap: 10px;
  align-items: flex-end; position: relative; z-index: 1;
}
.hero-badge {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,0.10); backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.14);
  color: #fff; padding: 10px 16px; border-radius: 999px;
  font-size: 13px; font-weight: 600;
}
.hero-badge .dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #34d399; box-shadow: 0 0 0 4px rgba(52,211,153,0.25);
  animation: pulse-dot 2s ease infinite;
}
.hero-time {
  color: rgba(255,255,255,0.55); font-size: 11px;
  font-family: 'JetBrains Mono', monospace; letter-spacing: 0.02em;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%      { opacity: 0.5; transform: scale(1.4); }
}

/* ══════════════ ALERT RIBBON ══════════════ */
.alert-ribbon {
  background: linear-gradient(90deg, rgba(254,243,199,0.9) 0%, rgba(254,249,195,0.7) 100%);
  border: 1px solid #fcd34d; border-left: 4px solid #f59e0b;
  border-radius: var(--radius); padding: 12px 18px; margin-bottom: 20px;
  display: flex; gap: 14px; align-items: center;
  box-shadow: var(--shadow-xs);
}
.alert-ribbon.crit {
  background: linear-gradient(90deg, rgba(254,226,226,0.9) 0%, rgba(254,242,242,0.7) 100%);
  border-color: #fca5a5; border-left-color: #dc2626;
}
.alert-ribbon .icon { font-size: 20px; flex-shrink: 0; }
.alert-ribbon .body { flex: 1; }
.alert-ribbon .title { font-size: 13px; font-weight: 800; color: #92400e; margin-bottom: 2px; }
.alert-ribbon.crit .title { color: #991b1b; }
.alert-ribbon .detail { font-size: 12px; color: #78350f; }
.alert-ribbon.crit .detail { color: #7f1d1d; }

/* ══════════════ SECTION LABELS ══════════════ */
.section-label {
  font-size: 11px; font-weight: 800; letter-spacing: 0.14em;
  text-transform: uppercase; color: var(--text-muted);
  margin: 32px 0 14px; display: flex; align-items: center; gap: 12px;
}
.section-label .icon {
  width: 24px; height: 24px; border-radius: 8px;
  background: var(--brand-50); color: var(--brand-700);
  display: flex; align-items: center; justify-content: center;
  font-size: 13px;
}
.section-label::after {
  content: ''; flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--border), transparent);
}

/* ══════════════ KPI ROW ══════════════ */
.kpi-row {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px;
  margin-bottom: 18px;
}
@media (max-width: 900px) { .kpi-row { grid-template-columns: repeat(2, 1fr); } }
.kpi-tile {
  background: var(--surface-soft); backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border); border-radius: var(--radius-lg);
  padding: 18px 20px; position: relative;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}
.kpi-tile:hover {
  transform: translateY(-2px); box-shadow: var(--shadow-md);
  border-color: var(--brand-100);
}
.kpi-tile .kpi-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 10px;
}
.kpi-tile .kpi-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.1em; color: var(--text-muted);
}
.kpi-tile .kpi-chip {
  font-size: 10px; font-weight: 700; padding: 3px 8px; border-radius: 999px;
  background: var(--brand-50); color: var(--brand-700);
}
.kpi-tile .kpi-chip.ok { background: var(--success-soft); color: #065f46; }
.kpi-tile .kpi-chip.warn { background: var(--warning-soft); color: #92400e; }
.kpi-tile .kpi-chip.bad { background: var(--danger-soft); color: #991b1b; }
.kpi-tile .kpi-value {
  font-size: 30px; font-weight: 900; line-height: 1;
  font-family: 'JetBrains Mono', monospace; letter-spacing: -1.5px;
}
.kpi-tile .kpi-sub { font-size: 11px; color: var(--text-muted); margin-top: 6px; }
.kpi-tile .kpi-bar {
  height: 4px; background: var(--border-soft); border-radius: 99px;
  overflow: hidden; margin-top: 10px;
}
.kpi-tile .kpi-bar-fill {
  height: 100%; border-radius: 99px;
  transition: width 0.9s cubic-bezier(.22,.61,.36,1);
}

/* ══════════════ HEALTH GAUGE CARD ══════════════ */
.health-card {
  background: var(--surface-soft); backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border); border-radius: var(--radius-lg);
  padding: 20px 22px; display: flex; gap: 18px; align-items: center;
  margin-bottom: 18px;
}
.health-ring {
  width: 92px; height: 92px; flex-shrink: 0;
  position: relative; display: flex; align-items: center; justify-content: center;
}
.health-ring svg { width: 100%; height: 100%; transform: rotate(-90deg); }
.health-ring .score {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; font-weight: 900;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: -1px;
}
.health-body { flex: 1; }
.health-body .title { font-size: 15px; font-weight: 800; color: var(--text); }
.health-body .desc { font-size: 12px; color: var(--text-muted); margin-top: 4px; line-height: 1.5; }
.health-body .pills { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.health-pill {
  font-size: 10px; font-weight: 700; padding: 4px 9px;
  border-radius: 999px; letter-spacing: 0.04em;
}
.health-pill.ok { background: var(--success-soft); color: #065f46; }
.health-pill.warn { background: var(--warning-soft); color: #92400e; }
.health-pill.bad { background: var(--danger-soft); color: #991b1b; }

/* ══════════════ LINK GRID ══════════════ */
.links-grid {
  display: grid; grid-template-columns: repeat(6, 1fr); gap: 10px;
}
@media (max-width: 900px) { .links-grid { grid-template-columns: repeat(3, 1fr); } }
.link-tile {
  background: var(--surface-soft); backdrop-filter: blur(8px);
  border: 1px solid var(--glass-border); border-radius: var(--radius);
  padding: 14px 12px; text-align: center;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.link-tile:hover {
  transform: translateY(-2px); box-shadow: var(--shadow-md);
  border-color: var(--brand-500);
}
.link-tile .tile-icon {
  font-size: 20px; margin-bottom: 4px;
  display: inline-flex; width: 36px; height: 36px;
  align-items: center; justify-content: center;
  background: var(--brand-50); border-radius: 10px;
}
.link-tile .tile-label {
  font-size: 10px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.06em; color: var(--text-muted);
  margin: 6px 0 4px;
}
.link-tile a {
  color: var(--brand-700); font-weight: 700;
  text-decoration: none; font-size: 12px;
}
.link-tile a:hover { color: var(--brand-800); }
.link-tile.na { border-style: dashed; opacity: 0.5; }
.link-tile.na .tile-icon { background: var(--bg-alt); }

/* ══════════════ LEGEND STRIP ══════════════ */
.legend-strip {
  display: flex; gap: 20px; flex-wrap: wrap; align-items: center;
  background: var(--surface-soft); backdrop-filter: blur(6px);
  border-radius: var(--radius-sm); padding: 10px 18px;
  font-size: 11px; color: var(--text-muted);
  margin-bottom: 6px; border: 1px solid var(--glass-border);
}
.legend-strip b { font-weight: 700; color: var(--text); }

/* ══════════════ ARCHIVED ══════════════ */
.archived-card {
  background: linear-gradient(135deg, rgba(240,253,250,0.85) 0%, rgba(204,251,241,0.65) 100%);
  backdrop-filter: blur(10px); border: 1px solid #99f6e4;
  border-left: 4px solid var(--brand-600);
  border-radius: var(--radius-lg); padding: 24px 28px; margin: 16px 0;
}
.archived-card h3 { color: var(--brand-700); margin: 0 0 8px; font-size: 18px; font-weight: 800; }
.archived-card p { color: var(--text); font-size: 14px; line-height: 1.65; margin: 0; }

/* ══════════════ LOGIN ══════════════ */
.login-shell { max-width: 440px; margin: 6vh auto; text-align: center; }
.login-shell .logo-circle {
  width: 80px; height: 80px; background: var(--g-brand);
  border-radius: 22px; display: flex; align-items: center; justify-content: center;
  margin: 0 auto 20px; font-size: 34px; color: #fff;
  box-shadow: 0 12px 32px rgba(15,23,42,0.30);
  position: relative;
}
.login-shell .logo-circle::after {
  content: ''; position: absolute; inset: -6px;
  border: 1px solid var(--brand-100); border-radius: 28px; opacity: 0.6;
}
.login-shell h2 {
  font-size: 28px; font-weight: 800; color: var(--text);
  margin-bottom: 4px; letter-spacing: -0.5px;
}
.login-shell .sub { font-size: 13px; color: var(--text-muted); margin-bottom: 26px; }
.login-about-card {
  max-width: 440px; margin: 16px auto 0;
  background: var(--surface-soft); backdrop-filter: blur(10px);
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 20px 22px; text-align: left;
  box-shadow: var(--shadow-xs);
}
.login-about-card h4 {
  color: var(--brand-700); margin: 0 0 8px;
  font-size: 13px; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.login-about-card p {
  font-size: 13px; color: var(--text-muted);
  line-height: 1.6; margin: 0;
}
.login-trust {
  display: flex; justify-content: center; gap: 18px;
  margin-top: 20px; font-size: 11px; color: var(--text-soft);
}
.login-trust .pill {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 12px; background: var(--surface-soft);
  border: 1px solid var(--border-soft); border-radius: 999px;
}
.error-toast {
  background: rgba(254,242,242,0.92); border-left: 4px solid var(--danger);
  border-radius: var(--radius); padding: 14px 18px; margin-top: 12px; text-align: left;
}
.error-toast strong { color: #991b1b; }
.error-toast p { color: #7f1d1d; font-size: 13px; margin: 4px 0 0; }

/* ══════════════ UPDATE LOG ══════════════ */
.upd-day {
  margin: 10px 0 14px; padding: 8px 12px 8px 16px;
  border-left: 3px solid var(--brand-700); background: var(--surface-soft);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
}
.upd-date { font-weight: 700; margin-bottom: 6px; color: var(--brand-700); font-size: 12px; }
.upd-item { margin: 4px 0; color: var(--text); font-size: 13px; line-height: 1.5; }
.upd-dot { color: var(--text-soft); margin-right: 8px; }
.upd-sep { height: 1px; background: var(--border); margin: 14px 0; }

/* ══════════════ STREAMLIT OVERRIDES ══════════════ */
.stSelectbox label, .stMultiSelect label, .stTextInput label {
  font-size: 11px !important; font-weight: 700 !important;
  color: var(--text-muted) !important;
  text-transform: uppercase; letter-spacing: 0.08em;
}
.stDataFrame {
  border-radius: var(--radius) !important; overflow: hidden;
  box-shadow: var(--shadow-xs) !important; background: var(--surface-soft) !important;
  border: 1px solid var(--border-soft) !important;
}
div[data-testid="stExpander"] {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  overflow: hidden; background: var(--surface-soft) !important;
  backdrop-filter: blur(8px) !important;
  box-shadow: var(--shadow-xs);
}
div[data-testid="stExpander"] summary {
  font-weight: 700 !important; font-size: 13px !important;
  padding: 14px 18px !important;
}
.stDownloadButton button, .stButton button {
  border-radius: var(--radius) !important;
  font-weight: 700 !important;
  font-family: 'Outfit', sans-serif !important;
  transition: transform 0.15s, box-shadow 0.15s !important;
}
.stDownloadButton button:hover, .stButton button:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md) !important;
}
.stButton button[kind="primary"] {
  background: var(--g-brand-soft) !important; border: none !important;
}
.js-plotly-plot .plotly { border-radius: var(--radius); }
div[data-testid="stAlert"] {
  background: var(--surface-soft) !important;
  backdrop-filter: blur(8px) !important;
  border-radius: var(--radius) !important;
  border: 1px solid var(--border-soft) !important;
}
/* Tabs */
div[data-baseweb="tab-list"] {
  background: transparent !important; gap: 4px;
  border-bottom: 1px solid var(--border-soft);
}
button[data-baseweb="tab"] {
  font-weight: 700 !important; font-size: 13px !important;
  color: var(--text-muted) !important;
  padding: 10px 18px !important; border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
  transition: color 0.15s, background 0.15s !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  color: var(--brand-700) !important;
  background: var(--brand-50) !important;
}
div[data-baseweb="tab-highlight"] { background: var(--brand-700) !important; height: 3px !important; }

/* Footer */
.app-footer {
  margin-top: 32px; padding: 18px 4px;
  border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11px; color: var(--text-soft);
}
.app-footer .app-footer-brand {
  display: flex; align-items: center; gap: 8px;
  font-weight: 700; color: var(--text-muted);
}
.app-footer .app-footer-brand .dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--success);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════════════════════════
csv_url       = st.secrets["CSV_URL_MAIN"]
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

def health_ring_svg(score: float, color: str) -> str:
    """Circular progress ring SVG for the health score card."""
    score = max(0.0, min(100.0, float(score)))
    r = 40
    c = 2 * np.pi * r
    offset = c * (1 - score / 100.0)
    return f"""
    <svg viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="{r}" fill="none"
              stroke="#e2e8f0" stroke-width="8"/>
      <circle cx="50" cy="50" r="{r}" fill="none"
              stroke="{color}" stroke-width="8" stroke-linecap="round"
              stroke-dasharray="{c:.2f}" stroke-dashoffset="{offset:.2f}"
              style="transition: stroke-dashoffset 0.9s ease"/>
    </svg>
    """

# ══════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.markdown("<div style='height:4vh'></div>", unsafe_allow_html=True)
    placeholder = st.empty()
    with placeholder.form("login"):
        st.markdown("""
        <div class="login-shell">
          <div class="logo-circle">📊</div>
          <h2>ATR Consulting</h2>
          <div class="sub">Data Collection &amp; QA Progress Tracker</div>
        </div>
        """, unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submit = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        st.markdown("""
        <div class="login-about-card">
          <h4>About this platform</h4>
          <p>Track data-collection progress, monitor QA workflows, and generate professional
          data summaries and surveyor performance reports — all in one secure place.</p>
        </div>
        <div class="login-trust">
          <div class="pill">🔒 Secure access</div>
          <div class="pill">⚡ Live data</div>
          <div class="pill">📊 Real-time QA</div>
        </div>
        """, unsafe_allow_html=True)
    if submit:
        if username in user_dict and password == user_dict[username]["password"]:
            st.session_state.logged_in = True
            st.session_state.username = username
            placeholder.empty()
            st.success("Welcome back!")
        else:
            st.markdown("""<div class="error-toast">
                <strong>Access denied</strong>
                <p>Incorrect username or password. Please try again.</p>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════
#  MAIN DASHBOARD
# ══════════════════════════════════════════════════════════════════
if st.session_state.logged_in:

    # ── USER PROJECT ACCESS ──
    if user_dict[st.session_state.username]["project"].split(',')[0] == 'All':
        main_project_names = df['Main Project'].unique()
    else:
        main_project_names = df[df['Main Project'].isin(
            user_dict[st.session_state.username]["project"].split(',')
        )]['Main Project'].unique()

    # ────────────────── SIDEBAR ──────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="sb-brand">
          <div class="logo">A</div>
          <div>
            <div class="title">ATR Consulting</div>
            <div class="subtitle">DC &amp; QA Platform</div>
          </div>
        </div>
        <div class="sb-user">
          <div class="avatar">{st.session_state.username[:2]}</div>
          <div class="info">
            <div class="name">{st.session_state.username}</div>
            <div class="role">QA Team</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-section-label">Portfolio</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="sb-stat">
          <span class="lbl">Accessible projects</span>
          <span class="val">{len(main_project_names)}</span>
        </div>
        <div class="sb-stat">
          <span class="lbl">Total sub-projects</span>
          <span class="val">{df[df['Main Project'].isin(main_project_names)].shape[0]}</span>
        </div>
        <div class="sb-stat">
          <span class="lbl">Last refresh</span>
          <span class="val">{datetime.now().strftime('%H:%M')}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="sb-section-label">Quick actions</div>', unsafe_allow_html=True)
        if st.button("🔄 Refresh data", use_container_width=True, key="sb_refresh"):
            st.cache_data.clear()
            st.rerun()
        if st.button("🚪 Sign out", use_container_width=True, key="sb_logout"):
            st.session_state.logged_in = False
            st.rerun()

        st.markdown("""
        <div class="sb-footer">
          ATR Consulting · v2.0<br/>
          © 2026 · Internal use only
        </div>
        """, unsafe_allow_html=True)

    # ────────────────── HERO ──────────────────
    st.markdown(f"""
    <div class="hero">
      <div class="hero-text">
        <div class="hero-eyebrow">Data Collection Platform</div>
        <h1>Data Collection &amp; QA Dashboard</h1>
        <div class="hero-sub">ATR Consulting · Live progress &amp; quality tracker</div>
      </div>
      <div class="hero-meta">
        <div class="hero-badge">
          <span class="dot"></span>{st.session_state.username}
        </div>
        <div class="hero-time">{datetime.now().strftime('%A, %d %b %Y · %H:%M')}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.toast("Press **R** to refresh · Figures include both complete and incomplete data by default.")

    # ────────────────── PROJECT SELECTOR ──────────────────
    cols1, cols2, cols3 = st.columns([1, 1, 1])
    with cols1:
        main_project = st.selectbox("Main project", main_project_names, key="selectbox_1")
    project_data = df[df['Main Project'] == main_project].reset_index()
    project_names = df[df['Main Project'] == main_project]['Project Name'].unique()

    # ────────────────── PROJECT TIMELINE ──────────────────
    st.markdown(
        '<div class="section-label"><span class="icon">📅</span>Project timeline</div>',
        unsafe_allow_html=True,
    )

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
    RUNNING_COLOR = "rgba(14,165,233,0.55)"
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
    def delay_days(plan_end, actual_end):
        if pd.notna(plan_end) and pd.notna(actual_end):
            d = (actual_end - plan_end).days
            return d if d > 0 else 0
        return 0

    for _, ps, pe, a_s, a_e in PHASES:
        for c in (ps, pe, a_s, a_e):
            if c in project_data.columns:
                project_data[c] = to_dt(project_data[c])

    # Count delayed & running phases for alerts
    delayed_count = 0
    running_count = 0

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
                if is_running: running_count += 1
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
                        font=dict(size=22, color="#0f766e"), bgcolor="rgba(0,0,0,0)")
                if not is_running:
                    d = delay_days(pe, a_e)
                    if d > 0:
                        delayed_count += 1
                        fig.add_trace(go.Scatter(
                            x=[a_e], y=[y], mode="markers+text",
                            marker=dict(size=8, color=DELAY_COLOR),
                            text=[f"+{d}d"], textposition="top center",
                            textfont=dict(size=9, color=DELAY_COLOR),
                            showlegend=False,
                        ))
                    else:
                        fig.add_annotation(x=a_e, y=y, text="<b>✓</b>",
                            showarrow=False, font=dict(size=16, color=ONTIME_COLOR), xshift=8)
            y += 1
        if project_y and responsible:
            fig.add_annotation(xref="paper", x=0.9, xanchor="left",
                y=sum(project_y) / len(project_y), yanchor="middle",
                text=f"<span style='color:#0f766e;font-size:12px;font-weight:700'>{row.get('Responsible')}</span>",
                showarrow=False)
        y += GAP

    # Alert ribbon based on timeline signals
    if delayed_count > 0:
        st.markdown(f"""
        <div class="alert-ribbon crit">
          <div class="icon">⚠️</div>
          <div class="body">
            <div class="title">{delayed_count} delayed phase{'s' if delayed_count > 1 else ''} detected</div>
            <div class="detail">Review the timeline below to identify projects running behind schedule.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    elif running_count > 0:
        st.markdown(f"""
        <div class="alert-ribbon" style="background: linear-gradient(90deg, rgba(220,252,231,0.9), rgba(240,253,250,0.7)); border-color: #86efac; border-left-color: var(--success);">
          <div class="icon">🟢</div>
          <div class="body">
            <div class="title" style="color:#065f46;">{running_count} phase{'s' if running_count > 1 else ''} running on track</div>
            <div class="detail" style="color:#047857;">All active phases are within their planned windows.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="legend-strip">
      <span><b style="color:#94a3b8">— — —</b> Planned</span>
      <span><b style="color:#0ea5e9">▬</b> Actual</span>
      <span style="color:#0ea5e9"><b>↝</b> Ongoing</span>
      <span style="color:#10b981"><b>✓</b> On time</span>
      <span style="color:#ef4444"><b>●</b> Delayed</span>
    </div>
    """, unsafe_allow_html=True)

    fig.add_vline(x=today, line_dash="dot", line_width=1, opacity=0.35)
    fig.add_annotation(x=today, y=0.99, xref="x", yref="paper",
        text="<b><i>Today</i></b>", showarrow=False, xanchor="center", yanchor="bottom",
        font=dict(size=12, color="#0f766e"))
    fig.update_yaxes(tickmode="array", tickvals=y_vals, ticktext=y_labels,
        autorange="reversed", title="")
    max_date = max(project_data[pe_c].max() if pe_c in project_data.columns else pd.Timestamp.today()
                   for _, _, pe_c, _, _ in PHASES)
    fig.update_xaxes(
        range=[project_data[[ps_c for _, ps_c, _, _, _ in PHASES if ps_c in project_data.columns]].min().min(),
               max_date + pd.Timedelta(days=20)],
        showgrid=True, gridcolor="rgba(0,0,0,0.03)", zeroline=False)
    fig.update_layout(
        height=max(380, 20 * len(y_vals)),
        margin=dict(l=95, r=80, t=20, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        hovermode="closest", font=dict(family="Outfit, sans-serif"))
    st.plotly_chart(fig, use_container_width=True)


    # ────────────────── SUB-PROJECT + ROADMAP ──────────────────
    st.markdown(
        '<div class="section-label"><span class="icon">🎯</span>Round / Sub-project</div>',
        unsafe_allow_html=True,
    )
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

    # ── ROADMAP STEPPER ──
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
                ring_bg, ring_border, txt_color, txt_weight, size = '#0f766e', '#0f766e', '#0f766e', '700', '30px'
            elif s == 'ongoing':
                inner = '<div style="width:10px;height:10px;background:#fff;border-radius:50%;animation:pulse-dot 2s ease infinite;"></div>'
                ring_bg, ring_border, txt_color, txt_weight, size = '#0f172a', '#0f172a', '#0f172a', '800', '36px'
            else:
                inner = '<div style="width:6px;height:6px;background:#cbd5e1;border-radius:50%;"></div>'
                ring_bg, ring_border, txt_color, txt_weight, size = 'rgba(255,255,255,0.8)', '#e2e8f0', '#94a3b8', '500', '28px'
            shadow = "box-shadow:0 0 0 5px rgba(15,23,42,0.08);" if s=='ongoing' else ""
            nodes_html += f"""<div style="display:flex;flex-direction:column;align-items:center;width:{100/num_steps}%;">
                <div style="width:{size};height:{size};border-radius:50%;background:{ring_bg};border:2px solid {ring_border};
                    display:flex;align-items:center;justify-content:center;z-index:2;{shadow}">{inner}</div>
                <p style="margin-top:36px;font-size:10px;font-weight:{txt_weight};color:{txt_color};width:84px;text-align:center;line-height:1.3;letter-spacing:0.02em;">{step['label']}</p>
            </div>"""
        pw = f"calc({progress_pct}%)" if num_steps > 1 else "0%"
        return f"""<style>@keyframes pulse-dot{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.5);opacity:.5}}}}</style>
        <div style="max-width:100%;margin:0 auto;padding:20px 8px;">
          <div style="position:relative;width:100%;">
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:100%;height:4px;background:#e2e8f0;border-radius:99px;"></div>
            <div style="position:absolute;top:50%;transform:translateY(-50%);width:{pw};height:4px;background:linear-gradient(90deg,#0f766e,#14b8a6);border-radius:99px;transition:width .5s;"></div>
            <div style="position:relative;display:flex;justify-content:space-between;align-items:flex-start;width:100%;">{nodes_html}</div>
          </div>
        </div>"""

    steps_data = [
        {"label": "Form Coding (XLSForm)"}, {"label": "Training"},
        {"label": "QA-Manual Checks"}, {"label": "QA-Automated Checks"},
        {"label": "QA-Dataset Finalization"}, {"label": "DM-Dataset Finalization"},
        {"label": "QA Report"}, {"label": "QA Completion"},
    ]
    current_step = project_data['current_step'][0]
    st.components.v1.html(generate_roadmap_html(steps_data, current_step), height=150)

    # ────────────────── PROJECT LINKS ──────────────────
    st.markdown(
        '<div class="section-label"><span class="icon">🔗</span>Project resources</div>',
        unsafe_allow_html=True,
    )
    links_row = project_data[['Tool link', 'XLSForm link', 'QA-Notes link',
                              'Tracker link', 'DC Tracker', 'Document folder link']].iloc[0]
    link_labels = {
        'Tool link':          ('🛠️', 'Tool'),
        'XLSForm link':       ('📋', 'XLSForm'),
        'QA-Notes link':      ('📊', 'QA Notes'),
        'Tracker link':       ('📈', 'QA Tracker'),
        'DC Tracker':         ('📉', 'DC Tracker'),
        'Document folder link': ('📁', 'Docs'),
    }
    cards_html = '<div class="links-grid">'
    for col_name, (icon, label) in link_labels.items():
        value = links_row[col_name]
        if pd.notna(value) and str(value).strip():
            cards_html += (f'<div class="link-tile">'
                           f'<div class="tile-icon">{icon}</div>'
                           f'<div class="tile-label">{label}</div>'
                           f'<a href="{value}" target="_blank">Open →</a></div>')
        else:
            cards_html += (f'<div class="link-tile na">'
                           f'<div class="tile-icon">{icon}</div>'
                           f'<div class="tile-label">{label}</div>'
                           f'<span style="font-size:11px;color:#94a3b8;font-style:italic;">Not available</span></div>')
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)


    # ────────────────── ARCHIVED OR DATA SECTION ──────────────────
    if proj_completed == "Yes":
        st.markdown("""
        <div class="archived-card">
          <h3>📁 Project archived</h3>
          <p>This project has been archived. For complete information on sampling and site visits,
          please refer to the <b>Documents</b> folder. Relevant datasets and trackers
          remain available through the project links above.</p>
        </div>
        """, unsafe_allow_html=True)

    else:
        # ── DATA LOADING + PROCESSING ──
        with st.spinner('Loading / refreshing project data…'):
            missing = pd.DataFrame(columns=['Tool', 'V_ID', 'KEY', 'Type', 'QA_Status'])
            rawsheet = project_data['raw_sheet'][0]
            Project_QA_ID  = project_data['Sampling_ID'][0]
            Project_QA_ID2 = project_data['QAlog_ID'][0]
            Project_QA_ID3 = project_data['HFC_ID'][0]
            raw_sheet_id = rawsheet.split('/d/')[1].split('/')[0]
            csv_url_raw = f"https://docs.google.com/spreadsheets/d/{raw_sheet_id}/export?format=csv&id={raw_sheet_id}&gid=0"
            t = pd.read_csv(csv_url_raw)
            t['KEY_Unique'] = t['KEY']
            qasheet = ("https://docs.google.com/spreadsheets/d/1V1SfBZUwHN0NtXFIoiXEh7JGkpTUOLZnGAfFN8QVXYQ/export?format=csv&"
                       + Project_QA_ID2)
            qalog = pd.read_csv(qasheet)
            t = pd.merge(t, qalog[['QA_Status', 'KEY_Unique']].drop_duplicates('KEY_Unique'),
                         on='KEY_Unique', how='left')
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
            samplingsheet = ("https://docs.google.com/spreadsheets/d/1U0Y7TQnTFEg1edMb0IHejOxv9S2YLY2UH-tp1qzXyBg/export?format=csv&"
                             + Project_QA_ID)
            tari = pd.read_csv(samplingsheet)
            tari['V_ID'] = tari['Tool'] + "/" + tari['V_ID']
            tari = tari[tari['Skipped'] != "Yes"]
            tari = tari[(tari["Tool"].isin(t["Tool"].unique())) &
                        (tari["Tool"].isin(project_data_tools["Tool"]))]
            df_free = t[t["Tool"].isin(project_data_tools["Tool"]) & ~t["Tool"].isin(tari["Tool"])].copy()
            df_free = df_free.drop(columns=["KEY", "QA_Status"], errors='ignore')
            df_free = df_free[tari.columns.intersection(df_free.columns)]
            tari = pd.concat([tari, df_free], ignore_index=True)

        # ── FILTERS ──
        st.markdown(
            '<div class="section-label"><span class="icon">🎛️</span>Filters</div>',
            unsafe_allow_html=True,
        )
        tool_names = project_data_tools['Tool'].unique()
        coll1, coll2, coll3 = st.columns(3)
        with coll1:
            selected_tool = st.multiselect('Tool', tool_names, default=None,
                placeholder="All tools")
        if selected_tool:
            t    = t[t.Tool.isin(selected_tool)]
            tari = tari[tari.Tool.isin(selected_tool)]
        with coll2:
            qastatus = st.multiselect('QA status', t.QA_Status.unique().tolist(),
                default=[x for x in t.QA_Status.unique().tolist() if x != 'Rejected_paused'])
        with coll3:
            status_options = ['Complete', 'Incomplete']
            completion = st.multiselect('Completion status', options=status_options,
                default=['Complete', 'Incomplete'])

        t = t[(t.QA_Status.isin(qastatus)) & (t.Completion_status.isin(completion))].copy()
        tari = tari.merge(t[['V_ID'] + [c for c in t.columns if c not in tari.columns and c != 'V_ID']]
                            .drop_duplicates('V_ID'), on='V_ID', how='left')
        t    = t.merge(tari[['V_ID'] + [c for c in tari.columns if c not in t.columns and c != 'V_ID']]
                            .drop_duplicates('V_ID'), on='V_ID', how='left')

        if list(tool_col_map.values())[0].rsplit('-', 1)[-1] == 'occurance':
            tall2 = t[t["V_ID"].str.startswith(
                tuple(tari["V_ID"].str.rsplit("-", n=1).str[0].unique()), na=False)]

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

        fig_timeline = px.area(dff, x='Date', y='N')
        fig_timeline.update_traces(
            line=dict(color='#0f766e', width=2.5),
            fillcolor='rgba(15,118,110,0.08)',
            mode='lines+markers',
            marker=dict(color='#0f766e', size=5,
                        line=dict(width=2, color='rgba(255,255,255,0.8)')))
        fig_timeline.update_layout(
            xaxis_title='', yaxis_title='Submissions',
            template='plotly_white', height=300,
            margin=dict(l=40, r=20, t=10, b=30),
            font=dict(family="Outfit, sans-serif"),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="rgba(0,0,0,0.03)"),
            yaxis=dict(gridcolor="rgba(0,0,0,0.05)"))

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
                fill_opacity=0.8, line_opacity=0.25,
                nan_fill_color="#EAEAEA", nan_fill_opacity=0.65,
                legend_name="Visits").add_to(m)
            folium.GeoJson(
                geo,
                style_function=lambda f: {"color": "#777", "weight": 0.7, "fillOpacity": 0},
                highlight_function=lambda f: {"color": "#111", "weight": 2},
                tooltip=folium.GeoJsonTooltip(
                    fields=["NAME_1", "VISITS"],
                    aliases=["Province:", "Visits:"], sticky=True),
            ).add_to(m)
            return m

        counts = t.groupby("Province").size().reset_index(name="count")
        counts["Province"] = counts["Province"].astype(str).str.strip()
        counts = counts[["Province", "count"]]
        geo_raw = load_geojson("afghanistan_provinces.geojson")
        m = build_map(geo_raw, counts)

        # ── COMPUTE DATA METRICS ──
        target   = tari.groupby('Tool').size()
        received = tari[tari.QA_Status.notna()].groupby('Tool').size()
        approved = tari[tari.QA_Status == 'Approved'].groupby('Tool').size()
        rejected = tari[tari.QA_Status == 'Rejected'].groupby('Tool').size()
        awaiting = tari[tari.QA_Status.isin(["Not QA'ed Yet", 'Pending'])].groupby('Tool').size()
        data_metrics = pd.DataFrame({
            'Target': target, 'Received data': received,
            'Approved data': approved, 'Rejected data': rejected,
            'Awaiting review': awaiting,
        }).fillna(0).astype(int).reset_index()
        if len(data_metrics) > 1:
            data_metrics.loc['Total'] = data_metrics.sum(numeric_only=True)
            data_metrics.loc['Total', 'Tool'] = 'All Tools'
        data_metrics['DC Completion %'] = (
            (data_metrics['Received data'] / data_metrics['Target']) * 100).round(2)
        data_metrics['Completed ✅'] = (
            data_metrics['Target'] == data_metrics['Approved data']
        ).apply(lambda x: '✅' if x else '❌')

        # ── CORE KPIs ──
        total_target    = tari.shape[0]
        total_received  = tari[tari.QA_Status.isin(qastatus)].shape[0]
        total_remaining = max(0, total_target - total_received)
        g = tari[tari.QA_Status.isin(qastatus)].QA_Status.value_counts().reset_index()
        approved_n = int(g[g['QA_Status'] == 'Approved']['count'].sum()) if 'Approved' in g['QA_Status'].values else 0
        rejected_n = int(g[g['QA_Status'] == 'Rejected']['count'].sum()) if 'Rejected' in g['QA_Status'].values else 0
        dc_pct  = round(100 * total_received / total_target) if total_target else 0
        qa_pct  = round(100 * approved_n / total_received) if total_received else 0
        rej_pct = round(100 * rejected_n / total_received) if total_received else 0

        # ── HEALTH SCORE (composite) ──
        # Weighted: completion progress (40%) + approval rate (35%) + low rejection (25%)
        health = round(
            0.40 * dc_pct
            + 0.35 * qa_pct
            + 0.25 * max(0, 100 - rej_pct * 3)
        )
        if health >= 80:
            health_color, health_label, health_desc = "#10b981", "Excellent", "This project is performing strongly across all quality indicators."
        elif health >= 60:
            health_color, health_label, health_desc = "#14b8a6", "Healthy", "Progress is steady. Monitor any rising rejection trends."
        elif health >= 40:
            health_color, health_label, health_desc = "#f59e0b", "Needs attention", "Some quality indicators are trailing. Review rejection patterns and velocity."
        else:
            health_color, health_label, health_desc = "#ef4444", "Critical", "Multiple signals require immediate action. Escalate to the QA lead."

        # Velocity (daily avg submissions over last 14 days)
        try:
            tt = tall.copy()
            tt['Date'] = pd.to_datetime(tt['Date'])
            recent = tt[tt['Date'] >= (pd.Timestamp.today() - pd.Timedelta(days=14))]
            velocity = round(recent.shape[0] / 14, 1) if recent.shape[0] else 0
            eta_days = int(np.ceil(total_remaining / velocity)) if velocity > 0 else None
        except Exception:
            velocity, eta_days = 0, None

        # ── HEALTH + KPI ROW ──
        st.markdown(
            '<div class="section-label"><span class="icon">📊</span>Key metrics</div>',
            unsafe_allow_html=True,
        )

        st.markdown(f"""
        <div class="health-card">
          <div class="health-ring">
            {health_ring_svg(health, health_color)}
            <div class="score" style="color:{health_color};">{health}</div>
          </div>
          <div class="health-body">
            <div class="title">Project health · <span style="color:{health_color};">{health_label}</span></div>
            <div class="desc">{health_desc}</div>
            <div class="pills">
              <span class="health-pill {'ok' if dc_pct>=70 else ('warn' if dc_pct>=40 else 'bad')}">DC · {dc_pct}%</span>
              <span class="health-pill {'ok' if qa_pct>=80 else ('warn' if qa_pct>=60 else 'bad')}">Approval · {qa_pct}%</span>
              <span class="health-pill {'ok' if rej_pct<=10 else ('warn' if rej_pct<=25 else 'bad')}">Rejection · {rej_pct}%</span>
              <span class="health-pill ok">Velocity · {velocity}/day</span>
              {f'<span class="health-pill ok">ETA · ~{eta_days} days</span>' if eta_days is not None else ''}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── 4 KPIs ──
        st.markdown(f"""<div class="kpi-row">
          <div class="kpi-tile">
            <div class="kpi-head">
              <div class="kpi-label">DC Progress</div>
              <div class="kpi-chip">{total_received}/{total_target}</div>
            </div>
            <div class="kpi-value" style="color:#0f766e;">{dc_pct}%</div>
            <div class="kpi-sub">Received out of target</div>
            <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{dc_pct}%;background:linear-gradient(90deg,#0f766e,#14b8a6);"></div></div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-head">
              <div class="kpi-label">QA Approved</div>
              <div class="kpi-chip ok">{qa_pct}%</div>
            </div>
            <div class="kpi-value" style="color:#10b981;">{approved_n}</div>
            <div class="kpi-sub">{qa_pct}% approval rate</div>
            <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{qa_pct}%;background:linear-gradient(90deg,#10b981,#34d399);"></div></div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-head">
              <div class="kpi-label">Rejected</div>
              <div class="kpi-chip {'bad' if rej_pct>20 else ('warn' if rej_pct>10 else 'ok')}">{rej_pct}%</div>
            </div>
            <div class="kpi-value" style="color:#ef4444;">{rejected_n}</div>
            <div class="kpi-sub">{rej_pct}% rejection rate</div>
            <div class="kpi-bar"><div class="kpi-bar-fill" style="width:{rej_pct}%;background:linear-gradient(90deg,#ef4444,#f87171);"></div></div>
          </div>
          <div class="kpi-tile">
            <div class="kpi-head">
              <div class="kpi-label">Remaining</div>
              <div class="kpi-chip">{round(100-dc_pct)}%</div>
            </div>
            <div class="kpi-value" style="color:#64748b;">{total_remaining}</div>
            <div class="kpi-sub">{f'~{eta_days} days at current pace' if eta_days else 'Not yet received'}</div>
          </div>
        </div>""", unsafe_allow_html=True)


        # ────────────────── ANALYTICS TABS ──────────────────
        tab_overview, tab_analytics, tab_summaries = st.tabs(
            ["📈 Overview", "🗺️ Geography & Trends", "📑 Summaries"]
        )

        # ── TAB 1: OVERVIEW (charts + sample table) ──
        with tab_overview:
            chart_col1, chart_col2 = st.columns(2, gap="medium")

            with chart_col1:
                with st.container(border=True):
                    dm_chart = (data_metrics[data_metrics['Tool'] != 'All Tools'].copy()
                                if 'All Tools' in data_metrics['Tool'].values
                                else data_metrics.copy())
                    dm_chart = dm_chart.sort_values('Target', ascending=True)
                    fig_tool = go.Figure()
                    fig_tool.add_trace(go.Bar(
                        y=dm_chart['Tool'], x=dm_chart['Approved data'], name='Approved',
                        orientation='h', marker_color='#10b981',
                        hovertemplate='<b>%{y}</b><br>Approved: %{x}<extra></extra>'))
                    fig_tool.add_trace(go.Bar(
                        y=dm_chart['Tool'], x=dm_chart['Rejected data'], name='Rejected',
                        orientation='h', marker_color='#ef4444',
                        hovertemplate='<b>%{y}</b><br>Rejected: %{x}<extra></extra>'))
                    fig_tool.add_trace(go.Bar(
                        y=dm_chart['Tool'], x=dm_chart['Awaiting review'], name='Awaiting QA',
                        orientation='h', marker_color='#f59e0b',
                        hovertemplate='<b>%{y}</b><br>Awaiting: %{x}<extra></extra>'))
                    remaining_per_tool = (dm_chart['Target'] - dm_chart['Received data']).clip(lower=0)
                    fig_tool.add_trace(go.Bar(
                        y=dm_chart['Tool'], x=remaining_per_tool, name='Not received',
                        orientation='h', marker_color='#e2e8f0',
                        hovertemplate='<b>%{y}</b><br>Not received: %{x}<extra></extra>'))
                    fig_tool.update_layout(
                        barmode='stack',
                        title=dict(text='Progress by tool',
                                   font=dict(size=14, weight=900, family='Outfit')),
                        height=max(260, 50 * len(dm_chart)),
                        margin=dict(l=10, r=20, t=45, b=10),
                        template='plotly_white',
                        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                        legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center',
                            font=dict(size=10, color='#64748b', family='Outfit')),
                        xaxis=dict(gridcolor='rgba(0,0,0,0.04)', title=''),
                        yaxis=dict(gridcolor='rgba(0,0,0,0)', title=''),
                        font=dict(family='Outfit, sans-serif'))
                    st.plotly_chart(fig_tool, use_container_width=True)

            with chart_col2:
                with st.container(border=True):
                    if len(tall) > 0 and 'Date' in tall.columns:
                        cum_df = tall.groupby('Date').size().reset_index(name='daily')
                        cum_df = cum_df.sort_values('Date')
                        cum_df['cumulative'] = cum_df['daily'].cumsum()
                        cum_approved = (tall[tall['QA_Status'] == 'Approved']
                                        .groupby('Date').size().reset_index(name='daily_approved'))
                        cum_approved = cum_approved.sort_values('Date')
                        cum_approved['cum_approved'] = cum_approved['daily_approved'].cumsum()
                        cum_df = cum_df.merge(cum_approved[['Date', 'cum_approved']],
                                              on='Date', how='left')
                        cum_df['cum_approved'] = cum_df['cum_approved'].ffill().fillna(0).astype(int)

                        fig_cum = go.Figure()
                        fig_cum.add_hline(y=total_target, line_dash='dot',
                            line_color='#94a3b8', line_width=1.5,
                            annotation_text=f'Target: {total_target}',
                            annotation_position='top right',
                            annotation_font=dict(size=10, color='#94a3b8', family='Outfit'))
                        fig_cum.add_trace(go.Scatter(
                            x=cum_df['Date'], y=cum_df['cumulative'], name='Total received',
                            mode='lines', line=dict(color='#0f766e', width=2.5),
                            fill='tozeroy', fillcolor='rgba(15,118,110,0.06)',
                            hovertemplate='<b>%{x}</b><br>Total: %{y}<extra></extra>'))
                        fig_cum.add_trace(go.Scatter(
                            x=cum_df['Date'], y=cum_df['cum_approved'], name='Approved',
                            mode='lines', line=dict(color='#10b981', width=2, dash='dash'),
                            hovertemplate='<b>%{x}</b><br>Approved: %{y}<extra></extra>'))
                        fig_cum.update_layout(
                            title=dict(text='Cumulative progress',
                                       font=dict(size=14, weight=900, family='Outfit')),
                            height=max(260, 50 * len(dm_chart)),
                            margin=dict(l=40, r=20, t=45, b=10),
                            template='plotly_white',
                            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                            legend=dict(orientation='h', y=-0.15, x=0.5, xanchor='center',
                                font=dict(size=10, color='#64748b', family='Outfit')),
                            xaxis=dict(gridcolor='rgba(0,0,0,0.03)', title=''),
                            yaxis=dict(gridcolor='rgba(0,0,0,0.05)', title='Submissions'),
                            font=dict(family='Outfit, sans-serif'))
                        st.plotly_chart(fig_cum, use_container_width=True)
                    else:
                        st.info("No submission dates available for the cumulative chart.")

            # Sample tracking table
            st.markdown(
                '<div class="section-label"><span class="icon">📋</span>Sample tracking by tool</div>',
                unsafe_allow_html=True,
            )
            st.dataframe(data_metrics, hide_index=True, use_container_width=True)

        # ── TAB 2: GEOGRAPHY & TRENDS ──
        with tab_analytics:
            colii1, colii2 = st.columns([1.1, 1], gap="medium")
            with colii1:
                with st.container(border=True):
                    st.markdown("##### 🗺️ Geographic coverage")
                    st.caption("Submissions by province — hover for details")
                    st_folium(m, height=320, use_container_width=True,
                              returned_objects=[], key="afg_map")
            with colii2:
                with st.container(border=True):
                    st.markdown("##### 📈 Submission timeline")
                    st.caption("Daily submission volume over time")
                    st.plotly_chart(fig_timeline, use_container_width=True)

            # QA status donut
            with st.container(border=True):
                st.markdown("##### 🍩 QA status distribution")
                qa_counts = pd.DataFrame({
                    'Status': ['Approved', 'Rejected', 'Awaiting review', 'Not received'],
                    'Count':  [approved_n, rejected_n,
                               max(0, total_received - approved_n - rejected_n),
                               total_remaining],
                    'Color':  ['#10b981', '#ef4444', '#f59e0b', '#e2e8f0'],
                })
                qa_counts = qa_counts[qa_counts['Count'] > 0]
                fig_donut = go.Figure(go.Pie(
                    labels=qa_counts['Status'], values=qa_counts['Count'],
                    hole=0.62, marker=dict(colors=qa_counts['Color'].tolist(),
                                           line=dict(color='#fff', width=2)),
                    textinfo='label+percent', textposition='outside',
                    textfont=dict(size=12, family='Outfit', color='#0f172a'),
                    hovertemplate='<b>%{label}</b><br>%{value} (%{percent})<extra></extra>',
                ))
                fig_donut.update_layout(
                    height=320, margin=dict(l=10, r=10, t=20, b=10),
                    template='plotly_white',
                    plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                    showlegend=False,
                    font=dict(family='Outfit, sans-serif'),
                    annotations=[dict(
                        text=f"<b style='font-size:22px;color:#0f172a'>{total_target}</b><br>"
                             f"<span style='font-size:10px;color:#64748b;letter-spacing:0.08em'>TOTAL TARGET</span>",
                        showarrow=False, x=0.5, y=0.5,
                        font=dict(family='Outfit'))])
                st.plotly_chart(fig_donut, use_container_width=True)

        # ── TAB 3: SUMMARIES ──
        with tab_summaries:
            st.info('ℹ️ Summaries include both "Complete" and "Incomplete" submissions by default. Select only "Complete" for accurate sample tracking.')

            col3, col4 = st.columns(2, gap="medium")
            with col3:
                with st.container(border=True):
                    st.markdown("##### 📦 Sample summary")
                    disag2 = st.multiselect('Group by', tari.columns.tolist(), def_var0,
                        help='Create summaries based on selected columns.',
                        key='disag2_key')
                    if disag2:
                        st.markdown("**DC progress summary**")
                        total_target_s  = tari.fillna('NAN').groupby(disag2).size()
                        received_data_s = tari.fillna('NAN')[tari['QA_Status'].isin(qastatus)].groupby(disag2).size()
                        summary = pd.DataFrame({
                            'Total_Target': total_target_s,
                            'Received_Data': received_data_s,
                        }).fillna(0).astype(int)
                        summary['Remaining'] = summary['Total_Target'] - summary['Received_Data']
                        summary['Completed ✅'] = (
                            summary['Received_Data'] == summary['Total_Target']
                        ).apply(lambda x: '✅' if x else '❌')
                        st.dataframe(summary)
                    else:
                        st.caption("Select one or more columns to generate a sample summary.")

            with col4:
                with st.container(border=True):
                    st.markdown("##### 📊 Dataset summary")
                    disag = st.multiselect('Group by', tall.columns.tolist(), default=def_var1,
                        help='Create summaries based on selected columns.',
                        key='disag_key')
                    if disag:
                        st.markdown("**Summary**")
                        if len(disag) == 1:
                            disag_t = tall.groupby(disag).size().reset_index().rename(columns={0: 'N'})
                            disag_t.loc[len(disag_t)] = ['Total', disag_t['N'].sum()]
                        else:
                            disag_t = tall.groupby(disag).size().unstack(disag[-1], fill_value=0).reset_index()
                            disag_t.loc['Total'] = disag_t.sum(numeric_only=True)
                        st.dataframe(disag_t)
                    else:
                        st.caption("Select one or more columns to generate a dataset summary.")

            if 'tall2' in locals():
                with st.container(border=True):
                    st.markdown("##### 📞 Tryouts summary (phone surveys)")
                    disag_raw = st.multiselect('Group by', tall2.columns.tolist(), def_var2,
                        help='For phone surveys where multiple attempts to reach respondents may be necessary.',
                        key='disag_raw_key')
                    if disag_raw:
                        st.markdown("**Raw data (tryouts)**")
                        if len(disag_raw) == 1:
                            disag_traw = tall2.groupby(disag_raw).size().reset_index().rename(columns={0: 'N'})
                            disag_traw.loc[len(disag_traw)] = ['Total', disag_traw['N'].sum()]
                        else:
                            disag_traw = tall2.groupby(disag_raw).size().unstack(disag_raw[-1], fill_value=0).reset_index()
                            disag_traw.loc['Total'] = disag_traw.sum(numeric_only=True)
                        st.dataframe(disag_traw)
                    else:
                        st.caption("Select one or more columns to generate a tryouts summary.")

        # ── MISSING / DUPLICATE DETECTION + DOWNLOAD ──
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

        # ── DOWNLOAD BAR ──
        st.markdown(
            '<div class="section-label"><span class="icon">⬇️</span>Downloads &amp; notes</div>',
            unsafe_allow_html=True,
        )
        col_dl1, col_dl2 = st.columns([1, 2])
        with col_dl1:
            tari_csv = convert_df_to_csv(tari)
            st.download_button(
                label="📥 Download target data (CSV)",
                data=tari_csv,
                file_name=f'Sample_Tracking_{selected_project}_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True,
            )

        j = project_data['notes'][0]
        if j != "-":
            st.markdown(eval(j[1:-1]), unsafe_allow_html=True)


    # ══════════════ UPDATE LOGS ══════════════
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
    header = f"📋 Project updates · {total_logs} update{'s' if total_logs != 1 else ''}"
    if start_d:
        header += f" · {start_d.strftime('%d %b %Y')} → {end_d.strftime('%d %b %Y')}"
    with st.expander(header, expanded=False):
        days = list(by_day.items())
        for i, (d, msgs) in enumerate(days):
            st.markdown(f"""<div class="upd-day">
              <div class="upd-date">{d.strftime('%d %b %Y')}</div>
              {''.join([f"<div class='upd-item'><span class='upd-dot'>•</span>{m_item}</div>" for m_item in msgs])}
            </div>{"<div class='upd-sep'></div>" if i < len(days)-1 else ""}""", unsafe_allow_html=True)

    # ══════════════ SURVEYOR REPORT (ECD / EFSP) ══════════════
    if main_project in ['ECD', 'EFSP']:
        st.markdown(
            '<div class="section-label"><span class="icon">📄</span>Surveyor performance report</div>',
            unsafe_allow_html=True,
        )
        st.caption("Generate a full HTML report covering the surveyor performance matrix and detailed feedback log.")
        sr = st.button("🧾 Generate surveyor performance report",
                       key="create_report_btn", type="primary",
                       use_container_width=False)

        if sr and main_project in ['ECD', 'EFSP']:
            qalog2 = pd.merge(
                tall,
                qalog[['Issue_Type', 'Issue_Description', 'surveyor_notified',
                       'surveyor_response', 'issue_resolved', 'KEY_Unique']],
                on='KEY_Unique', how='left')
            qalog2['severity'] = qalog2['QA_Status'].map({
                'Rejected': 'High', 'Approved': 'Low', 'Pending': 'Medium',
            })
            issues = qalog2[[
                'Site_Visit_ID', 'Province', 'Village', 'severity', 'QA_Status',
                'Surveyor_Name', 'KEY', 'Date', 'Issue_Type', 'Issue_Description',
                'surveyor_notified', 'surveyor_response', 'issue_resolved']].copy()
            summary_sr = (
                qalog2.groupby('Surveyor_Name').agg(
                    total_submissions=('Surveyor_Name', 'size'),
                    rejected_count=('QA_Status', lambda x: (x == 'Rejected').sum()),
                    total_feedback_ratio=('Issue_Type', lambda x: x.notna().mean()))
                .assign(rejection_ratio=lambda d: d.rejected_count / d.total_submissions)
                .reset_index()
            )
            hfcsheet = ("https://docs.google.com/spreadsheets/d/16EWCV7HTEx729ILvsYa72LkJ1P1Sw7Fo2R0FzXs3GvE/export?format=csv&"
                        + Project_QA_ID3)
            hfc = pd.read_csv(hfcsheet)
            hfc = hfc.drop_duplicates(subset='Surveyor_Name')
            summary_sr = pd.merge(summary_sr, hfc, on='Surveyor_Name', how='left').fillna(0)
            issues = issues[issues.Issue_Type.notna()].copy()
            issues["issue_resolved"] = issues["issue_resolved"].fillna("No").replace("", "No")
            for c in ["Issue_Description", "surveyor_response", "Province", "Village",
                      "Site_Visit_ID", "Surveyor_Name", "Issue_Type", "KEY"]:
                issues[c] = issues[c].fillna("")
            issues['Location'] = issues['Province'] + "-" + issues['Village']
            qalog2['Date'] = pd.to_datetime(qalog2['Date'], errors='coerce')
            chart_source = qalog2[[
                'Date', 'QA_Status', 'Surveyor_Name', 'Issue_Type', 'Issue_Description',
                'surveyor_response', 'KEY', 'Site_Visit_ID', 'Province', 'Village',
                'issue_resolved']].copy()
            chart_source['Date'] = chart_source['Date'].dt.strftime('%Y-%m-%d')
            chart_source = chart_source.dropna(subset=['Date'])
            for c in ['Issue_Type', 'Issue_Description', 'surveyor_response', 'KEY',
                      'Site_Visit_ID', 'Province', 'Village']:
                chart_source[c] = chart_source[c].fillna('')
            chart_source['issue_resolved'] = chart_source['issue_resolved'].fillna('No').replace('', 'No')
            chart_source['Location'] = chart_source['Province'] + "-" + chart_source['Village']
            chart_source_json = chart_source.to_json(orient='records')

            def score_surveyors(df_s, w_rej=0.5, w_out=0.10, w_out2=0.2, w_fb=0.2):
                df_s = df_s.copy()
                score = 100 - (
                    df_s["rejection_ratio"] * 100 * w_rej +
                    df_s["hfc_outliers_ratio"] * 100 * w_out +
                    df_s["ta_outliers"] * 100 * w_out2 +
                    df_s["total_feedback_ratio"] * 100 * w_fb
                )
                df_s["score"] = score.round(1).clip(0, 100)
                conds = [df_s["score"] >= 85, df_s["score"] >= 70, df_s["score"] >= 55]
                df_s["band"] = np.select(conds, ["Excellent", "Good", "Watch"], default="Critical")
                df_s["band_color"] = np.select(conds,
                    ["#10b981", "#3b82f6", "#f59e0b"], default="#ef4444")
                df_s["recommendation"] = np.select(conds,
                    ["Maintain monitoring", "Minor coaching", "Verify records"],
                    default="Urgent Retraining")
                return df_s

            # ── HTML REPORT BUILDER ──
            def build_html_report(project_name, meta, summary_df, issues_df, chart_src_json):
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                issues_df, summary_df = issues_df.copy(), summary_df.copy()
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
                      <td><div class="name">{r.Surveyor_Name}</div>
                          <div class="muted">ID: SURV-{abs(hash(r.Surveyor_Name)) % 1000}</div></td>
                      <td class="c"><div class="score">{r.score}</div>
                          <div class="bar"><span style="width:{r.score}%;background:{r.band_color}"></span></div></td>
                      <td><span class="pill" style="background:{r.band_color}">{r.band}</span></td>
                      <td class="c mono">{int(r.total_submissions)}</td>
                      <td class="c mono">{int(r.rejected_count)}</td>
                      <td class="c mono red">{(r.rejection_ratio*100):.1f}%</td>
                      <td class="c mono blue">{(r.total_feedback_ratio*100):.1f}%</td>
                      <td class="c mono blue">{(r.hfc_outliers_ratio*100):.1f}%</td>
                      <td class="c mono">{(float(getattr(r,"ta_outliers",0.0))*100):.1f}%</td>
                      <td class="rec">{r.recommendation}</td>
                    </tr>"""
                    for r in matrix_df.itertuples(index=False)
                )
                issues_json = issues_df.to_json(orient="records")

                report_css = """
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');
                :root{--bg:#f4f5f7;--card:#fff;--text:#0f172a;--muted:#64748b;--line:#e2e8f0;
                      --issue-bg:#fff7ed;--issue-bd:#fed7aa;--issue-date:#9a3412;--issue-txt:#7c2d12;
                      --resp-bg:#f0fdfa;--resp-bd:#99f6e4;--resp-date:#0f766e;--resp-txt:#334155;}
                *{box-sizing:border-box}
                body{margin:0;font-family:'Outfit',system-ui,sans-serif;background:var(--bg);color:var(--text)}
                .wrap{max-width:1100px;margin:0 auto;padding:18px}
                .card{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:18px}
                .top{display:flex;gap:14px;align-items:flex-start;justify-content:space-between;
                     background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 50%,#0f766e 100%);color:#fff;border:none;}
                .top .muted{color:rgba(255,255,255,0.6);}
                .badge{display:inline-block;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,0.15);color:#fff;font-size:11px;font-weight:800}
                .muted{color:var(--muted);font-size:12px}
                h1{margin:8px 0 2px;font-size:26px;line-height:1.1}
                .btn{border:0;border-radius:14px;padding:12px 14px;background:#0f766e;color:#fff;font-weight:800;cursor:pointer;font-family:'Outfit'}
                .grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-top:12px}
                .kpi .label{font-size:11px;color:var(--muted);font-weight:800;text-transform:uppercase;letter-spacing:.06em}
                .kpi .val{font-size:28px;font-weight:900;margin-top:6px;font-family:'JetBrains Mono',monospace}
                .bar{height:7px;background:#eef2f7;border-radius:999px;overflow:hidden;margin-top:8px}
                .bar span{display:block;height:100%}
                .tablecard{margin-top:12px;padding:0;overflow:hidden}
                .thead{padding:14px 18px;border-bottom:1px solid var(--line);background:#fafafa}
                table{width:100%;border-collapse:collapse}
                th,td{padding:12px 14px;border-bottom:1px solid #f1f5f9;vertical-align:top;font-size:13px}
                th{text-align:left;font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;background:#fafafa}
                .c{text-align:center}
                .mono{font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,monospace}
                .name{font-weight:900}
                .score{font-weight:900}
                .pill{display:inline-block;padding:4px 8px;border-radius:999px;color:#fff;font-size:11px;font-weight:900}
                .rec{color:var(--muted);font-style:italic;font-size:12px}
                .red{color:#dc2626}.blue{color:#2563eb}
                .filters{display:grid;grid-template-columns:1fr 180px 220px 140px;gap:10px;margin-top:12px}
                input,select{padding:10px 12px;border:1px solid var(--line);border-radius:12px;font-size:13px;background:#fff;font-family:'Outfit'}
                .ghost{background:#f1f5f9;color:#0f172a}
                .ticker tbody tr{border-bottom:1px dashed #e5e7eb}
                .ticker tbody tr:last-child{border-bottom:none}
                .ticker tbody tr td{padding-top:18px;padding-bottom:18px}
                .comment{margin-top:8px;padding:10px 12px;border-radius:12px;border:1px solid;}
                .comment-date{font-weight:900;font-size:12px}
                .comment-body{margin-top:4px;line-height:1.35;}
                .comment-divider{height:1px;margin:10px 2px;background:linear-gradient(90deg,rgba(148,163,184,0),rgba(148,163,184,0.85),rgba(148,163,184,0))}
                .issue-comments .comment{background:var(--issue-bg);border-color:var(--issue-bd);border-left:4px solid #fb923c;}
                .issue-comments .comment-date{color:var(--issue-date);}
                .issue-comments .comment-body{color:var(--issue-txt);}
                .response-comments .comment{background:var(--resp-bg);border-color:var(--resp-bd);border-left:4px solid #14b8a6;}
                .response-comments .comment-date{color:var(--resp-date);}
                .response-comments .comment-body{color:var(--resp-txt);font-style:italic;}
                .awaiting-response{color:#b91c1c;opacity:0.45;font-style:italic;font-weight:300;}
                .charts-row{display:grid;grid-template-columns:1.3fr 1fr;gap:14px;padding:18px;margin-top:4px;}
                .chart-box{background:#ffffff;border:1px solid var(--line);border-radius:14px;padding:16px;position:relative;}
                .chart-box canvas{width:100%!important;}
                @media print{.no-print{display:none!important}body{background:#fff}.wrap{padding:0}.card{border:0}}
                @media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}.filters{grid-template-columns:1fr}.charts-row{grid-template-columns:1fr}}
                """

                # Kept as a single-expression to preserve behavior; broken-out for readability.
                html_head = (
                    '<!doctype html><html><head><meta charset="utf-8"/>'
                    '<meta name="viewport" content="width=device-width,initial-scale=1"/>'
                    f'<title>{project_name} - QA Report</title>'
                    '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>'
                    f'<style>{report_css}</style></head>'
                )
                html_body = f"""<body><div class="wrap">
                  <div class="card top">
                    <div>
                      <span class="badge">{meta}</span>
                      <span class="muted" style="margin-left:10px">Report generated: {now}</span>
                      <h1>{project_name}</h1>
                      <div class="muted">Surveyor quality matrix + detailed feedback log</div>
                    </div>
                    <button class="btn no-print" onclick="window.print()">Export PDF</button>
                  </div>
                  <div class="grid">
                    <div class="card kpi"><div class="label">Overall quality score</div>
                      <div class="val">{avg_score:.1f} <span class="muted">/ 100</span></div>
                      <div class="bar"><span style="width:{avg_score}%;background:#0f766e"></span></div></div>
                    <div class="card kpi"><div class="label">Total recorded cases</div>
                      <div class="val" style="color:#4f46e5">{total_issues}</div>
                      <div class="muted">{resolved_count} resolved • {pending_count} open</div></div>
                    <div class="card kpi"><div class="label">Surveyor notifications</div>
                      <div class="val">{notified_count}</div>
                      <div class="muted">Awaiting responses for {not_notified_count} cases.</div></div>
                    <div class="card kpi"><div class="label">Critical (High severity)</div>
                      <div class="val" style="color:#dc2626">{high_severity}</div>
                      <div class="muted">Immediate coaching required</div></div>
                  </div>
                  <div class="card tablecard">
                    <div class="thead">
                      <div style="font-weight:900">Surveyor performance matrix (worst 10)</div>
                      <div class="muted">Lowest quality score surveyors</div>
                    </div>
                    <div style="overflow:auto"><table>
                      <thead><tr>
                        <th>Surveyor</th><th class="c">Score</th><th>Band</th>
                        <th class="c">Total subs</th><th class="c">Rej #</th>
                        <th class="c">Rej %</th><th class="c">Feedback %</th>
                        <th class="c">Data incons. %</th><th class="c">Speed vio. %</th>
                        <th>Action</th>
                      </tr></thead>
                      <tbody>{matrix_rows}</tbody>
                    </table></div>
                  </div>
                  <div class="card tablecard" style="margin-top:12px">
                    <div class="thead">
                      <div style="font-weight:900;text-align:center">Detailed feedback log</div>
                      <div class="filters no-print">
                        <input id="q" placeholder="Search logs..."/>
                        <select id="fResolved"><option value="">Status: all</option>
                          <option value="Yes">Resolved</option><option value="No">Pending</option></select>
                        <select id="fSurveyor"><option value="">Surveyor: all</option></select>
                        <button class="btn ghost" id="reset" type="button">Clear</button>
                      </div>
                    </div>
                    <div class="charts-row">
                      <div class="chart-box"><canvas id="trendChart"></canvas></div>
                      <div class="chart-box"><canvas id="issueTypeChart"></canvas></div>
                    </div>
                    <div style="overflow:auto"><table class="ticker">
                      <thead><tr>
                        <th>Verification detail</th><th>Surveyor response</th>
                        <th class="c">Severity</th><th class="c">Status</th>
                      </tr></thead>
                      <tbody id="tbody"></tbody>
                    </table></div>
                  </div>
                </div>"""

                report_js = """
                const data=__DATA__;const chartSource=__CHART__;
                const tbody=document.getElementById('tbody');
                const sSelect=document.getElementById('fSurveyor');
                const uniq=Array.from(new Set(data.map(x=>x.Surveyor_Name))).filter(Boolean).sort();
                for(const s of uniq){const o=document.createElement('option');o.value=s;o.textContent=s;sSelect.appendChild(o);}
                function esc(x){return String(x??"").replace(/[&<>"']/g,m=>({'"':"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[m]));}
                function formatComments(raw){const s=String(raw??"").trim();if(!s)return"";
                  const re=/\\[(\\d{1,2}\\/\\d{1,2}\\/\\d{4})\\]\\s*:?:?\\s*/g;
                  let match,lastIndex=0,lastDate=null;const blocks=[];
                  while((match=re.exec(s))!==null){if(lastDate!==null){blocks.push({date:lastDate,body:s.slice(lastIndex,match.index).trim()});}lastDate=match[1];lastIndex=re.lastIndex;}
                  if(lastDate!==null){blocks.push({date:lastDate,body:s.slice(lastIndex).trim()});}
                  if(!blocks.length)return esc(s);
                  let html="";for(let i=0;i<blocks.length;i++){if(i>0)html+='<div class="comment-divider"></div>';
                    html+=`<div class="comment"><div class="comment-date">[${esc(blocks[i].date)}]</div><div class="comment-body">${esc(blocks[i].body)}</div></div>`;}
                  return html;}
                const barColors=['#0f766e','#f59e0b','#ef4444','#10b981','#3b82f6','#ec4899','#8b5cf6','#14b8a6','#f97316','#64748b'];
                const ctx1=document.getElementById('trendChart').getContext('2d');
                const trendChart=new Chart(ctx1,{type:'line',data:{labels:[],datasets:[
                  {label:'Total',data:[],borderColor:'#0f766e',backgroundColor:'rgba(15,118,110,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#0f766e'},
                  {label:'Rejected',data:[],borderColor:'#ef4444',backgroundColor:'rgba(239,68,68,0.08)',borderWidth:2.5,tension:0.3,fill:true,pointRadius:3,pointBackgroundColor:'#ef4444'}]},
                  options:{responsive:true,maintainAspectRatio:true,plugins:{title:{display:true,text:'Daily submissions',font:{size:14,weight:'900',family:'Outfit'}},legend:{position:'top',labels:{usePointStyle:true,pointStyle:'circle',padding:14,font:{size:11,weight:'700'}}}},scales:{x:{ticks:{maxRotation:45,font:{size:9},maxTicksLimit:15},grid:{display:false}},y:{beginAtZero:true,grid:{color:'#f1f5f9'}}}}});
                const ctx2=document.getElementById('issueTypeChart').getContext('2d');
                const issueTypeChart=new Chart(ctx2,{type:'bar',data:{labels:[],datasets:[{label:'Count',data:[],backgroundColor:[],borderColor:[],borderWidth:1.5,borderRadius:6,barPercentage:0.7}]},
                  options:{responsive:true,maintainAspectRatio:true,indexAxis:'y',plugins:{title:{display:true,text:'Issues by type',font:{size:14,weight:'900',family:'Outfit'}},legend:{display:false}},scales:{x:{beginAtZero:true,grid:{color:'#f1f5f9'},ticks:{stepSize:1}},y:{ticks:{font:{size:11,weight:'600'}},grid:{display:false}}}}});
                function updateCharts(sf,qf,rf){let f=chartSource;if(sf)f=f.filter(r=>r.Surveyor_Name===sf);if(rf)f=f.filter(r=>r.issue_resolved===rf);
                  if(qf){const q=qf.toLowerCase();f=f.filter(r=>((r.Surveyor_Name||'')+' '+(r.KEY||'')+' '+(r.Issue_Type||'')+' '+(r.Issue_Description||'')).toLowerCase().includes(q));}
                  const dm={};for(const r of f){if(!r.Date)continue;if(!dm[r.Date])dm[r.Date]={t:0,r:0};dm[r.Date].t+=1;if(r.QA_Status==='Rejected')dm[r.Date].r+=1;}
                  const sd=Object.keys(dm).sort();trendChart.data.labels=sd;trendChart.data.datasets[0].data=sd.map(d=>dm[d].t);trendChart.data.datasets[1].data=sd.map(d=>dm[d].r);trendChart.update();
                  const tm={};for(const r of f){if(!r.Issue_Type)continue;tm[r.Issue_Type]=(tm[r.Issue_Type]||0)+1;}
                  const st=Object.entries(tm).sort((a,b)=>b[1]-a[1]);issueTypeChart.data.labels=st.map(e=>e[0]);
                  issueTypeChart.data.datasets[0].data=st.map(e=>e[1]);
                  issueTypeChart.data.datasets[0].backgroundColor=st.map((_,i)=>barColors[i%barColors.length]+'cc');
                  issueTypeChart.data.datasets[0].borderColor=st.map((_,i)=>barColors[i%barColors.length]);
                  issueTypeChart.update();}
                function render(){const q=document.getElementById('q').value.toLowerCase();const res=document.getElementById('fResolved').value;const sur=document.getElementById('fSurveyor').value;
                  updateCharts(sur,q,res);const out=[];
                  for(const i of data){if(res&&i.issue_resolved!==res)continue;if(sur&&i.Surveyor_Name!==sur)continue;
                    if(q){const blob=((i.Surveyor_Name||"")+' '+(i.KEY||"")+' '+(i.Issue_Type||"")+' '+(i.Issue_Description||"")).toLowerCase();if(!blob.includes(q))continue;}
                    out.push(`<tr><td>
                      <div class="muted" style="font-weight:900;text-transform:uppercase;color:#0f766e">${esc(i.Surveyor_Name)}</div>
                      <div class="muted">KEY: ${esc(i.KEY)}</div>
                      <div class="muted">Location: ${esc(i.Location)}</div>
                      <div style="font-weight:700;margin-top:8px">Issue: <span style="font-weight:400;text-decoration:underline">${esc(i.Issue_Type)}</span></div>
                      <div class="muted">QA: <span style="font-weight:900;color:${i.QA_Status==='Rejected'?'#ef4444':'#10b981'}">${esc(i.QA_Status)}</span></div>
                      <div class="muted" style="margin-top:8px"><span style="color:#dc2626;font-weight:900">ISSUE:</span>
                        <div class="issue-comments">${formatComments(i.Issue_Description)}</div></div>
                    </td><td><div class="response-comments">${i.surveyor_response?formatComments(i.surveyor_response):'<div class="awaiting-response">Awaiting response...</div>'}</div></td>
                    <td class="c"><span class="pill" style="background:#e2e8f0;color:#0f172a">${esc(i.severity)}</span></td>
                    <td class="c"><span class="pill" style="background:${i.issue_resolved==="Yes"?"#dcfce7":"#ffe4e6"};color:${i.issue_resolved==="Yes"?"#166534":"#9f1239"}">${i.issue_resolved==="Yes"?"Closed":"Pending"}</span></td></tr>`);}
                  tbody.innerHTML=out.join("");}
                document.getElementById('q').addEventListener('input',render);
                document.getElementById('fResolved').addEventListener('input',render);
                document.getElementById('fSurveyor').addEventListener('input',render);
                document.getElementById('reset').addEventListener('click',()=>{document.getElementById('q').value="";document.getElementById('fResolved').value="";document.getElementById('fSurveyor').value="";render();});
                render();
                """
                report_js = report_js.replace("__DATA__", issues_json).replace("__CHART__", chart_src_json)
                return html_head + html_body + f"<script>{report_js}</script></body></html>"

            p_name = selected_project
            m_text = "ATR-QA Department"
            summary_scored = score_surveyors(summary_sr, w_rej=0.35, w_out=0.1, w_out2=0.2, w_fb=0.35)
            report_html = build_html_report(p_name, m_text, summary_scored, issues, chart_source_json)
            st.download_button(
                label="⬇ Download surveyor report (HTML)",
                data=report_html,
                file_name=f"Audit_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html",
                use_container_width=True, type="primary",
                key="download_report_btn",
            )

    # ══════════════ FOOTER ══════════════
    st.markdown(f"""
    <div class="app-footer">
      <div class="app-footer-brand">
        <span class="dot"></span>
        ATR Consulting · Data Collection &amp; QA Platform
      </div>
      <div>v2.0 · {datetime.now().strftime('%Y')} · All times local</div>
    </div>
    """, unsafe_allow_html=True)
