"""
Indoor Occupational Heat Stress Dashboard
Unit 1 — Surat
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
from datetime import datetime, timedelta
import time
import math

st.set_page_config(
    page_title="Heat Stress Monitor | Unit 1",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root {
    --bg: #dbeafe;
    --surface: #bfdbfe;
    --surface2: #eff6ff;
    --border: #93c5fd;
    --font: 'Calibri', 'Segoe UI', Arial, sans-serif;
}

html, body, [class*="css"], .stApp {
    font-family: var(--font) !important;
    background-color: var(--bg) !important;
    color: #000000 !important;
}
.stApp { background-color: var(--bg) !important; }

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 2px solid var(--border) !important;
}
[data-testid="stSidebar"] * {
    color: #000000 !important;
    font-family: var(--font) !important;
}

[data-testid="stSidebar"] .stButton > button {
    background-color: #eff6ff !important;
    color: #000000 !important;
    font-family: var(--font) !important;
    font-weight: 700 !important;
    border: 1px solid #93c5fd !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #bfdbfe !important;
}

p, span, div, li, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText {
    color: #000000 !important;
    font-family: var(--font) !important;
}

[data-testid="stDateInput"] input, input[type="text"] {
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #93c5fd !important;
    border-radius: 6px !important;
}
[data-baseweb="calendar"], [data-baseweb="datepicker"],
[data-baseweb="calendar"] * {
    background-color: #ffffff !important;
    color: #000000 !important;
}
[data-baseweb="calendar"] [aria-selected="true"] {
    background-color: #2563eb !important;
    color: #ffffff !important;
}

[data-testid="stToggle"] label, [data-testid="stToggle"] span,
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] span {
    color: #000000 !important;
    font-family: var(--font) !important;
}

[data-baseweb="select"], [data-baseweb="select"] > div {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-color: #93c5fd !important;
}
[data-baseweb="select"] span, [data-baseweb="select"] [class*="singleValue"] {
    color: #000000 !important;
}
[data-baseweb="select"] svg { fill: #000000 !important; }
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {
    background-color: #ffffff !important;
    border: 1px solid #93c5fd !important;
}
[role="option"] { background-color: #ffffff !important; color: #000000 !important; }
[role="option"]:hover { background-color: #dbeafe !important; }

.stSelectbox label, .stCheckbox label, .stToggle label,
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] p {
    color: #000000 !important;
    font-weight: 600 !important;
}

code, pre { background-color: #dbeafe !important; color: #000000 !important; border: 1px solid #93c5fd !important; }

.stTabs [data-baseweb="tab"] {
    font-family: var(--font) !important;
    font-weight: 600 !important;
    color: #000000 !important;
    font-size: 12px !important;
}

.js-plotly-plot .plotly text { fill: #000000 !important; font-family: var(--font) !important; }
.js-plotly-plot { border-radius: 8px; }

[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
    color: #000000 !important;
}

.stDownloadButton button {
    background-color: #2563eb !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    border-radius: 6px !important;
    border: none !important;
}

hr { border-color: var(--border) !important; }
#MainMenu, footer, header { visibility: hidden; }
.stDataFrame { border: 1px solid var(--border); border-radius: 8px; }

.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 12px;
    color: #000000 !important;
    box-shadow: 0 2px 6px rgba(59,130,246,0.10);
}
.metric-card .label {
    font-size: 11px; color: #000000 !important;
    text-transform: uppercase; letter-spacing: 1.5px;
    margin-bottom: 4px; font-weight: 600;
}
.metric-card .value {
    font-size: 30px; font-weight: 700;
    line-height: 1.1; color: #000000 !important;
}
.metric-card .sub { font-size: 12px; color: #000000 !important; margin-top: 4px; }
.v-safe    { color: #15803d !important; }
.v-caution { color: #92400e !important; }
.v-danger  { color: #c2410c !important; }
.v-extreme { color: #991b1b !important; }

.badge {
    display: inline-block; padding: 3px 10px; border-radius: 4px;
    font-size: 10px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;
}
/* Updated badge colours to match image: Yellow / Orange / Red scheme */
.badge-safe    { background:#dcfce7; color:#14532d !important; border:1px solid #86efac; }
.badge-caution { background:#fef08a; color:#713f12 !important; border:1px solid #ca8a04; }
.badge-danger  { background:#fb923c; color:#ffffff !important; border:1px solid #ea580c; }
.badge-extreme { background:#dc2626; color:#ffffff !important; border:1px solid #991b1b; }

.section-header {
    font-size: 12px; color: #000000 !important; text-transform: uppercase;
    letter-spacing: 2px; padding: 0 0 8px 0;
    border-bottom: 2px solid var(--border); margin-bottom: 16px; font-weight: 700;
}

.alert-box {
    border-left: 4px solid #c2410c; background: #fff7ed;
    color: #000000 !important; padding: 14px 18px;
    border-radius: 0 6px 6px 0; margin: 8px 0;
    font-size: 14px; font-weight: 500;
}
.alert-box * { color: #000000 !important; }
.alert-box strong { font-weight: 700; }

.main-title { font-size: 22px; font-weight: 700; color: #000000 !important; }
.main-subtitle { font-size: 13px; color: #000000 !important; margin-top: 2px; }
</style>
""", unsafe_allow_html=True)

