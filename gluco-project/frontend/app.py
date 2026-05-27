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

    pd.DataFrame(
        columns=["Time", "Glucose"]
    ).to_csv(LOG_FILE, index=False)


# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

/* ===================================================== */
/* MAIN BACKGROUND */
/* ===================================================== */

.stApp {
    background: linear-gradient(
        135deg,
        #06141f 0%,
        #0c2433 35%,
        #112f44 70%,
        #1a3f57 100%
    );
    color: white;
}

/* ===================================================== */
/* BACKGROUND LOGO */
/* ===================================================== */

.stApp::before {
    content: "";
    position: fixed;
    top: 50%;
    left: 50%;
    width: 700px;
    height: 700px;
    transform: translate(-50%, -50%);
    background-image: url("https://i.imgur.com/Qj8Z4bR.png");
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
    opacity: 0.06;
    filter: grayscale(100%) hue-rotate(180deg) brightness(1.2);
    z-index: -1;
}

/* ===================================================== */
/* HIDE HEADER */
/* ===================================================== */

header {
    visibility: hidden;
}

/* ===================================================== */
/* SIDEBAR */
/* ===================================================== */

section[data-testid="stSidebar"] {
    display: none;
}

/* ===================================================== */
/* TITLE */
/* ===================================================== */

.main-title {
    font-size: 72px;
    font-weight: 800;
    text-align: center;
    background: linear-gradient(90deg, #9ed8ff, #5db8ff, #d8ecff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-top: 10px;
    margin-bottom: 5px;
}

/* ===================================================== */
/* SUBTITLE */
/* ===================================================== */

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #d7ecff !important;
    margin-bottom: 35px;
}

/* ===================================================== */
/* SECTION TITLE */
/* ===================================================== */

.section-title {
    font-size: 26px;
    font-weight: 700;
    color: #eef7ff;
    margin-bottom: 15px;
}

/* ===================================================== */
/* GLASS CARD */
/* ===================================================== */

.card {
    background: rgba(255,255,255,0.08);
    border-radius: 28px;
    padding: 28px;
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(16px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
}

/* ===================================================== */
/* LABELS */
/* ===================================================== */

label {
    color: #eaf6ff !important;
    font-weight: 600 !important;
}

/* ===================================================== */
/* INPUTS */
/* ===================================================== */

input,
textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 12px !important;
}

/* ===================================================== */
/* TEXT INPUT FIX */
/* ===================================================== */

.stTextInput input {
    color: black !important;
}

/* ===================================================== */
/* NUMBER INPUT FIX */
/* ===================================================== */

[data-testid="stNumberInput"] input {
    color: black !important;
    background-color: white !important;
}

/* ===================================================== */
/* CLEAN WHITE SELECTBOX FIX */
/* ===================================================== */

/* main container */

div[data-baseweb="select"] {
    background: white !important;
    border-radius: 14px !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    box-shadow: none !important;
}

/* inner control */

div[data-baseweb="select"] > div {
    background: white !important;
    border: none !important;
    box-shadow: none !important;
}

/* input field */

div[data-baseweb="select"] input {
    background: white !important;
    color: black !important;
    caret-color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

/* remove focus glow */

div[data-baseweb="select"]:focus-within {
    outline: none !important;
    box-shadow: none !important;
}

/* selected text */

div[data-baseweb="select"] * {
    color: black !important;
}

/* remove weird borders */

div[data-baseweb="select"] div {
    border: none !important;
}

/* ===================================================== */
/* BIG GLUCOSE NUMBER */
/* ===================================================== */

.big-number {
    font-size: 50px;
    font-weight: 800;
    color: #8bd0ff !important;
    text-shadow: 0px 0px 20px rgba(139,208,255,0.45);
}

/* ===================================================== */
/* METRIC CONTAINER */
/* ===================================================== */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.06);

    border-radius: 20px;

    padding: 15px;

    border: 1px solid rgba(255,255,255,0.08);
}

/* ===================================================== */
/* METRIC LABEL */
/* ===================================================== */

[data-testid="metric-container"] label {

    color: #8fd3ff !important;

    font-weight: bold !important;

    font-size: 16px !important;
}

/* ===================================================== */
/* METRIC NUMBER */
/* ===================================================== */

[data-testid="metric-container"] [data-testid="stMetricValue"] {

    color: white !important;

    font-weight: 800 !important;
}

/* ===================================================== */
/* METRIC NUMBER TEXT */
/* ===================================================== */

[data-testid="metric-container"] [data-testid="stMetricValue"] * {

    color: white !important;
}

/* ===================================================== */
/* BUTTON */
/* ===================================================== */

