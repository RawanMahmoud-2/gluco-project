import streamlit as st
import requests
import pandas as pd
import time
import os

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gluco-Guard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# BACKEND API
# =========================================================

API_URL = "https://gluco-backend-ok69.onrender.com/"

# =========================================================
# LOGO PATH
# =========================================================

logo_path = "gluco_guard_logo.png"

# =========================================================
# CSS STYLING
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
    color: #d7ecff;
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
    border: 1px solid rgba(0,0,0,0.12) !important;
    box-shadow: none !important;
}

div[data-baseweb="select"] > div {
    background: white !important;
    border: none !important;
    box-shadow: none !important;
}

div[data-baseweb="select"] input {
    background: white !important;
    color: black !important;
    caret-color: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

div[data-baseweb="select"]:focus-within {
    outline: none !important;
    box-shadow: none !important;
}

div[data-baseweb="select"] * {
    color: black !important;
}

div[data-baseweb="select"] div {
    border: none !important;
}

/* ===================================================== */
/* BIG NUMBER */
/* ===================================================== */

.big-number {
    font-size: 50px;
    font-weight: 800;
    color: #8bd0ff;
    text-shadow: 0px 0px 20px rgba(139,208,255,0.45);
}

/* ===================================================== */
/* BUTTON */
/* ===================================================== */

.stDownloadButton button {
    background: linear-gradient(90deg, #3a8dff, #6fb6ff);
    color: white;
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
# LOGO + TITLE
# =========================================================

col1, col2 = st.columns([1, 3])

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=180)
    else:
        st.warning("Logo not found")

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

st.markdown(
    '<div class="section-title">Patient Information</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

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
        ["Non-Diabetic", "Type 1 Diabetes", "Type 2 Diabetes"]
    )

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# LIVE PPG SECTION
# =========================================================

st.markdown(
    '<div class="section-title">Live PPG Signal</div>',
    unsafe_allow_html=True
)

placeholder = st.empty()

# =========================================================
# AUTO REFRESH LOOP
# =========================================================

while True:

    try:

        response = requests.get(API_URL)

        if response.status_code == 200:

            data = response.json()

            ppg = data.get("ppg", [])

            with placeholder.container():

                if len(ppg) > 0:

                    df = pd.DataFrame({"PPG": ppg})

                    st.line_chart(df)

                    st.success(f"Received {len(ppg)} samples")

                else:
                    st.warning("Waiting for ESP32 Data...")

        else:
            st.error("Backend connection failed")

    except Exception as e:
        st.error(f"Error: {e}")

    time.sleep(1)