# ── Floating sidebar toggle button (replaces broken Streamlit default) ────────
st.markdown("""
<style>
#sidebar-toggle-btn {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 99999;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: #1d4ed8;
    border: 2px solid #1e40af;
    box-shadow: 0 2px 8px rgba(37,99,235,0.5);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
}
#sidebar-toggle-btn:hover { background-color: #1e40af; }
#sidebar-toggle-btn svg { width: 20px; height: 20px; fill: #ffffff; }
</style>

<button id="sidebar-toggle-btn" title="Toggle sidebar" onclick="toggleSidebar()">
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>
  </svg>
</button>

<script>
function toggleSidebar() {
    // Try every known selector Streamlit uses across versions
    const selectors = [
        '[data-testid="collapsedControl"]',
        '[data-testid="stSidebarCollapsedControl"]',
        'button[aria-label="Close sidebar"]',
        'button[aria-label="Collapse sidebar"]',
        'button[aria-label="Expand sidebar"]',
        'button[aria-label="Open sidebar"]',
        'section[data-testid="stSidebar"] button',
    ];
    for (const sel of selectors) {
        const el = document.querySelector(sel);
        if (el) { el.click(); return; }
    }
    // Fallback: toggle sidebar width manually
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    if (sidebar) {
        const isCollapsed = sidebar.getAttribute('aria-expanded') === 'false'
                         || sidebar.style.width === '0px'
                         || sidebar.classList.contains('st-emotion-cache-hidden');
        sidebar.style.display = isCollapsed ? 'block' : 'none';
    }
}
</script>
""", unsafe_allow_html=True)



# ── Change 4: Renamed 2BA640 ──────────────────────────────────────────────────
DEVICES = {
    "2BA61C": {"name": "Ground Stenter",                        "zone": "Production"},
    "2D66E4": {"name": "Zero zero — near gate",                 "zone": "Entry/Circulation"},
    "2BA554": {"name": "Washing-Dyeing Range",                  "zone": "Production"},
    "2BA298": {"name": "Jigger",                                "zone": "Production"},
    "2BA638": {"name": "Jets — B/H Office",                     "zone": "Production"},
    "2BA640": {"name": "Long Jets — B/H Office",                "zone": "Production"},  # renamed
    "2BA578": {"name": "First Printing",                        "zone": "Production"},
    "2BA680": {"name": "Cabin & Stenter",                       "zone": "Production"},
    "2BA64C": {"name": "Stenter and Jet — Heighted",            "zone": "Production"},
    "2BA4CC": {"name": "Loop and Folding",                      "zone": "Post-Process"},
    "2BA558": {"name": "Transition/Circulation Area",           "zone": "Circulation"},
    "2BA478": {"name": "Second Folding — near Digital Print",   "zone": "Post-Process"},
    "2BA544": {"name": "Printing — Circulation",               "zone": "Circulation"},
    "2BA534": {"name": "Transition/Circulation Area (2)",       "zone": "Circulation"},
    "2BA650": {"name": "Printing Table",                        "zone": "Production"},
}

OIZOM_BASE = "https://opendata.oizom.com/v1"
API_KEY    = st.secrets.get("OIZOM_API_KEY", "")


def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32

def f_to_c(f: float) -> float:
    return (f - 32) * 5 / 9

def heat_index_fahrenheit(T_f: float, RH: float) -> float:
    """Full NWS Rothfusz regression with low-RH and high-RH adjustments."""
    hi_simple = 0.5 * (T_f + 61.0 + (T_f - 68.0) * 1.2 + RH * 0.094)
    if (hi_simple + T_f) / 2 < 80:
        return hi_simple
    HI = (-42.379
          + 2.04901523  * T_f
          + 10.14333127 * RH
          - 0.22475541  * T_f * RH
          - 6.83783e-3  * T_f ** 2
          - 5.481717e-2 * RH  ** 2
          + 1.22874e-3  * T_f ** 2 * RH
          + 8.5282e-4   * T_f * RH ** 2
          - 1.99e-6     * T_f ** 2 * RH ** 2)
    if RH < 13 and 80 <= T_f <= 112:
        HI -= ((13 - RH) / 4) * math.sqrt((17 - abs(T_f - 95)) / 17)
    if RH > 85 and 80 <= T_f <= 87:
        HI += ((RH - 85) / 10) * ((87 - T_f) / 5)
    return HI

def heat_index_category(hi_f: float):
    if hi_f < 80:
        return "Normal",          "safe"
    elif hi_f < 91:
        return "Caution",         "caution"
    elif hi_f < 103:
        return "Extreme Caution", "danger"
    elif hi_f < 125:
        return "Danger",          "extreme"
    else:
        return "Extreme Danger",  "extreme"

# ── Change 1: NWS-aligned colour palette (Yellow → Orange → Red) ─────────────
# Matches image exactly: yellow=Caution, orange=Extreme Caution/Danger, red=Extreme Danger
HI_COLORSCALE = [
    [0.00, "#ffffff"],   # Normal  (white/green region — below caution)
    [0.20, "#ffff00"],   # Caution (bright yellow)
    [0.45, "#ffa500"],   # Extreme Caution (orange)
    [0.70, "#ff6600"],   # Danger (deep orange)
    [1.00, "#ff0000"],   # Extreme Danger (red)
]

# Category colours matching the legend image
CAT_COLORS = {
    "Normal":          "#ffffff",
    "Caution":         "#ffff00",
    "Extreme Caution": "#ffa500",
    "Danger":          "#ff6600",
    "Extreme Danger":  "#ff0000",
}
CAT_TEXT_COLORS = {
    "Normal":          "#000000",
    "Caution":         "#000000",
    "Extreme Caution": "#000000",
    "Danger":          "#000000",
    "Extreme Danger":  "#000000",
}

