# 🌡️ Indoor Occupational Heat Stress Dashboard

**WRI Research · Prayagraj Dyeing and Printing Private Limited · Surat**

Real-time monitoring of indoor heat conditions across 15 sensor nodes in a textile MSME unit. Computes the NWS Heat Index and provides risk classification aligned with occupational health guidelines.

---

## Features

- **Live data** fetched from [Oizom OpenData API](https://opendata.oizom.com/) — auto-refreshes every 5 minutes
- **Heat Index** computed using the Rothfusz regression (temperatures converted °C → °F)
- **6 tabs**: Overview · Heat Map · Trends · HI Reference · Devices · About
- **15 sensor nodes** across production zones, circulation areas, and folding areas
- Risk classification: Normal / Caution / Extreme Caution / Danger / Extreme Danger
- CSV export per device
- Graceful fallback to synthetic demo data if API is unavailable

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_ORG/heat-stress-dashboard.git
cd heat-stress-dashboard
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API key
Edit `.streamlit/secrets.toml`:
```toml
OIZOM_API_KEY = "your_actual_key"
```

### 4. Run locally
```bash
streamlit run app.py
```
Open `http://localhost:8501`

---

## Deploy to Streamlit Community Cloud (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**
3. Select repo + `app.py`
4. Under **Advanced settings → Secrets**, add:
   ```
   OIZOM_API_KEY = "your_key"
   ```
5. Click **Deploy** — live in ~2 minutes

---

## Device Map

| # | Device ID | Location |
|---|-----------|----------|
| 1  | 2BA61C | Ground Stenter |
| 2  | 2D66E4 | Zero zero — near gate |
| 3  | 2BA554 | Washing-Dyeing Range |
| 4  | 2BA298 | Jigger |
| 5  | 2BA638 | Jets — B/H Office |
| 6  | 2BA640 | Jet Dyeing — Heighted |
| 7  | 2BA578 | First Printing |
| 8  | 2BA680 | Cabin & Stenter |
| 9  | 2BA64C | Stenter and Jet — Heighted |
| 10 | 2BA4CC | Loop and Folding |
| 11 | 2BA558 | Transition/Circulation Area |
| 12 | 2BA478 | Second Folding — near Digital Print |
| 13 | 2BA544 | Printing — Circulation |
| 14 | 2BA534 | Transition/Circulation Area (2) |
| 15 | 2BA650 | Printing Table |

---

## Heat Index Formula

Uses the **NWS Rothfusz regression**:

```
HI = -42.379 + 2.04901523T + 10.14333127RH
     − 0.22475541TRH − 6.83783×10⁻³T²
     − 5.481717×10⁻²RH² + 1.22874×10⁻³T²RH
     + 8.5282×10⁻⁴TRH² − 1.99×10⁻⁶T²RH²
```

where T = air temperature in **°F**, RH = relative humidity in **%**.

Sensor temperatures (°C) are converted before applying the formula:
```
T(°F) = T(°C) × 9/5 + 32
```

---

## Research Context

**Publication:** *Assessing Indoor Occupational Heat Stress: A Case Study of Textile Processing MSMEs in Surat* — WRI Working Paper

**Authors:** Pooja Yadav · Mehul Patel · Abhijit Namboothiri · Ambar Singh

**Data source:** Oizom environmental sensors, continuous 12-month deployment

---

## License

MIT — see LICENSE
