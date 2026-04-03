"""
Indoor Occupational Heat Stress Dashboard
Prayagraj Dyeing and Printing Private Limited — Surat
WRI India
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

st.set_page_config(
    page_title="Heat Stress Monitor | Prayagraj Dyeing and Printing Pvt. Ltd.",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap');

:root {
    --bg: #ffffff;
    --surface: #f8f9fa;
    --surface2: #f1f3f5;
    --border: #dee2e6;
    --text: #000000;
    --muted: #000000;
    --accent: #e85d04;
    --accent2: #dc2626;
    --safe: #16a34a;
    --warn: #b45309;
    --danger: #c2410c;
    --extreme: #b91c1c;
    --mono: 'IBM Plex Mono', monospace;
    --sans: 'IBM Plex Sans', sans-serif;
}

html, body, [class*="css"] {
    font-family: var(--sans);
    background-color: var(--bg) !important;
    color: #000000 !important;
}

.stApp { background-color: var(--bg) !important; }

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

/* Force ALL text black everywhere */
p, span, div, li, label, h1, h2, h3, h4, h5, h6,
.stMarkdown, .stText, [class*="css"] {
    color: #000000 !important;
}

.metric-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 12px;
    color: #000000 !important;
}
.metric-card .label {
    font-family: var(--mono);
    font-size: 10px;
    color: #000000 !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}
.metric-card .value {
    font-family: var(--mono);
    font-size: 28px;
    font-weight: 700;
    line-height: 1;
    color: #000000 !important;
}
.metric-card .sub {
    font-size: 11px;
    color: #000000 !important;
    margin-top: 4px;
}

/* Value colour overrides — dark enough to read on white */
.v-safe    { color: #15803d !important; }
.v-caution { color: #92400e !important; }
.v-danger  { color: #c2410c !important; }
.v-extreme { color: #991b1b !important; }

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 4px;
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-safe    { background: #dcfce7; color: #14532d !important; border: 1px solid #86efac; }
.badge-caution { background: #fef9c3; color: #713f12 !important; border: 1px solid #fde047; }
.badge-danger  { background: #ffedd5; color: #7c2d12 !important; border: 1px solid #fdba74; }
.badge-extreme { background: #fee2e2; color: #7f1d1d !important; border: 1px solid #fca5a5; }

.section-header {
    font-family: var(--mono);
    font-size: 11px;
    color: #000000 !important;
    text-transform: uppercase;
    letter-spacing: 2px;
    padding: 0 0 8px 0;
    border-bottom: 2px solid var(--border);
    margin-bottom: 16px;
    font-weight: 600;
}

hr { border-color: var(--border) !important; }

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stDataFrame { border: 1px solid var(--border); border-radius: 8px; }

/* Alert box — solid dark text, tinted background */
.alert-box {
    border-left: 4px solid #c2410c;
    background: #fff7ed;
    color: #000000 !important;
    padding: 14px 18px;
    border-radius: 0 6px 6px 0;
    margin: 8px 0;
    font-size: 14px;
    font-weight: 500;
}
.alert-box * { color: #000000 !important; }
.alert-box strong { color: #000000 !important; font-weight: 700; }

.main-title {
    font-family: var(--mono);
    font-size: 20px;
    font-weight: 700;
    color: #000000 !important;
    letter-spacing: -0.5px;
}
.main-subtitle {
    font-family: var(--sans);
    font-size: 12px;
    color: #000000 !important;
    margin-top: 2px;
}

.js-plotly-plot { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)


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
API_KEY    = st.secrets.get("OIZOM_API_KEY", "")


def celsius_to_fahrenheit(c: float) -> float:
    return c * 9 / 5 + 32

def heat_index_fahrenheit(T_f: float, RH: float) -> float:
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
        return "Normal",          "safe"
    elif hi_f < 91:
        return "Caution",         "caution"
    elif hi_f < 103:
        return "Extreme Caution", "danger"
    elif hi_f < 125:
        return "Danger",          "extreme"
    else:
        return "Extreme Danger",  "extreme"

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
      <div class='main-subtitle'>Prayagraj Dyeing &amp; Printing Pvt. Ltd.<br>Surat · WRI India</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    auto_refresh = st.toggle("⟳ Auto-refresh (5 min)", value=False)

    time_range = st.selectbox(
        "Time window",
        ["Last 6 hours", "Last 24 hours", "Last 48 hours", "Last 7 days"],
        index=1,
    )
    hours_map = {"Last 6 hours": 6, "Last 24 hours": 24,
                 "Last 48 hours": 48, "Last 7 days": 168}
    selected_hours = hours_map[time_range]

    st.markdown("#### Devices")
    all_checked = st.checkbox("Select all", value=True)
    selected_devices = {}
    for did, info in DEVICES.items():
        checked = st.checkbox(f"`{did}` {info['name']}", value=all_checked, key=f"cb_{did}")
        if checked:
            selected_devices[did] = info

    st.markdown("---")
    st.markdown("""
    <div style='font-size:10px; color:#000000 !important; font-family: IBM Plex Mono, monospace;'>
    <strong>DATA SOURCE</strong><br>
    <a href='https://opendata.oizom.com' style='color:#c2410c'>opendata.oizom.com</a><br><br>
    <strong>REFERENCE</strong><br>
    NWS Heat Index Chart<br>
    Rothfusz Regression<br><br>
    <strong>UNITS</strong><br>
    Temperature → °C / °F<br>
    Heat Index → °F (NWS)
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
<div style='padding:8px 0 24px 0'>
  <div style='font-family:IBM Plex Mono,monospace; font-size:11px; color:#c2410c;
              letter-spacing:2px; text-transform:uppercase; margin-bottom:6px; font-weight:600;'>
    WRI India · Indoor Occupational Heat Stress
  </div>
  <h1 style='margin:0; font-family:IBM Plex Sans,sans-serif; font-weight:700;
             font-size:26px; color:#000000; letter-spacing:-0.5px;'>
    Prayagraj Dyeing &amp; Printing Pvt. Ltd. — Live Sensor Dashboard
  </h1>
  <p style='margin:4px 0 0 0; color:#000000; font-size:13px; font-weight:500;'>
    Surat · 15 Sensor Nodes · Heat Index Analysis
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
            "HI (°F)":      round(hi_f, 1),
            "HI (°C)":      round((hi_f-32)*5/9, 1) if not np.isnan(hi_f) else np.nan,
            "Risk":         row.get("HI_Cat", "—"),
        })
    return pd.DataFrame(rows)