def compute_heat_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Temp_F"]   = df["Temperature"].apply(celsius_to_fahrenheit)
    df["HI_F"]     = df.apply(lambda r: heat_index_fahrenheit(r["Temp_F"], r["Humidity"]), axis=1)
    df["HI_C"]     = (df["HI_F"] - 32) * 5 / 9
    cats           = df["HI_F"].apply(heat_index_category)
    df["HI_Cat"]   = [c[0] for c in cats]
    df["HI_Level"] = [c[1] for c in cats]
    return df


@st.cache_data(ttl=300)
def fetch_device_history(device_id: str, hours: int = 24) -> pd.DataFrame:
    end   = datetime.utcnow()
    start = end - timedelta(hours=hours)
    url   = (f"{OIZOM_BASE}/devices/{device_id}/data"
             f"?from={int(start.timestamp())}&to={int(end.timestamp())}&interval=3600")
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    try:
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            rows = data.get("data", data.get("payload", []))
            if rows:
                df = pd.DataFrame(rows)
                rename = {}
                for col in df.columns:
                    cl = col.lower()
                    if "temp" in cl: rename[col] = "Temperature"
                    if "hum"  in cl: rename[col] = "Humidity"
                    if "time" in cl or cl == "ts": rename[col] = "Time"
                df.rename(columns=rename, inplace=True)
                if "Time" in df.columns:
                    df["Time"] = pd.to_datetime(df["Time"], unit="s", errors="coerce")
                return df
    except Exception:
        pass
    return pd.DataFrame()


def load_sample_data() -> dict:
    np.random.seed(42)
    base_times = pd.date_range("2026-03-25 00:30", periods=48, freq="1h")
    zone_offsets = {
        "Production":        (2.0, -1.0),
        "Entry/Circulation": (0.0,  0.0),
        "Circulation":       (1.0, -0.5),
        "Post-Process":      (0.5, -0.3),
    }
    results = {}
    for did, info in DEVICES.items():
        dt_off, hum_off = zone_offsets.get(info["zone"], (0, 0))
        temps = 32 + dt_off + np.random.randn(48)*2 + 3*np.sin(np.linspace(0, 2*np.pi, 48))
        hums  = 38 + hum_off + np.random.randn(48)*1.5
        df = pd.DataFrame({"Time": base_times, "Temperature": temps, "Humidity": hums})
        results[did] = compute_heat_index(df)
    return results


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0'>
      <div class='main-title'>Indoor Occupational Heat Stress</div>
      <div class='main-subtitle'>Unit 1<br>Surat</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    auto_refresh = st.toggle("⟳ Auto-refresh (5 min)", value=False)

    st.markdown("<div style='font-size:12px;font-weight:700;color:#000000;text-transform:uppercase;"
                "letter-spacing:1px;margin:8px 0 4px 0;'>Time Window</div>", unsafe_allow_html=True)

    preset_cols = st.columns(4)
    presets = [("6h", 6), ("24h", 24), ("48h", 48), ("7d", 168)]
    if "selected_hours" not in st.session_state:
        st.session_state.selected_hours = 24
    if "use_custom_dates" not in st.session_state:
        st.session_state.use_custom_dates = False

    for col, (label, hrs) in zip(preset_cols, presets):
        with col:
            if st.button(label, key=f"preset_{hrs}", use_container_width=True):
                st.session_state.selected_hours  = hrs
                st.session_state.use_custom_dates = False

    st.markdown("<div style='font-size:11px;font-weight:600;color:#000000;"
                "margin:10px 0 2px 0;'>Custom date range</div>", unsafe_allow_html=True)
    today    = datetime.utcnow().date()
    min_date = today - timedelta(days=365)

    date_range = st.date_input(
        "From → To",
        value=(today - timedelta(days=1), today),
        min_value=min_date, max_value=today,
        key="dr", label_visibility="hidden",
    )
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        date_from, date_to = date_range[0], date_range[1]
    else:
        date_from = date_to = date_range

    if st.button("Apply date range", use_container_width=True, key="apply_dates"):
        if date_from <= date_to:
            delta_hours = int((datetime.combine(date_to,   datetime.max.time()) -
                               datetime.combine(date_from, datetime.min.time())
                               ).total_seconds() / 3600)
            st.session_state.selected_hours   = max(1, delta_hours)
            st.session_state.use_custom_dates = True
        else:
            st.error("'From' date must be before 'To' date.")

    if st.session_state.use_custom_dates:
        st.markdown(f"<div style='font-size:11px;color:#1d4ed8;font-weight:600;"
                    f"background:#eff6ff;border:1px solid #93c5fd;border-radius:6px;"
                    f"padding:5px 8px;margin-top:6px;'>"
                    f"📅 {date_from.strftime('%d %b')} → {date_to.strftime('%d %b %Y')}"
                    f"</div>", unsafe_allow_html=True)
    else:
        label_map = {6:"Last 6 hours", 24:"Last 24 hours", 48:"Last 48 hours", 168:"Last 7 days"}
        lbl = label_map.get(st.session_state.selected_hours,
                             f"Last {st.session_state.selected_hours}h")
        st.markdown(f"<div style='font-size:11px;color:#1d4ed8;font-weight:600;"
                    f"background:#eff6ff;border:1px solid #93c5fd;border-radius:6px;"
                    f"padding:5px 8px;margin-top:6px;'>🕐 {lbl}</div>",
                    unsafe_allow_html=True)

    selected_hours = st.session_state.selected_hours

    st.markdown("#### Devices")
    all_checked = st.checkbox("Select all", value=True)
    selected_devices = {}
    for did, info in DEVICES.items():
        checked = st.checkbox(f"`{did}` {info['name']}", value=all_checked, key=f"cb_{did}")
        if checked:
            selected_devices[did] = info

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px; color:#000000; font-family:Calibri,Segoe UI,Arial,sans-serif;'>
    <strong>DATA SOURCE</strong><br>
    <a href='https://opendata.oizom.com' style='color:#c2410c'>opendata.oizom.com</a><br><br>
    <strong>REFERENCE</strong><br>
    NWS Heat Index Chart<br>
    Rothfusz Regression<br><br>
    <strong>UNITS</strong><br>
    Temperature → °C<br>
    Heat Index → °C (NWS)
    </div>
    """, unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_all_data(device_ids: list, hours: int) -> dict:
    results = {}
    for did in device_ids:
        df = fetch_device_history(did, hours)
        if df.empty or "Temperature" not in df.columns or "Humidity" not in df.columns:
            sample = load_sample_data()
            df = sample.get(did, pd.DataFrame())
        else:
            df = compute_heat_index(df)
        if not df.empty:
            results[did] = df
    return results

if auto_refresh:
    time.sleep(300)
    st.rerun()

device_ids = list(selected_devices.keys())

with st.spinner("Fetching sensor data from Oizom…"):
    data_store = load_all_data(device_ids, selected_hours)

if not data_store:
    data_store = load_sample_data()
    data_store = {k: v for k, v in data_store.items() if k in selected_devices}


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:14px 22px 20px 22px; background:#bfdbfe; border-radius:12px;
            margin-bottom:16px; border:1px solid #93c5fd;'>
  <div style='font-size:12px; color:#c2410c; letter-spacing:2px;
              text-transform:uppercase; margin-bottom:6px; font-weight:700;'>
    Indoor Occupational Heat Stress
  </div>
  <h1 style='margin:0; font-weight:700; font-size:26px; color:#000000;'>
    Unit 1 — Live Sensor Dashboard
  </h1>
  <p style='margin:6px 0 0 0; color:#000000; font-size:13px; font-weight:500;'>
    Surat · Heat Index Analysis
  </p>
</div>
""", unsafe_allow_html=True)