.stDownloadButton button {
    background: linear-gradient(90deg, #3a8dff, #6fb6ff);
    color: white !important;
    border-radius: 16px;
    padding: 12px 24px;
    font-weight: 700;
    border: none;
}

.stDownloadButton button:hover {
    transform: scale(1.03);
    box-shadow: 0px 0px 18px rgba(120,190,255,0.4);
}

/* ===================================================== */
/* CHART */
/* ===================================================== */

[data-testid="stLineChart"] {
    background: rgba(255,255,255,0.05);
    border-radius: 22px;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================

col1, col2 = st.columns([1, 4])

with col1:

    if os.path.exists(logo_path):
        st.image(logo_path, width=400)

with col2:

    st.markdown("""
   <h1 style="
    font-size:72px;
    font-weight:900;
    margin-bottom:0;
    line-height:1;
   ">
    <span style="color:#c7d0d9;">Gluco</span><span style="color:#5db8ff;">Guard</span>
   </h1>

   <p style="
    font-size:24px;
    color:#dff2ff !important;
    margin-top:10px;
    font-weight:500;
   ">
    Stay aware. Stay healthy. Stay in Guard.
   </p>
    
    """, unsafe_allow_html=True)


# =========================================================
# STATUS FUNCTION
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
# PATIENT INFO
# =========================================================

st.markdown(
    '<div class="section-title">Patient Information</div>',
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)

with col1:

    name = st.text_input("Patient Name")

    age = st.number_input(
        "Age",
        1,
        120,
        25
    )

with col2:

    gender = st.selectbox(
        "Gender",
        ["Female", "Male"]
    )

    diabetes_type = st.selectbox(
        "Diabetes Status",
        [
            "Non-Diabetic",
            "Type 1 Diabetes",
            "Type 2 Diabetes"
        ]
    )

with col3:

    meal_state = st.selectbox(
        "Meal Status",
        [
            "Fasting",
            "Ate in last 1–2 hours"
        ]
    )

fasting = meal_state == "Fasting"

# =========================================================
# FETCH BACKEND DATA
# =========================================================

try:

    response = requests.get(
        f"{BASE_URL}/data",
        timeout=10
    )

    if response.status_code == 200:

        backend_online = True

        data = response.json()

        ppg = data.get("ppg", [])
        ppg = [
    x for x in ppg
    if isinstance(x, (int, float))
                ]

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

    if backend_online:
        st.success("Backend Connected")

    else:
        st.error("Backend Offline")

with col2:

         log_df = pd.read_csv(LOG_FILE)
    measurement_count = len(log_df)
    
    st.info(f"Measurements: {measurement_count}")

with col3:

    st.info(
        f"Updated: {datetime.now().strftime('%H:%M:%S')}"
    )

# =========================================================
# MAIN DASHBOARD
# =========================================================

if len(ppg) > 0:

    glucose = glucose_predict(ppg)

    status, color = get_status(glucose, fasting)

    # =====================================================
    # GLUCOSE DISPLAY
    # =====================================================

    st.markdown("## Current Glucose Level")

    st.markdown(
        f"""
        <h1 style='
            text-align:center;
            font-size:90px;
            color:{color};
            margin-bottom:0;
        '>
            {glucose:.1f}
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
    f"""
    <h3 style='
        text-align:center;
        color:{color};
        margin-top:0;
        font-weight:700;
    '>
        mg/dL — {status}
    </h3>
    """,
    unsafe_allow_html=True
)
    # =====================================================
    # LIVE PPG GRAPH
    # =====================================================

    st.markdown(
        '<div class="section-title">Live PPG Signal</div>',
        unsafe_allow_html=True
    )

    df = pd.DataFrame({
        "PPG": ppg
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

        new_row.to_csv(
            LOG_FILE,
            mode="a",
            header=False,
            index=False
        )

    # =====================================================
    # READ LOG
    # =====================================================

    log_df = pd.read_csv(LOG_FILE)

    # =====================================================
    # DAILY TREND
    # =====================================================

    st.markdown(
        '<div class="section-title">Daily Glucose Trend</div>',
        unsafe_allow_html=True
    )

    if len(log_df) > 0:

        log_df["Time"] = pd.to_datetime(log_df["Time"])

        st.line_chart(
            log_df.set_index("Time")["Glucose"]
        )

        avg_glucose = log_df["Glucose"].mean()

        max_glucose = log_df["Glucose"].max()

        min_glucose = log_df["Glucose"].min()

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Average",
            f"{avg_glucose:.1f} mg/dL"
        )

        c2.metric(
            "Highest",
            f"{max_glucose:.1f} mg/dL"
        )

        c3.metric(
            "Lowest",
            f"{min_glucose:.1f} mg/dL"
        )

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
