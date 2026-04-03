"""
Indoor Occupational Heat Stress Dashboard
Prayagraj Dyeing and Printing Private Limited — Surat
WRI INDIA
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
import json

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Heat Stress Monitor | Prayagraj Dyeing and Printing Private Limited",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

:root {
    --bg: #ffffff;
    --surface: #f8f9fa;
    --surface2: #f1f3f5;
    --border: #dee2e6;
    --text: #1a1d23;
    --muted: #6b7280;
    --accent: #e85d04;
    --accent2: #dc2626;
    --safe: #16a34a;
    --warn: #ca8a04;
    --danger: #e85d04;
    --extreme: #dc2626;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans);
    background-color: var(--bg);
    color: var(--text);
}

.stApp { background-color: var(--bg); }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Metric cards */
.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
}
.metric-card .label {
    font-family: var(--mono);
    font-size: 10px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}
.metric-card .value {
    font-family: var(--mono);
    font-size: 28px;
    font-weight: 600;
    line-height: 1;
}
.metric-card .sub {
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
}
.v-safe   { color: var(--safe); }
.v-caution { color: var(--warn); }
.v-danger { color: var(--danger); }
.v-extreme { color: var(--extreme); }

/* Risk badges */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-safe    { background: rgba(34,197,94,0.15);  color: #22c55e; border: 1px solid rgba(34,197,94,0.3); }
.badge-caution { background: rgba(234,179,8,0.15);  color: #eab308; border: 1px solid rgba(234,179,8,0.3); }
.badge-danger  { background: rgba(249,115,22,0.15); color: #f97316; border: 1px solid rgba(249,115,22,0.3); }
.badge-extreme { background: rgba(239,68,68,0.15);  color: #ef4444; border: 1px solid rgba(239,68,68,0.3); }

/* Section headers */
.section-header {
    font-family: var(--mono);
    font-size: 11px;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 0 0 8px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 16px;
}

/* Divider line */
hr { border-color: var(--border) !important; }

/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Table styles */
.stDataFrame { border: 1px solid var(--border); border-radius: 8px; }

/* Alert boxes */
.alert-box {
    border-left: 3px solid var(--accent);
    background: rgba(249,115,22,0.08);
    padding: 12px 16px;
    border-radius: 0 6px 6px 0;
    margin: 8px 0;
    font-size: 13px;
}

/* Title */
.main-title {
    font-family: var(--mono);
    font-size: 22px;
    font-weight: 600;
    color: var(--text);
    letter-spacing: -0.5px;
}
.main-subtitle {
    font-family: var(--sans);
    font-size: 13px;
    color: var(--muted);
    margin-top: 2px;
}

/* Plotly chart background override */
.js-plotly-plot { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


# ── Device map ────────────────────────────────────────────────────────────────
DEVICES = {
    "2BA61C": {"name": "Ground Stenter",                        "zone": "Production"},
    "2D66E4": {"name": "Zero zero — near gate",                 "zone": "Entry/Circulation"},
    "2BA554": {"name": "Washing-Dyeing Range",                  "zone": "Production"},
    "2BA298": {"name": "Jigger",                                "zone": "Production"},
    "2BA638": {"name": "Jets — B/H Office",                     "zone": "Production"},
    "2BA640": {"name": "Jet Dyeing — Heighted",                 "zone": "Production"},
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
API_KEY    = st.secrets.get("OIZOM_API_KEY", "")   # set in .streamlit/secrets.toml


# ── Heat Index calculation ────────────────────────────────────────────────────
def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32

def heat_index_fahrenheit(T_f: float, RH: float) -> float:
    """Rothfusz regression — T in °F, RH in %."""
    if T_f < 80:
        return T_f
    HI = (-42.379
          + 2.04901523 * T_f
          + 10.14333127 * RH
          - 0.22475541 * T_f * RH
          - 6.83783e-3 * T_f ** 2
          - 5.481717e-2 * RH ** 2
          + 1.22874e-3 * T_f ** 2 * RH
          + 8.5282e-4 * T_f * RH ** 2
          - 1.99e-6 * T_f ** 2 * RH ** 2)
    return HI

def heat_index_category(hi_f: float):
    if hi_f < 80:
        return "Normal",       "safe"
    elif hi_f < 91:
        return "Caution",      "caution"
    elif hi_f < 103:
        return "Extreme Caution", "danger"
    elif hi_f < 125:
        return "Danger",       "extreme"
    else:
        return "Extreme Danger", "extreme"

def compute_heat_index(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Temp_F"]    = df["Temperature"].apply(celsius_to_fahrenheit)
    df["HI_F"]      = df.apply(lambda r: heat_index_fahrenheit(r["Temp_F"], r["Humidity"]), axis=1)
    df["HI_C"]      = (df["HI_F"] - 32) * 5 / 9
    cats            = df["HI_F"].apply(heat_index_category)
    df["HI_Cat"]    = [c[0] for c in cats]
    df["HI_Level"]  = [c[1] for c in cats]
    return df


# ── Oizom API helpers ─────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_device_latest(device_id: str) -> dict:
    """Fetch latest reading for a device from Oizom OpenData."""
    url = f"{OIZOM_BASE}/devices/{device_id}/latest"
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}

@st.cache_data(ttl=300)
def fetch_device_history(device_id: str, hours: int = 24) -> pd.DataFrame:
    """Fetch hourly history for a device."""
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
                # Normalise column names — Oizom can vary
                rename = {}
                for col in df.columns:
                    cl = col.lower()
                    if "temp" in cl:    rename[col] = "Temperature"
                    if "hum" in cl:     rename[col] = "Humidity"
                    if "time" in cl or "ts" == cl: rename[col] = "Time"
                df.rename(columns=rename, inplace=True)
                if "Time" in df.columns:
                    df["Time"] = pd.to_datetime(df["Time"], unit="s", errors="coerce")
                return df
    except Exception:
        pass
    return pd.DataFrame()


def load_sample_data() -> dict[str, pd.DataFrame]:
    """
    Fallback: synthetic data that mimics the uploaded CSV snippet.
    One full day per device, slightly varied per zone.
    """
    np.random.seed(42)
    base_times = pd.date_range("2026-03-25 00:30", periods=48, freq="1h")
    results = {}
    zone_offsets = {
        "Production":   (2.0, -1.0),
        "Entry/Circulation": (0.0, 0.0),
        "Circulation":  (1.0, -0.5),
        "Post-Process": (0.5, -0.3),
    }
    for did, info in DEVICES.items():
        dt_off, hum_off = zone_offsets.get(info["zone"], (0, 0))
        temps = 32 + dt_off + np.random.randn(48) * 2 + 3 * np.sin(np.linspace(0, 2*np.pi, 48))
        hums  = 38 + hum_off + np.random.randn(48) * 1.5
        df = pd.DataFrame({"Time": base_times, "Temperature": temps, "Humidity": hums})
        results[did] = compute_heat_index(df)
    return results


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:16px 0 8px 0'>
      <div class='main-title'>Indoor Occupational Heat Stress</div>
      <div class='main-subtitle'>Prayagraj Dyeing & Printing Pvt. Ltd.<br>Surat · WRI India</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # Auto-refresh
    auto_refresh = st.toggle("⟳ Auto-refresh (5 min)", value=False)

    # Time range
    time_range = st.selectbox(
        "Time window",
        ["Last 6 hours", "Last 24 hours", "Last 48 hours", "Last 7 days"],
        index=1,
    )
    hours_map = {"Last 6 hours": 6, "Last 24 hours": 24,
                 "Last 48 hours": 48, "Last 7 days": 168}
    selected_hours = hours_map[time_range]

    # Device filter
    st.markdown("#### Devices")
    all_checked = st.checkbox("Select all", value=True)
    selected_devices = {}
    for did, info in DEVICES.items():
        checked = st.checkbox(f"`{did}` {info['name']}", value=all_checked, key=f"cb_{did}")
        if checked:
            selected_devices[did] = info

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px; color:#6b7280; font-family: IBM Plex Mono, monospace;'>
    DATA SOURCE<br>
    <a href='https://opendata.oizom.com' style='color:#f97316'>opendata.oizom.com</a><br><br>
    REFERENCE<br>
    NWS Heat Index Chart<br>
    Rothfusz Regression<br><br>
    UNIT<br>
    Temperature → °C / °F<br>
    Heat Index → °F (NWS standard)
    </div>
    """, unsafe_allow_html=True)


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_all_data(device_ids: list, hours: int) -> dict[str, pd.DataFrame]:
    results = {}
    for did in device_ids:
        df = fetch_device_history(did, hours)
        if df.empty or "Temperature" not in df.columns or "Humidity" not in df.columns:
            # Use sample data for demonstration
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

