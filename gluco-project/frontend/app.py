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
/* INPUTS */
/* ===================================================== */

input, textarea {
    background-color: white !important;
    color: black !important;
    border-radius: 12px !important;
}

/* ===================================================== */
/* SELECTBOX */
/* ===================================================== */

div[data-baseweb="select"] {
    background: white !important;
    border-radius: 14px !important;
}

div[data-baseweb="select"] * {
    color: black !important;
}

/* ===================================================== */
/* METRIC CARD */
/* ===================================================== */

.metric-card {

    background: rgba(255,255,255,0.08);

    border-radius: 30px;

    padding: 40px;

    border: 1px solid rgba(255,255,255,0.12);

    backdrop-filter: blur(16px);

    box-shadow: 0 8px 32px rgba(0,0,0,0.35);

    text-align: center;

    margin-top: 10px;

    margin-bottom: 30px;
}

/* ===================================================== */
/* BIG GLUCOSE */
/* ===================================================== */

.big-glucose {

    font-size: 82px;

    font-weight: 900;

    margin-bottom: 10px;
}

/* ===================================================== */
/* STATUS TEXT */
/* ===================================================== */

.status-text {

    font-size: 28px;

    font-weight: 700;

    color: #dff4ff;
}

/* ===================================================== */
/* SECTION TITLE */
/* ===================================================== */

.section-title {

    font-size: 28px;

    font-weight: 700;

    color: #eef7ff;

    margin-bottom: 15px;

    margin-top: 10px;
}

/* ===================================================== */
/* METRIC CONTAINER */
/* ===================================================== */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.06);

    border: 1px solid rgba(255,255,255,0.10);

    padding: 18px;

    border-radius: 22px;

    backdrop-filter: blur(12px);
}

/* ===================================================== */
/* METRIC LABEL */
/* ===================================================== */

[data-testid="metric-container"] label {

    color: #b9dfff !important;

    font-weight: 700 !important;

    font-size: 18px !important;
}

/* ===================================================== */
/* METRIC VALUE */
/* ===================================================== */

[data-testid="metric-container"] div {

    color: #dff4ff !important;

    font-weight: 800 !important;
}

/* ===================================================== */
/* DOWNLOAD BUTTON */
/* ===================================================== */

.stDownloadButton button {

    background: linear-gradient(
        90deg,
        #3a8dff,
        #6fb6ff
    );

    color: white;

    border-radius: 16px;

    padding: 12px 24px;

    font-weight: 700;

    border: none;
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
        st.image(logo_path, width=220)

with col2:

    st.markdown("""
    <h1 style="
        font-size:72px;
        font-weight:900;
        margin-bottom:0;
        color:#dff4ff;
        line-height:1;
    ">
        Gluco-Guard
    </h1>

    <p style="
        font-size:24px;
        color:#b9dfff;
        margin-top:10px;
    ">
        Stay aware, stay healthy, stay in Guard
    </p>
    """, unsafe_allow_html=True)

# =========================================================
# LOG FILE
# =========================================================

LOG_FILE = "daily_glucose_log.csv"

if not os.path.exists(LOG_FILE):

    pd.DataFrame(
        columns=["Time", "Glucose"]
    ).to_csv(LOG_FILE, index=False)

# =========================================================
# LOAD ML MODEL
# =========================================================

model = None

if os.path.exists("model.pkl"):

    with open("model.pkl", "rb") as f:

        model = pickle.load(f)

# =========================================================
# PREDICTION FUNCTION
# =========================================================

def predict_glucose(ppg_signal):

    if len(ppg_signal) == 0:
        return 0

    # ==========================================
    # MODEL PREDICTION
    # ==========================================

    if model is not None:

        MAX_LEN = 100

        signal = ppg_signal[:MAX_LEN]

        if len(signal) < MAX_LEN:

            signal += [0] * (MAX_LEN - len(signal))

        features = np.array(signal).reshape(1, -1)

        prediction = model.predict(features)[0]

        return float(prediction)

    # ==========================================
    # DUMMY PREDICTION
    # ==========================================

    glucose = 80 + (np.mean(ppg_signal) % 40)

    return round(float(glucose), 1)

# =========================================================
# GLUCOSE STATUS
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
# FETCH DATA FROM BACKEND
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
    # GLUCOSE CARD
    # =====================================================

    st.markdown(
        f"""
        <div class="metric-card">

            <div
            class="big-glucose"
            style="color:{color};">

                {glucose:.1f} mg/dL

            </div>

            <div class="status-text">

                {status}

            </div>

        </div>
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
    # READ LOG AGAIN
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
