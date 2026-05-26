import streamlit as st
import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from gluco_predict import glucose_predict

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gluco-Guard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# AUTO REFRESH
# =========================================================

st_autorefresh(interval=15000, key="refresh")

# =========================================================
# BACKEND URL
# =========================================================

BASE_URL = "https://gluco-gaurd.onrender.com"

# =========================================================
# FILES
# =========================================================

logo_path = "gluco_guard_logo.png"
LOG_FILE = "daily_glucose_log.csv"

# =========================================================
# CREATE LOG FILE
# =========================================================

if not os.path.exists(LOG_FILE):
    pd.DataFrame(columns=["Time", "Glucose"]).to_csv(LOG_FILE, index=False)

# =========================================================
# CSS (UNCHANGED)
# =========================================================

st.markdown("""<style> ... </style>""", unsafe_allow_html=True)

# =========================================================
# HEADER (UNCHANGED)
# =========================================================

col1, col2 = st.columns([1, 4])

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=220)

with col2:
    st.markdown("""
    <h1 style="
        font-size:72px;
        font-weight:900;
        margin-bottom:0;
        color:#8fd3ff !important;
        line-height:1;
    ">
        Gluco-Guard
    </h1>

    <p style="
        font-size:24px;
        color:#b9dfff !important;
        margin-top:10px;
    ">
        Stay aware, stay healthy, stay in Guard
    </p>
    """, unsafe_allow_html=True)

# =========================================================
# STATUS FUNCTION (UNCHANGED)
# =========================================================

def get_status(glucose, fasting):

    if fasting:
        if glucose < 80:
            return "LOW", "#ff5c5c"
        elif glucose <= 130:
            return "NORMAL", "#4dff88"
        elif glucose <= 180:
            return "HIGH", "#ffd24d"
        else:
            return "DANGEROUS", "#ff2e2e"
    else:
        if glucose < 80:
            return "LOW", "#ff5c5c"
        elif glucose <= 180:
            return "NORMAL", "#4dff88"
        else:
            return "HIGH", "#ff2e2e"

# =========================================================
# PATIENT INFO (UNCHANGED)
# =========================================================

st.markdown('<div class="section-title">Patient Information</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    name = st.text_input("Patient Name")
    age = st.number_input("Age", 1, 120, 25)

with col2:
    gender = st.selectbox("Gender", ["Female", "Male"])
    diabetes_type = st.selectbox(
        "Diabetes Status",
        ["Non-Diabetic", "Type 1 Diabetes", "Type 2 Diabetes"]
    )

with col3:
    meal_state = st.selectbox(
        "Meal Status",
        ["Fasting", "Ate in last 1–2 hours"]
    )

fasting = meal_state == "Fasting"

# =========================================================
# FETCH BACKEND DATA
# =========================================================

try:
    response = requests.get(f"{BASE_URL}/data", timeout=10)

    if response.status_code == 200:
        backend_online = True
        data = response.json()
        ppg = data.get("ppg", [])
    else:
        backend_online = False
        ppg = []

except Exception as e:
    backend_online = False
    ppg = []
    st.error(f"Connection Error: {e}")

# =========================================================
# STATUS BAR
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.success("Backend Connected") if backend_online else st.error("Backend Offline")

with col2:
    st.info(f"Samples: {len(ppg)}")

with col3:
    st.info(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# =========================================================
# MAIN DASHBOARD
# =========================================================

if ppg is not None and len(ppg) > 0:

    # ---------- FIX 1: ensure numeric array ----------
    ppg = np.array(ppg, dtype=float)

    # ---------- FIX 2: convert to DataFrame ----------
    ppg_df = pd.DataFrame({"ppg": ppg})

    # ---------- MODEL PREDICTION ----------
    glucose = glucose_predict(ppg_df)
    glucose = float(np.array(glucose).reshape(-1)[0])

    status, color = get_status(glucose, fasting)

    # =====================================================
    # GLUCOSE DISPLAY
    # =====================================================

    st.markdown("## Current Glucose Level")

    st.markdown(f"""
        <h1 style='
            text-align:center;
            font-size:90px;
            color:{color};
            margin-bottom:0;
        '>
            {glucose:.1f}
        </h1>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <h3 style='
            text-align:center;
            color:{color};
            margin-top:0;
            font-weight:700;
        '>
            mg/dL — {status}
        </h3>
    """, unsafe_allow_html=True)

    # =====================================================
    # LIVE PPG GRAPH
    # =====================================================

    st.markdown('<div class="section-title">Live PPG Signal</div>', unsafe_allow_html=True)

    df = pd.DataFrame({
        "PPG": np.array(ppg, dtype=float)
    })

    st.line_chart(df)

    # =====================================================
    # SAVE LOG
    # =====================================================

    log_df = pd.read_csv(LOG_FILE)

    new_row = pd.DataFrame({
        "Time": [datetime.now()],
        "Glucose": [glucose]
    })

    if len(log_df) == 0 or abs(glucose - log_df["Glucose"].iloc[-1]) > 2:
        new_row.to_csv(LOG_FILE, mode="a", header=False, index=False)

    # =====================================================
    # DAILY TREND
    # =====================================================

    log_df = pd.read_csv(LOG_FILE)

    st.markdown('<div class="section-title">Daily Glucose Trend</div>', unsafe_allow_html=True)

    log_df["Time"] = pd.to_datetime(log_df["Time"])

    st.line_chart(log_df.set_index("Time")["Glucose"])

    avg_glucose = log_df["Glucose"].mean()
    max_glucose = log_df["Glucose"].max()
    min_glucose = log_df["Glucose"].min()

    c1, c2, c3 = st.columns(3)

    c1.metric("Average", f"{avg_glucose:.1f} mg/dL")
    c2.metric("Highest", f"{max_glucose:.1f} mg/dL")
    c3.metric("Lowest", f"{min_glucose:.1f} mg/dL")

    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    csv = log_df.to_csv(index=False)

    st.download_button(
        label="⬇ Download Daily Report",
        data=csv,
        file_name="daily_glucose_report.csv",
        mime="text/csv"
    )

else:
    st.warning("Waiting for ESP32 PPG signal...")
    st.stop()