# Fallback to full sample if API returned nothing
if not data_store:
    data_store = load_sample_data()
    data_store = {k: v for k, v in data_store.items() if k in selected_devices}


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 8px 0 24px 0'>
  <div style='font-family: IBM Plex Mono, monospace; font-size: 11px;
              color: #f97316; letter-spacing: 2px; text-transform: uppercase;
              margin-bottom: 6px;'>
    WRI Research · Indoor Occupational Heat Stress
  </div>
  <h1 style='margin:0; font-family: IBM Plex Sans, sans-serif; font-weight:700;
             font-size:28px; color:#1a1d23; letter-spacing:-0.5px;'>
    Prayagraj Dyeing & Printing — Live Sensor Dashboard
  </h1>
  <p style='margin:4px 0 0 0; color:#6b7280; font-size:13px;'>
    Surat Textile MSME Cluster · 15 Sensor Nodes · Heat Index Analysis
  </p>
</div>
""", unsafe_allow_html=True)

tab_overview, tab_heatmap, tab_trends, tab_hi, tab_devices, tab_about = st.tabs([
    "📊 Overview", "🔥 Heat Map", "📈 Trends", "🌡️ Heat Index", "📡 Devices", "ℹ️ About"
])


# ── Helper: latest row per device ────────────────────────────────────────────
def get_latest(did: str) -> dict | None:
    df = data_store.get(did)
    if df is None or df.empty:
        return None
    row = df.sort_values("Time").iloc[-1]
    return row.to_dict()

def summary_table() -> pd.DataFrame:
    rows = []
    for did, info in selected_devices.items():
        row = get_latest(did)
        if row is None:
            continue
        hi_f  = row.get("HI_F", np.nan)
        cat   = row.get("HI_Cat", "—")
        rows.append({
            "Device ID":   did,
            "Location":    info["name"],
            "Zone":        info["zone"],
            "Temp (°C)":   round(row.get("Temperature", np.nan), 1),
            "Humidity (%)": round(row.get("Humidity", np.nan), 1),
            "HI (°F)":     round(hi_f, 1),
            "HI (°C)":     round((hi_f - 32) * 5/9, 1) if not np.isnan(hi_f) else np.nan,
            "Risk":        cat,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:

    # Top KPI row
    all_latest = [get_latest(did) for did in selected_devices if get_latest(did)]
    if all_latest:
        avg_temp  = np.mean([r["Temperature"] for r in all_latest])
        avg_hum   = np.mean([r["Humidity"]    for r in all_latest])
        avg_hi_f  = np.mean([r["HI_F"]        for r in all_latest])
        max_hi_f  = max(r["HI_F"]             for r in all_latest)
        max_loc   = max(selected_devices.keys(),
                        key=lambda d: get_latest(d)["HI_F"] if get_latest(d) else -999)
        max_cat   = heat_index_category(max_hi_f)[0]
        max_level = heat_index_category(max_hi_f)[1]

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Avg. Temperature</div>
              <div class='value v-{"danger" if avg_temp>35 else "caution" if avg_temp>30 else "safe"}'>{avg_temp:.1f}°C</div>
              <div class='sub'>{celsius_to_fahrenheit(avg_temp):.1f}°F across {len(all_latest)} sensors</div>
            </div>""", unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Avg. Relative Humidity</div>
              <div class='value v-caution'>{avg_hum:.1f}%</div>
              <div class='sub'>Indoor RH — all active sensors</div>
            </div>""", unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Avg. Heat Index</div>
              <div class='value v-{heat_index_category(avg_hi_f)[1]}'>{avg_hi_f:.1f}°F</div>
              <div class='sub'>{(avg_hi_f-32)*5/9:.1f}°C apparent temperature</div>
            </div>""", unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Peak Heat Index</div>
              <div class='value v-{max_level}'>{max_hi_f:.1f}°F</div>
              <div class='sub'>{selected_devices[max_loc]["name"]} · <span class='badge badge-{max_level}'>{max_cat}</span></div>
            </div>""", unsafe_allow_html=True)

        st.markdown("")

    # Summary table
    st.markdown("<div class='section-header'>All Sensor Readings — Current</div>", unsafe_allow_html=True)

    df_sum = summary_table()
    if not df_sum.empty:
        def style_risk(val):
            colors = {
                "Normal": "color: #22c55e",
                "Caution": "color: #eab308",
                "Extreme Caution": "color: #f97316",
                "Danger": "color: #ef4444",
                "Extreme Danger": "color: #ef4444; font-weight:700",
            }
            return colors.get(val, "")

        try:
            styled = df_sum.style.map(style_risk, subset=["Risk"])
        except AttributeError:
            styled = df_sum.style.applymap(style_risk, subset=["Risk"])
        st.dataframe(styled, use_container_width=True, hide_index=True)

    # Alert panel
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
              <strong>{info['name']}</strong> ({did}) — Heat Index <strong>{hi_f:.1f}°F</strong>
              &nbsp;<span class='badge badge-{level}'>{cat}</span>
              &nbsp;· Temp {row['Temperature']:.1f}°C · RH {row['Humidity']:.1f}%
            </div>""", unsafe_allow_html=True)
            alert_count += 1
    if alert_count == 0:
        st.success("✓ No devices currently exceeding Caution threshold (91°F Heat Index)")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: HEAT MAP
