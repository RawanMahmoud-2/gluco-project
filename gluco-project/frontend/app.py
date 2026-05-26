import streamlit as st
import requests
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

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

st_autorefresh(interval=3000, key="refresh")

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
# LOAD MODEL
# =========================================================

model = None

if os.path.exists("model.pkl"):

    with open("model.pkl", "rb") as f:
        model = pickle.load(f)

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
/* ALL TEXT */
/* ===================================================== */

html,
body,
p,
span,
div,
label,
h1,
h2,
h3,
h4,
h5,
h6 {
    color: white !important;
}

/* ===================================================== */
/* INPUTS */
/* ===================================================== */

input {
    background-color: white !important;
    color: black !important;
    border-radius: 12px !important;
}

/* ===================================================== */
/* TEXT INPUT */
/* ===================================================== */

.stTextInput input {
    color: black !important;
}

/* ===================================================== */
/* NUMBER INPUT */
/* ===================================================== */

[data-testid="stNumberInput"] input {
    color: black !important;
    background-color: white !important;
}

/* ===================================================== */
/* SELECTBOX */
/* ===================================================== */

div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 12px !important;
}

/* ===================================================== */
/* SELECTBOX TEXT */
/* ===================================================== */

div[data-baseweb="select"] * {
    color: black !important;
}

/* ===================================================== */
/* METRICS */
/* ===================================================== */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.06);

    border-radius: 20px;

    padding: 15px;

    border: 1px solid rgba(255,255,255,0.08);
}

[data-testid="metric-container"] label {

    color: #8fd3ff !important;

    font-weight: bold !important;
}

[data-testid="metric-container"] div {

    color: white !important;

    font-weight: bold !important;
}

/* ===================================================== */
/* CHART */
/* ===================================================== */

[data-testid="stLineChart"] {

    background: rgba(255,255,255,0.04);

    border-radius: 20px;

    padding: 10px;
}

/* ===================================================== */
/* BUTTON */
/* ===================================================== */

.stDownloadButton button {

    background: linear-gradient(
        90deg,
        #3a8dff,
        #6fb6ff
    );

    color: white !important;

    border-radius: 14px;

    border: none;

    font-weight: bold;
}

/* ===================================================== */
/* SECTION TITLE */
/* ===================================================== */

.section-title {

    font-size: 28px;

    font-weight: 700;

    color: white !important;

    margin-bottom: 15px;

    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
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
# PREDICTION FUNCTION
# =========================================================

def predict_glucose(ppg_signal):

    if len(ppg_signal) == 0:
        return 0

    if model is not None:

        MAX_LEN = 100

        signal = ppg_signal[:MAX_LEN]

        if len(signal) < MAX_LEN:
            signal += [0] * (MAX_LEN - len(signal))

        features = np.array(signal).reshape(1, -1)

        prediction = model.predict(features)[0]

        return float(prediction)

    glucose = 80 + (np.mean(ppg_signal) % 40)

    return round(float(glucose), 1)

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

    st.info(f"Samples: {len(ppg)}")

with col3:

    st.info(
        f"Updated: {datetime.now().strftime('%H:%M:%S')}"
    )

# =========================================================
# MAIN DASHBOARD
# =========================================================

if len(ppg) > 0:

    glucose = predict_glucose(ppg)

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
            color:white;
            margin-top:0;
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