tab_overview, tab_heatmap, tab_trends, tab_hi, tab_devices, tab_about = st.tabs([
    "Overview", "Heat Map", "Trends", "Heat Index", "Devices", "About"
])


def get_latest(did: str):
    df = data_store.get(did)
    if df is None or df.empty:
        return None
    return df.sort_values("Time").iloc[-1].to_dict()

def summary_table() -> pd.DataFrame:
    rows = []
    for did, info in selected_devices.items():
        row = get_latest(did)
        if row is None:
            continue
        hi_f = row.get("HI_F", np.nan)
        rows.append({
            "Device ID":    did,
            "Location":     info["name"],
            "Zone":         info["zone"],
            "Temp (°C)":    round(row.get("Temperature", np.nan), 1),
            "Humidity (%)": round(row.get("Humidity",    np.nan), 1),
            "HI (°C)":      round(f_to_c(hi_f), 1) if not np.isnan(hi_f) else np.nan,
            "Risk":         row.get("HI_Cat", "—"),
        })
    return pd.DataFrame(rows)

_FONT = "Calibri, Segoe UI, Arial, sans-serif"
_TF   = dict(color="#000000", family=_FONT, size=12)
_GRID = "#bfdbfe"

def _apply_theme(fig, height=400, margin=None, legend=None, showlegend=False):
    mg = margin or dict(l=60, r=20, t=40, b=40)
    fig.update_layout(
        paper_bgcolor="#dbeafe", plot_bgcolor="#eff6ff",
        height=height, showlegend=showlegend, margin=mg,
        font=dict(family=_FONT, color="#000000", size=13),
    )
    if legend is not None:
        fig.update_layout(legend=legend)