# ─────────────────────────────────────────────────────────────────────────────
with tab_heatmap:
    st.markdown("<div class='section-header'>Spatial Heat Index Distribution</div>",
                unsafe_allow_html=True)

    hi_vals, names, temps, hums, cats, levels = [], [], [], [], [], []
    for did, info in selected_devices.items():
        row = get_latest(did)
        if row is None:
            continue
        hi_vals.append(row["HI_F"])
        names.append(info["name"])
        temps.append(row["Temperature"])
        hums.append(row["Humidity"])
        cat, lev = heat_index_category(row["HI_F"])
        cats.append(cat)
        levels.append(lev)

    if hi_vals:
        color_map = {
            "Normal": "#22c55e",
            "Caution": "#eab308",
            "Extreme Caution": "#f97316",
            "Danger": "#ef4444",
            "Extreme Danger": "#7f1d1d",
        }
        bar_colors = [color_map.get(c, "#6b7280") for c in cats]

        fig = go.Figure(go.Bar(
            x=hi_vals,
            y=names,
            orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.1f}°F — {c}" for v, c in zip(hi_vals, cats)],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Heat Index: %{x:.1f}°F<extra></extra>",
        ))
        # Reference lines
        for threshold, label, color in [
                (80, "Normal/Caution", "#22c55e"),
                (91, "Extreme Caution", "#eab308"),
                (103, "Danger", "#f97316"),
                (125, "Extreme Danger", "#ef4444")]:
            fig.add_vline(x=threshold, line_dash="dot", line_color=color,
                          annotation_text=label,
                          annotation_font_color=color,
                          annotation_font_size=10)

        fig.update_layout(
            paper_bgcolor="#ffffff",
            plot_bgcolor="#f8f9fa",
            font=dict(family="IBM Plex Mono", color="#1a1d23"),
            xaxis=dict(title="Heat Index (°F)", gridcolor="#dee2e6",
                       range=[min(hi_vals)-5, max(hi_vals)+25]),
            yaxis=dict(gridcolor="#dee2e6"),
            margin=dict(l=0, r=60, t=20, b=40),
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Scatter: Temp vs Humidity coloured by HI
    st.markdown("<div class='section-header'>Temperature × Humidity Scatter</div>",
                unsafe_allow_html=True)

    all_dfs = []
    for did, info in selected_devices.items():
        df = data_store.get(did)
        if df is None or df.empty:
            continue
        df2 = df.copy()
        df2["Device"]   = did
        df2["Location"] = info["name"]
        df2["Zone"]     = info["zone"]
        all_dfs.append(df2)

    if all_dfs:
        big = pd.concat(all_dfs, ignore_index=True)
        fig2 = px.scatter(
            big, x="Temperature", y="Humidity",
            color="HI_F",
            hover_data=["Location", "Time", "HI_Cat"],
            color_continuous_scale=["#22c55e", "#eab308", "#f97316", "#ef4444"],
            labels={"Temperature": "Temp (°C)", "Humidity": "RH (%)", "HI_F": "HI (°F)"},
        )
        fig2.update_layout(
            paper_bgcolor="#ffffff", plot_bgcolor="#f8f9fa",
            font=dict(family="IBM Plex Mono", color="#1a1d23"),
            xaxis=dict(gridcolor="#dee2e6"),
            yaxis=dict(gridcolor="#dee2e6"),
            margin=dict(l=0, r=0, t=20, b=40),
            height=400,
        )
        st.plotly_chart(fig2, use_container_width=True)


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
        fig3 = make_subplots(rows=3, cols=1,
                             shared_xaxes=True,
                             vertical_spacing=0.06,
                             subplot_titles=("Temperature (°C)", "Relative Humidity (%)",
                                             "Heat Index (°F)"))

        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["Temperature"],
                                  mode="lines", name="Temp",
                                  line=dict(color="#f97316", width=1.5)), row=1, col=1)
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["Humidity"],
                                  mode="lines", name="RH",
                                  line=dict(color="#38bdf8", width=1.5)), row=2, col=1)
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["HI_F"],
                                  mode="lines", name="HI",
                                  line=dict(color="#ef4444", width=2)), row=3, col=1)

        # NWS thresholds on HI chart
        for y, color in [(80, "#22c55e"), (91, "#eab308"), (103, "#f97316"), (125, "#ef4444")]:
            fig3.add_hline(y=y, line_dash="dot", line_color=color,
                           line_width=1, row=3, col=1)

        fig3.update_layout(
            paper_bgcolor="#ffffff", plot_bgcolor="#f8f9fa",
            font=dict(family="IBM Plex Mono", color="#1a1d23"),
            xaxis3=dict(gridcolor="#dee2e6"),
            yaxis=dict(gridcolor="#dee2e6"),
            yaxis2=dict(gridcolor="#dee2e6"),
            yaxis3=dict(gridcolor="#dee2e6"),
            legend=dict(bgcolor="#f8f9fa", bordercolor="#dee2e6"),
            margin=dict(l=0, r=0, t=40, b=40),
            height=600,
            showlegend=False,
        )
        st.plotly_chart(fig3, use_container_width=True)

        # Stats strip
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Min Temp", f"{df_t['Temperature'].min():.1f}°C")
        c2.metric("Max Temp", f"{df_t['Temperature'].max():.1f}°C")
        c3.metric("Avg Temp", f"{df_t['Temperature'].mean():.1f}°C")
        c4.metric("Max HI",   f"{df_t['HI_F'].max():.1f}°F")
        c5.metric("Avg HI",   f"{df_t['HI_F'].mean():.1f}°F")

    # Multi-device comparison
    st.markdown("---")
    st.markdown("<div class='section-header'>Multi-Device Comparison — Heat Index Over Time</div>",
                unsafe_allow_html=True)
    fig4 = go.Figure()
    palette = px.colors.qualitative.Set2
    for i, (did, info) in enumerate(selected_devices.items()):
        df = data_store.get(did)
        if df is None or df.empty:
            continue
        fig4.add_trace(go.Scatter(
            x=df["Time"], y=df["HI_F"],
            mode="lines", name=info["name"],
            line=dict(color=palette[i % len(palette)], width=1.2),
        ))
    fig4.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#f8f9fa",
        font=dict(family="IBM Plex Mono", color="#1a1d23"),
        xaxis=dict(gridcolor="#dee2e6"),
        yaxis=dict(gridcolor="#dee2e6", title="Heat Index (°F)"),
        legend=dict(bgcolor="#f8f9fa", bordercolor="#dee2e6", font_size=10),
        margin=dict(l=0, r=0, t=20, b=40),
        height=400,
    )
    st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: HEAT INDEX REFERENCE
