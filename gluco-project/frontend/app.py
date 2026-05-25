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
# BACKEND API
# =========================================================

API_URL = "https://gluco-backend-ok69.onrender.com/data"

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
    # REAL MODEL
    # ==========================================

    if model is not None:

        features = np.array(ppg_signal).reshape(1, -1)

        prediction = model.predict(features)[0]

        return float(prediction)

    # ==========================================
    # DUMMY MODEL
    # ==========================================

    glucose = 80 + (np.mean(ppg_signal) % 40)

    return round(float(glucose), 1)

# =========================================================
# GLUCOSE STATUS COLOR
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
# CSS
# =========================================================

st.markdown("""
<style>

/* MAIN BACKGROUND */

.stApp {
    background:
    linear-gradient(
        135deg,
        #06141f 0%,
        #0c2433 35%,
        #112f44 70%,
        #1a3f57 100%
    );
    color: white;
}

/* BACKGROUND LOGO */

.stApp::before {

    content: "";

    position: fixed;

    top: 50%;
    left: 50%;

    width: 700px;
    height: 700px;

    transform: translate(-50%, -50%);

    background-image:
    url("https://i.imgur.com/Qj8Z4bR.png");

    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;

    opacity: 0.05;

    z-index: -1;
}

/* HIDE HEADER */

header {
    visibility: hidden;
}

/* TITLES */

.main-title {

    font-size: 72px;
    font-weight: 800;

    background:
    linear-gradient(
        90deg,
        #9ed8ff,
        #5db8ff,
        #d8ecff
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {

    font-size: 20px;

    color: #d7ecff;

    margin-bottom: 35px;
}

/* GLASS CARD */

.card {

    background: rgba(255,255,255,0.08);

    border-radius: 28px;

    padding: 28px;

    border:
    1px solid rgba(255,255,255,0.12);

    backdrop-filter: blur(16px);

    box-shadow:
    0 8px 32px rgba(0,0,0,0.35);
}

/* INPUTS */

label {
    color: #eaf6ff !important;
    font-weight: 600 !important;
}

input, textarea {

    background-color: white !important;

    color: black !important;

    border-radius: 12px !important;
}

/* SELECTBOX */

div[data-baseweb="select"] {

    background: white !important;

    border-radius: 14px !important;
}

div[data-baseweb="select"] * {
    color: black !important;
}

/* METRIC CARD */

.metric-card {

    background: rgba(255,255,255,0.08);

    border-radius: 24px;

    padding: 25px;

    text-align: center;

    border:
    1px solid rgba(255,255,255,0.1);
}

/* BIG GLUCOSE */

.big-glucose {

    font-size: 72px;

    font-weight: 900;

    margin-bottom: 10px;
}

/* STATUS TEXT */

.status-text {

    font-size: 24px;

    font-weight: 700;
}

/* CHART */

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

col1, col2 = st.columns([1, 3])

with col1:

    if os.path.exists(logo_path):

        st.image(logo_path, width=180)

with col2:

    st.markdown(
        '<div class="main-title">Gluco-Guard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">AI-Powered Non-Invasive Glucose Monitoring</div>',
        unsafe_allow_html=True
    )

# =========================================================
# PATIENT INFO
# =========================================================

st.markdown("## Patient Information")

col1, col2, col3 = st.columns(3)

with col1:

    name = st.text_input("Patient Name")

    age = st.number_input("Age", 1, 120, 25)

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

    response = requests.get(API_URL, timeout=10)

    if response.status_code == 200:

        backend_online = True

        data = response.json()

        ppg = data.get("ppg", [])

    else:

        backend_online = False

        ppg = []

except:

    backend_online = False

    ppg = []

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

    st.markdown("<br>", unsafe_allow_html=True)

    # =====================================================
    # LIVE PPG GRAPH
    # =====================================================

    st.markdown("## Live PPG Signal")

    df = pd.DataFrame({"PPG": ppg})

    st.line_chart(df)

    # =====================================================
    # SAVE LOG
    # =====================================================

    new_row = pd.DataFrame({
        "Time": [datetime.now()],
        "Glucose": [glucose]
    })

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
    # DAILY ANALYTICS
    # =====================================================

    st.markdown("## Daily Glucose Trend")

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