def _style_axes(fig, xtitle="", ytitle="", xrange=None):
    xkw = dict(gridcolor=_GRID, linecolor="#93c5fd", color="#000000",
               tickfont=_TF, automargin=True)
    if xtitle: xkw["title_text"] = xtitle; xkw["title_font"] = dict(color="#000000", family=_FONT)
    if xrange: xkw["range"] = xrange
    fig.update_xaxes(**xkw)
    ykw = dict(gridcolor=_GRID, linecolor="#93c5fd", color="#000000",
               tickfont=_TF, automargin=True)
    if ytitle: ykw["title_text"] = ytitle; ykw["title_font"] = dict(color="#000000", family=_FONT)
    fig.update_yaxes(**ykw)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    all_latest = [get_latest(d) for d in selected_devices if get_latest(d)]
    if all_latest:
        avg_temp = np.mean([r["Temperature"] for r in all_latest])
        avg_hum  = np.mean([r["Humidity"]    for r in all_latest])
        avg_hi_f = np.mean([r["HI_F"]        for r in all_latest])
        max_hi_f = max(r["HI_F"]             for r in all_latest)
        max_loc  = max(selected_devices.keys(),
                       key=lambda d: get_latest(d)["HI_F"] if get_latest(d) else -999)
        max_cat, max_level = heat_index_category(max_hi_f)

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            lv = "danger" if avg_temp > 35 else "caution" if avg_temp > 30 else "safe"
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Avg. Temperature</div>
              <div class='value v-{lv}'>{avg_temp:.1f}°C</div>
              <div class='sub'>{len(all_latest)} active sensors</div>
            </div>""", unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Avg. Relative Humidity</div>
              <div class='value v-caution'>{avg_hum:.1f}%</div>
              <div class='sub'>Indoor RH — all active sensors</div>
            </div>""", unsafe_allow_html=True)
        with kpi3:
            _, avg_lv = heat_index_category(avg_hi_f)
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Avg. Heat Index</div>
              <div class='value v-{avg_lv}'>{f_to_c(avg_hi_f):.1f}°C</div>
              <div class='sub'>Apparent temperature (Heat Index)</div>
            </div>""", unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Peak Heat Index</div>
              <div class='value v-{max_level}'>{f_to_c(max_hi_f):.1f}°C</div>
              <div class='sub'>{selected_devices[max_loc]["name"]} &nbsp;
                <span class='badge badge-{max_level}'>{max_cat}</span></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("")

    st.markdown("<div class='section-header'>All Sensor Readings — Current</div>",
                unsafe_allow_html=True)
    df_sum = summary_table()
    if not df_sum.empty:
        def style_risk(val):
            m = {
                "Normal":         "color:#14532d; font-weight:600",
                "Caution":        "color:#713f12; font-weight:600",
                "Extreme Caution":"color:#7c2d12; font-weight:600",
                "Danger":         "color:#7f1d1d; font-weight:700",
                "Extreme Danger": "color:#7f1d1d; font-weight:700",
            }
            return m.get(val, "color:#000000")
        try:
            styled = df_sum.style.map(style_risk, subset=["Risk"])
        except AttributeError:
            styled = df_sum.style.applymap(style_risk, subset=["Risk"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("<div class='section-header'>⚠ Active Alerts</div>", unsafe_allow_html=True)
    alert_count = 0
    for did, info in selected_devices.items():
        row = get_latest(did)
        if row is None:
            continue
        hi_f = row.get("HI_F", 0)
        if hi_f >= 91:
            cat, level = heat_index_category(hi_f)
            st.markdown(f"""
            <div class='alert-box'>
              <strong>{info['name']}</strong> ({did}) — Heat Index <strong>{f_to_c(hi_f):.1f}°C</strong>
              &nbsp;<span class='badge badge-{level}'>{cat}</span>
              &nbsp;· Temp {row['Temperature']:.1f}°C · RH {row['Humidity']:.1f}%
            </div>""", unsafe_allow_html=True)
            alert_count += 1
    if alert_count == 0:
        st.success("✓ No devices currently exceeding Caution threshold (33°C Heat Index)")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: HEAT MAP
# ─────────────────────────────────────────────────────────────────────────────
with tab_heatmap:
    st.markdown("<div class='section-header'>Spatial Heat Index Distribution</div>",
                unsafe_allow_html=True)

    hi_vals, names, cats = [], [], []
    for did, info in selected_devices.items():
        row = get_latest(did)
        if row is None:
            continue
        hi_vals.append(row["HI_F"])
        names.append(info["name"])
        cat, _ = heat_index_category(row["HI_F"])
        cats.append(cat)

    if hi_vals:
        hi_c_vals  = [f_to_c(v) for v in hi_vals]
        bar_colors = [CAT_COLORS.get(c, "#cccccc") for c in cats]
        txt_colors = [CAT_TEXT_COLORS.get(c, "#000000") for c in cats]

        fig = go.Figure()
        for i in range(len(names)):
            # Place label inside bar if tall enough, otherwise just above
            val = hi_c_vals[i]
            txt_pos = "inside" if val > f_to_c(86) else "outside"
            txt_color = "#000000" if txt_pos == "outside" else "#000000"
            fig.add_trace(go.Bar(
                x=[names[i]], y=[val],
                marker_color=bar_colors[i],
                marker_line_color="#888888",
                marker_line_width=0.8,
                # ── Only °C value, no category text ──
                text=f"{val:.1f}°C",
                textposition=txt_pos,
                textfont=dict(color=txt_color, size=11, family=_FONT),
                hovertemplate=f"<b>{names[i]}</b><br>Heat Index: {val:.1f}°C"
                              f"<br>Category: {cats[i]}<extra></extra>",
                name=cats[i], showlegend=False,
            ))

        # NWS threshold lines — annotation on LEFT to avoid clashing with legend
        threshold_lines = [
            (f_to_c(80),  "Caution (27°C)",         "#ca8a04"),
            (f_to_c(91),  "Extreme Caution (33°C)", "#ea580c"),
            (f_to_c(103), "Danger (39°C)",           "#dc2626"),
            (f_to_c(125), "Extreme Danger (52°C)",   "#991b1b"),
        ]
        for y_c, lbl, color in threshold_lines:
            fig.add_hline(y=y_c, line_dash="dot", line_color=color,
                          line_width=1.5,
                          annotation_text=lbl,
                          annotation_font_color=color,
                          annotation_font_size=10,
                          annotation_font_family=_FONT,
                          annotation_position="top left",
                          annotation_bgcolor="rgba(255,255,255,0.7)",
                          annotation_borderpad=3)

        # ── Change 1: Legend patch matching image colours ──
        for cat_name, bg, txt in [
            ("Caution",         "#ffff00", "#000000"),
            ("Extreme Caution", "#ffa500", "#000000"),
            ("Danger",          "#ff6600", "#000000"),
            ("Extreme Danger",  "#ff0000", "#000000"),
        ]:
            fig.add_trace(go.Bar(
                x=[None], y=[None],
                name=cat_name,
                marker_color=bg,
                marker_line_color="#888888",
                marker_line_width=0.8,
                showlegend=True,
            ))

        _apply_theme(fig, height=560, margin=dict(l=70, r=160, t=50, b=160),
                     showlegend=True,
                     legend=dict(
                         bgcolor="#eff6ff", bordercolor="#93c5fd",
                         font=dict(color="#000000", size=11, family=_FONT),
                         x=1.01, y=1, xanchor="left",
                         title=dict(text="Risk Level", font=dict(color="#000000", family=_FONT)),
                     ))
        _style_axes(fig, ytitle="Heat Index (°C)")
        fig.update_xaxes(tickangle=-40, tickfont=dict(size=10, family=_FONT, color="#000000"))
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig, use_container_width=True)

    # ── Change 3: Grouped bar chart of Temp & Humidity per device ─────────────
    st.markdown("<div class='section-header'>Temperature & Humidity — All Devices</div>",
                unsafe_allow_html=True)

    bar_names, bar_temps, bar_hums = [], [], []
    for did, info in selected_devices.items():
        row = get_latest(did)
        if row is None:
            continue
        bar_names.append(info["name"])
        bar_temps.append(round(row.get("Temperature", np.nan), 1))
        bar_hums.append(round(row.get("Humidity",    np.nan), 1))

    if bar_names:
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name="Temperature (°C)",
            x=bar_names, y=bar_temps,
            marker_color="#ea580c",
            marker_line_color="#c2410c", marker_line_width=0.8,
            text=[f"{v:.1f}°C" for v in bar_temps],
            textposition="outside",
            textfont=dict(color="#000000", size=10, family=_FONT),
            hovertemplate="<b>%{x}</b><br>Temperature: %{y:.1f}°C<extra></extra>",
        ))
        fig_bar.add_trace(go.Bar(
            name="Relative Humidity (%)",
            x=bar_names, y=bar_hums,
            marker_color="#0284c7",
            marker_line_color="#0369a1", marker_line_width=0.8,
            text=[f"{v:.1f}%" for v in bar_hums],
            textposition="outside",
            textfont=dict(color="#000000", size=10, family=_FONT),
            hovertemplate="<b>%{x}</b><br>Humidity: %{y:.1f}%<extra></extra>",
        ))
        fig_bar.update_layout(barmode="group")
        _apply_theme(fig_bar, height=500, margin=dict(l=70, r=20, t=40, b=160),
                     showlegend=True,
                     legend=dict(bgcolor="#eff6ff", bordercolor="#93c5fd",
                                 font=dict(color="#000000", size=12, family=_FONT),
                                 orientation="h", yanchor="bottom", y=1.02,
                                 xanchor="left", x=0))
        _style_axes(fig_bar, ytitle="Value")
        fig_bar.update_xaxes(tickangle=-40, tickfont=dict(size=10, family=_FONT, color="#000000"))
        fig_bar.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig_bar, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: TRENDS
# ─────────────────────────────────────────────────────────────────────────────
with tab_trends:
    st.markdown("<div class='section-header'>Temperature & Humidity Time Series</div>",
                unsafe_allow_html=True)

    device_choice = st.selectbox(
        "Select sensor",
        options=list(selected_devices.keys()),
        format_func=lambda d: f"{d} — {selected_devices[d]['name']}",
        key="trend_device",
    )
    df_t = data_store.get(device_choice)
    if df_t is not None and not df_t.empty:
        fig3 = make_subplots(rows=3, cols=1, shared_xaxes=True,
                             vertical_spacing=0.06,
                             subplot_titles=("Temperature (°C)",
                                             "Relative Humidity (%)",
                                             "Heat Index (°C)"))
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["Temperature"],
                                  mode="lines", name="Temp",
                                  line=dict(color="#ea580c", width=2)), row=1, col=1)
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["Humidity"],
                                  mode="lines", name="RH",
                                  line=dict(color="#0284c7", width=2)), row=2, col=1)
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["HI_C"],
                                  mode="lines", name="HI",
                                  line=dict(color="#dc2626", width=2)), row=3, col=1)
        for y_f, color in [(80,"#ffff00"),(91,"#ffa500"),(103,"#ff6600"),(125,"#ff0000")]:
            fig3.add_hline(y=f_to_c(y_f), line_dash="dot", line_color=color,
                           line_width=1.5, row=3, col=1)

        _apply_theme(fig3, height=600, margin=dict(l=60, r=20, t=40, b=40))
        _style_axes(fig3)
        fig3.update_layout(
            legend=dict(bgcolor="#eff6ff", bordercolor="#93c5fd",
                        font=dict(color="#000000", family=_FONT)))
        for ann in fig3.layout.annotations:
            ann.font.color  = "#000000"
            ann.font.family = _FONT
        st.plotly_chart(fig3, use_container_width=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Min Temp", f"{df_t['Temperature'].min():.1f}°C")
        c2.metric("Max Temp", f"{df_t['Temperature'].max():.1f}°C")
        c3.metric("Avg Temp", f"{df_t['Temperature'].mean():.1f}°C")
        c4.metric("Max HI",   f"{df_t['HI_C'].max():.1f}°C")
        c5.metric("Avg HI",   f"{df_t['HI_C'].mean():.1f}°C")

    st.markdown("---")
    st.markdown("<div class='section-header'>Multi-Device Comparison — Heat Index Over Time</div>",
                unsafe_allow_html=True)
    fig4 = go.Figure()
    palette = px.colors.qualitative.Dark24
    for i, (did, info) in enumerate(selected_devices.items()):
        df = data_store.get(did)
        if df is None or df.empty:
            continue
        fig4.add_trace(go.Scatter(
            x=df["Time"], y=df["HI_C"],
            mode="lines", name=info["name"],
            line=dict(color=palette[i % len(palette)], width=1.5),
        ))
    _apply_theme(fig4, height=400, margin=dict(l=60, r=20, t=20, b=40),
                 showlegend=True,
                 legend=dict(bgcolor="#eff6ff", bordercolor="#93c5fd",
                             font=dict(color="#000000", size=11, family=_FONT)))
    _style_axes(fig4, ytitle="Heat Index (°C)")
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: HEAT INDEX REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
with tab_hi:
    st.markdown("<div class='section-header'>NWS Heat Index Reference Chart</div>",
                unsafe_allow_html=True)

    # ── Change 1 & 2: Colours match image + value labels inside cells ─────────
    rh_range     = list(range(40, 105, 5))
    temp_f_range = list(range(80, 112, 2))
    temp_c_range = [round(f_to_c(t), 1) for t in temp_f_range]
    z_matrix     = [[round(f_to_c(heat_index_fahrenheit(float(T), float(RH))), 1)
                     for RH in rh_range] for T in temp_f_range]

    # Build colour matrix matching image exactly
    def hi_cell_color(hi_c):
        hi_f = hi_c * 9/5 + 32
        if hi_f < 80:   return "#ffffff"   # white / no stress
        elif hi_f < 91: return "#ffff00"   # yellow — Caution
        elif hi_f < 103:return "#ffa500"   # orange — Extreme Caution
        elif hi_f < 125:return "#ff0000"   # red    — Danger / Extreme Danger
        else:           return "#cc0000"   # dark red

    # Custom discrete colour per cell using annotation trick
    fig5 = go.Figure()

    # Background heatmap with custom colourscale
    fig5.add_trace(go.Heatmap(
        z=z_matrix,
        x=[f"{r}%" for r in rh_range],
        y=[f"{tc}°C" for tc in temp_c_range],
        colorscale=[
            [0.00, "#ffffff"],
            [0.20, "#ffff00"],
            [0.50, "#ffa500"],
            [0.75, "#ff0000"],
            [1.00, "#cc0000"],
        ],
        zmin=f_to_c(70), zmax=f_to_c(130),
        showscale=True,
        colorbar=dict(
            title=dict(text="HI (°C)",
                       font=dict(family=_FONT, color="#000000")),
            tickfont=dict(family=_FONT, color="#000000"),
            tickvals=[f_to_c(v) for v in [75, 80, 91, 103, 115, 125]],
            ticktext=["<27°C<br>Normal",
                      "27°C<br>Caution",
                      "33°C<br>Ext. Caution",
                      "39°C<br>Danger",
                      "46°C",
                      "52°C<br>Ext. Danger"],
        ),
        # ── Change 2: Show value labels in each cell ──
        text=[[str(v) for v in row] for row in z_matrix],
        texttemplate="%{text}",
        textfont=dict(size=9, family=_FONT, color="#000000"),
        hovertemplate="Temp: %{y}<br>RH: %{x}<br>HI: %{z}°C<extra></extra>",
    ))

    _apply_theme(fig5, height=580, margin=dict(l=20, r=120, t=30, b=40))
    _style_axes(fig5, xtitle="Relative Humidity (%)", ytitle="Air Temperature (°C)")
    fig5.update_layout(plot_bgcolor="#ffffff", paper_bgcolor="#dbeafe")
    st.plotly_chart(fig5, use_container_width=True)

    # Colour legend matching image exactly
    st.markdown("""
    <div style='display:flex; gap:24px; flex-wrap:wrap; padding:10px 0 16px 0; align-items:center;'>
      <div style='display:flex;align-items:center;gap:6px;'>
        <div style='width:28px;height:20px;background:#ffff00;border:1px solid #ca8a04;'></div>
        <span style='font-size:12px;color:#000000;font-weight:600;'>Caution</span>
      </div>
      <div style='display:flex;align-items:center;gap:6px;'>
        <div style='width:28px;height:20px;background:#ffa500;border:1px solid #ea580c;'></div>
        <span style='font-size:12px;color:#000000;font-weight:600;'>Extreme Caution</span>
      </div>
      <div style='display:flex;align-items:center;gap:6px;'>
        <div style='width:28px;height:20px;background:#ff6600;border:1px solid #dc2626;'></div>
        <span style='font-size:12px;color:#000000;font-weight:600;'>Danger</span>
      </div>
      <div style='display:flex;align-items:center;gap:6px;'>
        <div style='width:28px;height:20px;background:#ff0000;border:1px solid #991b1b;'></div>
        <span style='font-size:12px;color:#000000;font-weight:600;'>Extreme Danger</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Risk Levels</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    categories = [
        ("< 27°C",  "Normal",          "safe",    "No heat stress"),
        ("27–32°C", "Caution",         "caution", "Fatigue possible with prolonged exposure"),
        ("33–39°C", "Extreme Caution", "danger",  "Heat cramps / exhaustion possible"),
        ("40–51°C", "Danger",          "extreme", "Heat cramps / exhaustion likely; stroke possible"),
        ("≥ 52°C",  "Extreme Danger",  "extreme", "Heat stroke highly likely"),
    ]
    for i, (rng, name, level, desc) in enumerate(categories):
        target = col1 if i % 2 == 0 else col2
        with target:
            st.markdown(f"""
            <div class='metric-card' style='margin-bottom:8px'>
              <span class='badge badge-{level}'>{name}</span>
              <span style='margin-left:8px;font-size:12px;color:#000000;font-weight:600'>{rng}</span>
              <div style='font-size:12px;color:#000000;margin-top:6px'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.info("💡 **Note:** Heat Index is computed in °F per the NWS Rothfusz regression "
            "(with low-RH and high-RH adjustments), then converted to °C for display.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: DEVICES
# ─────────────────────────────────────────────────────────────────────────────
with tab_devices:
    st.markdown("<div class='section-header'>Sensor Network — Unit 1</div>",
                unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (did, info) in enumerate(DEVICES.items()):
        row = get_latest(did)
        with cols[i % 3]:
            if row:
                hi_f = row.get("HI_F", 0)
                cat, lev = heat_index_category(hi_f)
                temp_c   = row.get("Temperature", 0)
                hum      = row.get("Humidity", 0)
                st.markdown(f"""
                <div class='metric-card'>
                  <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                    <div>
                      <div class='label'>{did}</div>
                      <div style='font-size:13px;font-weight:700;color:#000000;
                                  margin:2px 0 4px 0'>{info['name']}</div>
                      <span style='font-size:10px;color:#000000;font-weight:600;
                                   background:#e9ecef;padding:2px 6px;
                                   border-radius:3px'>{info['zone']}</span>
                    </div>
                    <span class='badge badge-{lev}'>{cat}</span>
                  </div>
                  <div style='display:grid;grid-template-columns:1fr 1fr 1fr;
                              gap:8px;margin-top:12px;'>
                    <div>
                      <div class='label'>Temp</div>
                      <div style='font-size:16px;color:#c2410c;font-weight:600'>{temp_c:.1f}°C</div>
                    </div>
                    <div>
                      <div class='label'>RH</div>
                      <div style='font-size:16px;color:#0369a1;font-weight:600'>{hum:.1f}%</div>
                    </div>
                    <div>
                      <div class='label'>HI</div>
                      <div style='font-size:16px;color:#b91c1c;font-weight:600'>{f_to_c(hi_f):.1f}°C</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='metric-card' style='opacity:0.6'>
                  <div class='label'>{did}</div>
                  <div style='font-size:13px;color:#000000;font-weight:600'>{info['name']}</div>
                  <div style='font-size:11px;color:#000000;margin-top:8px'>No data</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-header'>Raw Data Export</div>", unsafe_allow_html=True)
    export_device = st.selectbox(
        "Device to export", list(selected_devices.keys()),
        format_func=lambda d: f"{d} — {selected_devices[d]['name']}",
        key="export_sel",
    )
    df_exp = data_store.get(export_device)
    if df_exp is not None and not df_exp.empty:
        csv = df_exp.to_csv(index=False).encode("utf-8")
        st.download_button(
            f"⬇ Download {export_device} CSV", data=csv,
            file_name=f"heat_{export_device}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 6: ABOUT
# ─────────────────────────────────────────────────────────────────────────────
with tab_about:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
## Assessing Indoor Occupational Heat Stress
### A Case Study of Textile Processing MSMEs in Surat

**WRI Working Paper** · *Draft in Progress*

---

### Research Objectives

1. Assess indoor thermal environments across four representative textile processing MSME unit types in Surat
2. Examine the influence of building design, layout, and operational processes on heat accumulation
3. Understand worker perceptions and adaptive responses through qualitative assessments
4. Develop evidence-based recommendations for improving indoor thermal conditions

---

### About This Dashboard

This real-time dashboard displays environmental sensor data from **Unit 1**, one of four study units in the WRI occupational heat stress research.

Sensors are deployed across the facility — from stenter machines and jet dyeing areas to circulation zones and folding tables — capturing spatial and temporal variation in indoor heat conditions.

**Heat Index** is computed using the **NWS Rothfusz regression** formula (with low-RH and high-RH adjustments), applied after converting sensor temperatures from °C to °F, then converted back to °C for display.

### Study Unit Typologies

| # | Type | Description |
|---|------|-------------|
| 1 | High-ventilation, high-ceiling | Newly constructed, open space |
| 2 | Traditional ground-floor shed | Dense cluster |
| 3 | Multi-floor congested building | Old construction, restricted airflow |
| 4 | Retrofitted mixed structure | Old-new with restricted airflow |

---

### Authors

Pooja Yadav · Mehul Patel · Abhijit Namboothiri · Ambar Singh · *WRI India*

---

### Data Source

Sensor data via [Oizom OpenData API](https://opendata.oizom.com/)
Monitoring period: 12 months (continuous) · Interval: Hourly readings
        """)

    with col2:
        st.markdown("""
### Risk Reference (°C)

| Heat Index | Category |
|------------|----------|
| < 27°C     | Normal   |
| 27–32°C    | Caution  |
| 33–39°C    | Extreme Caution |
| 40–51°C    | Danger   |
| ≥ 52°C     | Extreme Danger |

---

### Key References

- ILO (2019). *Working on a Warmer Planet*
- Foster et al. (2021). *Heat and human work capacity*
- Hardik Parmar et al. (2023). Foundry heat stress
- OSHWC 2020, Section 21
- ISHRAE thermal comfort standards

---

### Contact

WRI India · [wri.org/india](https://www.wri.org/india)

Data: [opendata.oizom.com](https://opendata.oizom.com)
        """)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px;color:#000000;text-align:center;font-weight:500'>
    © World Resources Institute · Dashboard for research purposes only ·
    Data: Oizom OpenData API · Heat Index: NWS Rothfusz Regression
    </div>
    """, unsafe_allow_html=True)