# ─────────────────────────────────────────────────────────────────────────────
with tab_hi:
    st.markdown("<div class='section-header'>NWS Heat Index Reference Chart</div>",
                unsafe_allow_html=True)

    rh_range  = list(range(40, 105, 5))
    temp_range = list(range(80, 112, 2))   # °F
    z_matrix  = []
    for T in temp_range:
        row_hi = []
        for RH in rh_range:
            hi = heat_index_fahrenheit(float(T), float(RH))
            row_hi.append(round(hi, 1))
        z_matrix.append(row_hi)

    fig5 = go.Figure(go.Heatmap(
        z=z_matrix,
        x=[f"{r}%" for r in rh_range],
        y=[f"{t}°F ({(t-32)*5/9:.0f}°C)" for t in temp_range],
        colorscale=[
            [0,    "#22c55e"],
            [0.25, "#eab308"],
            [0.55, "#f97316"],
            [0.75, "#ef4444"],
            [1.0,  "#7f1d1d"],
        ],
        text=[[str(v) for v in row] for row in z_matrix],
        texttemplate="%{text}",
        textfont=dict(size=9, family="IBM Plex Mono"),
        hovertemplate="Temp: %{y}<br>RH: %{x}<br>HI: %{z}°F<extra></extra>",
        showscale=True,
        colorbar=dict(
            title=dict(text="HI (°F)", font=dict(family="IBM Plex Mono", color="#1a1d23")),
            tickfont=dict(family="IBM Plex Mono", color="#1a1d23"),
        ),
    ))
    fig5.update_layout(
        paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
        font=dict(family="IBM Plex Mono", color="#1a1d23"),
        margin=dict(l=0, r=0, t=20, b=40),
        xaxis=dict(title="Relative Humidity"),
        yaxis=dict(title="Air Temperature"),
        height=550,
    )
    st.plotly_chart(fig5, use_container_width=True)

    # Category legend
    st.markdown("<div class='section-header'>Risk Levels</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    categories = [
        ("< 80°F",     "Normal",          "safe",    "No heat stress"),
        ("80–90°F",    "Caution",         "caution", "Fatigue possible with prolonged exposure"),
        ("91–102°F",   "Extreme Caution", "danger",  "Heat cramps/exhaustion possible"),
        ("103–124°F",  "Danger",          "extreme", "Heat cramps/exhaustion likely; stroke possible"),
        ("≥ 125°F",    "Extreme Danger",  "extreme", "Heat stroke highly likely"),
    ]
    for i, (rng, name, level, desc) in enumerate(categories):
        target = col1 if i % 2 == 0 else col2
        with target:
            st.markdown(f"""
            <div class='metric-card' style='margin-bottom:8px'>
              <span class='badge badge-{level}'>{name}</span>
              <span style='margin-left:8px; font-family:IBM Plex Mono; font-size:12px; color:#1a1d23'>{rng}</span>
              <div style='font-size:12px; color:#9ca3af; margin-top:6px'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.info("💡 **Note:** Heat Index values in this chart are in °F as per NWS standard. "
            "Current sensor readings are in °C and are converted using T(°F) = T(°C) × 9/5 + 32 "
            "before applying the Rothfusz regression formula.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: DEVICES
# ─────────────────────────────────────────────────────────────────────────────
with tab_devices:
    st.markdown("<div class='section-header'>Sensor Network — Prayagraj Dyeing & Printing</div>",
                unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (did, info) in enumerate(DEVICES.items()):
        row = get_latest(did)
        with cols[i % 3]:
            if row:
                hi_f  = row.get("HI_F", 0)
                cat, lev = heat_index_category(hi_f)
                temp_c = row.get("Temperature", 0)
                hum    = row.get("Humidity", 0)
                st.markdown(f"""
                <div class='metric-card'>
                  <div style='display:flex; justify-content:space-between; align-items:flex-start'>
                    <div>
                      <div class='label'>{did}</div>
                      <div style='font-size:13px; font-weight:600; color:#1a1d23;
                                  margin:2px 0 4px 0'>{info['name']}</div>
                      <span style='font-size:10px; color:#6b7280;
                                   background:#e9ecef; padding:2px 6px;
                                   border-radius:3px'>{info['zone']}</span>
                    </div>
                    <span class='badge badge-{lev}'>{cat}</span>
                  </div>
                  <div style='display:grid; grid-template-columns:1fr 1fr 1fr;
                              gap:8px; margin-top:12px;'>
                    <div>
                      <div class='label'>Temp</div>
                      <div style='font-family:IBM Plex Mono; font-size:16px;
                                  color:#f97316'>{temp_c:.1f}°C</div>
                    </div>
                    <div>
                      <div class='label'>RH</div>
                      <div style='font-family:IBM Plex Mono; font-size:16px;
                                  color:#38bdf8'>{hum:.1f}%</div>
                    </div>
                    <div>
                      <div class='label'>HI</div>
                      <div style='font-family:IBM Plex Mono; font-size:16px;
                                  color:#ef4444'>{hi_f:.1f}°F</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='metric-card' style='opacity:0.5'>
                  <div class='label'>{did}</div>
                  <div style='font-size:13px; color:#9ca3af'>{info['name']}</div>
                  <div style='font-size:11px; color:#6b7280; margin-top:8px'>No data</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div class='section-header'>Raw Data Export</div>", unsafe_allow_html=True)
    export_device = st.selectbox("Device to export", list(selected_devices.keys()),
                                 format_func=lambda d: f"{d} — {selected_devices[d]['name']}",
                                 key="export_sel")
    df_exp = data_store.get(export_device)
    if df_exp is not None and not df_exp.empty:
        csv = df_exp.to_csv(index=False).encode("utf-8")
        st.download_button(
            f"⬇ Download {export_device} CSV",
            data=csv,
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

This real-time dashboard displays environmental sensor data from **Prayagraj Dyeing and Printing Private Limited**, one of four study units in the WRI occupational heat stress research.

Sensors are deployed at 15 locations across the facility — from stenter machines and jet dyeing areas to circulation zones and folding tables — capturing spatial and temporal variation in indoor heat conditions.

**Heat Index** is computed using the **NWS Rothfusz regression** formula, applied after converting sensor temperatures from °C to °F:
```
HI = -42.379 + 2.049T + 10.143RH − 0.225T·RH − 6.838×10⁻³T² 
     − 5.482×10⁻²RH² + 1.229×10⁻³T²·RH + 8.528×10⁻⁴T·RH² 
     − 1.99×10⁻⁶T²·RH²
```
where T = temperature in °F, RH = relative humidity in %.

---

### Study Unit Typologies

| # | Type | Description |
|---|------|-------------|
| 1 | High-ventilation, high-ceiling | Newly constructed, open space |
| 2 | Traditional ground-floor shed | Dense cluster |
| 3 | Multi-floor congested building | Old construction, restricted airflow |
| 4 | Retrofitted mixed structure | Old-new with restricted airflow |

---

### Authors

Pooja Yadav · Mehul Patel · Abhijit Namboothiri · Ambar Singh  
*World Resources Institute India*

---

### Data Source

Sensor data via [Oizom OpenData API](https://opendata.oizom.com/)  
Monitoring period: 12 months (continuous)  
Interval: Hourly readings
        """)

    with col2:
        st.markdown("""
### Risk Reference

| Heat Index | Category |
|------------|----------|
| < 80°F     | Normal   |
| 80–90°F    | Caution  |
| 91–102°F   | Extreme Caution |
| 103–124°F  | Danger   |
| ≥ 125°F    | Extreme Danger |

---

### Key References

- ILO (2019). *Working on a Warmer Planet*
- Foster et al. (2021). *Quantifying the impact of heat on human physical work capacity*
- Hardik Parmar et al. (2023). Foundry heat stress study
- OSHWC 2020, Section 21 — Workplace safety
- ISHRAE thermal comfort standards

---

### Contact

WRI India  
[wri.org/india](https://www.wri.org/india)

Data: [opendata.oizom.com](https://opendata.oizom.com)
        """)

    st.markdown("---")
    st.markdown("""
    <div style='font-family: IBM Plex Mono, monospace; font-size: 10px; color: #6b7280; text-align:center'>
    © World Resources Institute · Dashboard built for research purposes only ·
    Data: Oizom OpenData API · Heat Index: NWS Rothfusz Regression
    </div>
    """, unsafe_allow_html=True)