# Plotly shared theme
PLOTLY_LAYOUT = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#f8f9fa",
    font=dict(family="IBM Plex Mono", color="#000000", size=12),
)


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
              <div class='sub'>{celsius_to_fahrenheit(avg_temp):.1f}°F · {len(all_latest)} sensors</div>
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
              <div class='value v-{avg_lv}'>{avg_hi_f:.1f}°F</div>
              <div class='sub'>{(avg_hi_f-32)*5/9:.1f}°C apparent temperature</div>
            </div>""", unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
            <div class='metric-card'>
              <div class='label'>Peak Heat Index</div>
              <div class='value v-{max_level}'>{max_hi_f:.1f}°F</div>
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

    st.markdown("<div class='section-header'>⚠ Active Alerts</div>",
                unsafe_allow_html=True)
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
        color_map = {
            "Normal":         "#16a34a",
            "Caution":        "#ca8a04",
            "Extreme Caution":"#ea580c",
            "Danger":         "#dc2626",
            "Extreme Danger": "#7f1d1d",
        }
        bar_colors = [color_map.get(c, "#6b7280") for c in cats]

        fig = go.Figure(go.Bar(
            x=hi_vals, y=names, orientation="h",
            marker_color=bar_colors,
            text=[f"{v:.1f}°F — {c}" for v, c in zip(hi_vals, cats)],
            textposition="outside",
            textfont=dict(color="#000000", size=11),
            hovertemplate="<b>%{y}</b><br>Heat Index: %{x:.1f}°F<extra></extra>",
        ))
        for threshold, label, color in [
                (80, "Caution",         "#16a34a"),
                (91, "Extreme Caution", "#ca8a04"),
                (103,"Danger",          "#ea580c"),
                (125,"Extreme Danger",  "#dc2626")]:
            fig.add_vline(x=threshold, line_dash="dot", line_color=color,
                          annotation_text=label,
                          annotation_font_color="#000000",
                          annotation_font_size=10)

        fig.update_layout(
            **PLOTLY_LAYOUT,
            xaxis=dict(title="Heat Index (°F)", gridcolor="#dee2e6", color="#000000",
                       range=[min(hi_vals)-5, max(hi_vals)+30]),
            yaxis=dict(gridcolor="#dee2e6", color="#000000"),
            margin=dict(l=0, r=80, t=20, b=40),
            height=500,
        )
        st.plotly_chart(fig, use_container_width=True)

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
            big, x="Temperature", y="Humidity", color="HI_F",
            hover_data=["Location", "Time", "HI_Cat"],
            color_continuous_scale=["#16a34a","#ca8a04","#ea580c","#dc2626"],
            labels={"Temperature":"Temp (°C)","Humidity":"RH (%)","HI_F":"HI (°F)"},
        )
        fig2.update_layout(
            **PLOTLY_LAYOUT,
            xaxis=dict(gridcolor="#dee2e6", color="#000000"),
            yaxis=dict(gridcolor="#dee2e6", color="#000000"),
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
        fig3 = make_subplots(rows=3, cols=1, shared_xaxes=True,
                             vertical_spacing=0.06,
                             subplot_titles=("Temperature (°C)",
                                             "Relative Humidity (%)",
                                             "Heat Index (°F)"))
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["Temperature"],
                                  mode="lines", name="Temp",
                                  line=dict(color="#ea580c", width=2)), row=1, col=1)
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["Humidity"],
                                  mode="lines", name="RH",
                                  line=dict(color="#0284c7", width=2)), row=2, col=1)
        fig3.add_trace(go.Scatter(x=df_t["Time"], y=df_t["HI_F"],
                                  mode="lines", name="HI",
                                  line=dict(color="#dc2626", width=2)), row=3, col=1)
        for y, color in [(80,"#16a34a"),(91,"#ca8a04"),(103,"#ea580c"),(125,"#dc2626")]:
            fig3.add_hline(y=y, line_dash="dot", line_color=color,
                           line_width=1, row=3, col=1)

        axis_style = dict(gridcolor="#dee2e6", color="#000000", linecolor="#000000")
        fig3.update_layout(
            **PLOTLY_LAYOUT,
            xaxis3=axis_style, yaxis=axis_style, yaxis2=axis_style, yaxis3=axis_style,
            legend=dict(bgcolor="#f8f9fa", bordercolor="#dee2e6", font=dict(color="#000000")),
            margin=dict(l=0, r=0, t=40, b=40),
            height=600, showlegend=False,
        )
        # Subplot title colour
        for ann in fig3.layout.annotations:
            ann.font.color = "#000000"
        st.plotly_chart(fig3, use_container_width=True)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Min Temp", f"{df_t['Temperature'].min():.1f}°C")
        c2.metric("Max Temp", f"{df_t['Temperature'].max():.1f}°C")
        c3.metric("Avg Temp", f"{df_t['Temperature'].mean():.1f}°C")
        c4.metric("Max HI",   f"{df_t['HI_F'].max():.1f}°F")
        c5.metric("Avg HI",   f"{df_t['HI_F'].mean():.1f}°F")

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
            x=df["Time"], y=df["HI_F"],
            mode="lines", name=info["name"],
            line=dict(color=palette[i % len(palette)], width=1.5),
        ))
    fig4.update_layout(
        **PLOTLY_LAYOUT,
        xaxis=dict(gridcolor="#dee2e6", color="#000000"),
        yaxis=dict(gridcolor="#dee2e6", color="#000000", title="Heat Index (°F)"),
        legend=dict(bgcolor="#f8f9fa", bordercolor="#dee2e6",
                    font=dict(color="#000000", size=10)),
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

    rh_range   = list(range(40, 105, 5))
    temp_range = list(range(80, 112, 2))
    z_matrix   = []
    for T in temp_range:
        z_matrix.append([round(heat_index_fahrenheit(float(T), float(RH)), 1)
                         for RH in rh_range])

    fig5 = go.Figure(go.Heatmap(
    z=z_matrix,
    x=[f"{r}%" for r in rh_range],
    y=[f"{t}°F ({(t-32)*5/9:.0f}°C)" for t in temp_range],
    colorscale=[[0,"#16a34a"],[0.25,"#ca8a04"],
                [0.55,"#ea580c"],[0.75,"#dc2626"],[1.0,"#7f1d1d"]],
    text=[[str(v) for v in row] for row in z_matrix],
    texttemplate="%{text}",
    textfont=dict(size=9, family="IBM Plex Mono", color="#000000"),
    hovertemplate="Temp: %{y}<br>RH: %{x}<br>HI: %{z}°F<extra></extra>",
    showscale=True,
    colorbar=dict(
        title="HI (°F)",  # ✅ FIXED (string instead of dict)
        tickfont=dict(family="IBM Plex Mono", color="#000000"),
    ),
))
    fig5.update_layout(
        **PLOTLY_LAYOUT,
        plot_bgcolor="#ffffff",
        xaxis=dict(title="Relative Humidity", color="#000000"),
        yaxis=dict(title="Air Temperature",   color="#000000"),
        margin=dict(l=0, r=0, t=20, b=40),
        height=550,
    )
    st.plotly_chart(fig5, use_container_width=True)

    st.markdown("<div class='section-header'>Risk Levels</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    categories = [
        ("< 80°F",    "Normal",          "safe",    "No heat stress"),
        ("80–90°F",   "Caution",         "caution", "Fatigue possible with prolonged exposure"),
        ("91–102°F",  "Extreme Caution", "danger",  "Heat cramps / exhaustion possible"),
        ("103–124°F", "Danger",          "extreme", "Heat cramps / exhaustion likely; stroke possible"),
        ("≥ 125°F",   "Extreme Danger",  "extreme", "Heat stroke highly likely"),
    ]
    for i, (rng, name, level, desc) in enumerate(categories):
        target = col1 if i % 2 == 0 else col2
        with target:
            st.markdown(f"""
            <div class='metric-card' style='margin-bottom:8px'>
              <span class='badge badge-{level}'>{name}</span>
              <span style='margin-left:8px; font-family:IBM Plex Mono; font-size:12px;
                           color:#000000; font-weight:600'>{rng}</span>
              <div style='font-size:12px; color:#000000; margin-top:6px'>{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.info("💡 **Note:** Heat Index values are in °F (NWS standard). Sensor readings in °C "
            "are converted via T(°F) = T(°C) × 9/5 + 32 before applying the Rothfusz regression.")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: DEVICES
# ─────────────────────────────────────────────────────────────────────────────
with tab_devices:
    st.markdown("<div class='section-header'>Sensor Network — Prayagraj Dyeing &amp; Printing</div>",
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
                      <div style='font-family:IBM Plex Mono;font-size:16px;
                                  color:#c2410c;font-weight:600'>{temp_c:.1f}°C</div>
                    </div>
                    <div>
                      <div class='label'>RH</div>
                      <div style='font-family:IBM Plex Mono;font-size:16px;
                                  color:#0369a1;font-weight:600'>{hum:.1f}%</div>
                    </div>
                    <div>
                      <div class='label'>HI</div>
                      <div style='font-family:IBM Plex Mono;font-size:16px;
                                  color:#b91c1c;font-weight:600'>{hi_f:.1f}°F</div>
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
Monitoring period: 12 months (continuous) · Interval: Hourly readings
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
- OSHWC 2020, Section 21
- ISHRAE thermal comfort standards

---

### Contact

WRI India · [wri.org/india](https://www.wri.org/india)

Data: [opendata.oizom.com](https://opendata.oizom.com)
        """)

    st.markdown("---")
    st.markdown("""
    <div style='font-family:IBM Plex Mono,monospace;font-size:10px;
                color:#000000;text-align:center;font-weight:500'>
    © World Resources Institute · Dashboard for research purposes only ·
    Data: Oizom OpenData API · Heat Index: NWS Rothfusz Regression
    </div>
    """, unsafe_allow_html=True)
