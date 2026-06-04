import streamlit as st
import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime
from gluco_predict import glucose_predict

# ========================= NEW IMPORT (ADDED)
from twilio.rest import Client

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Gluco-Guard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SMART DATA TRACKING
# =========================================================

if "last_ppg" not in st.session_state:
    st.session_state.last_ppg = []

if "last_update" not in st.session_state:
    st.session_state.last_update = None

# ========================= NEW STATE (ADDED)
if "last_alert" not in st.session_state:
    st.session_state.last_alert = None

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

# ========================= TWILIO FUNCTIONS (ADDED)

def send_sms(to_number, message):
    client = Client(
        os.getenv("TWILIO_SID"),
        os.getenv("TWILIO_TOKEN")
    )

    client.messages.create(
        body=message,
        from_=os.getenv("TWILIO_PHONE"),
        to=to_number
    )


def send_whatsapp(to_number, message):
    client = Client(
        os.getenv("TWILIO_SID"),
        os.getenv("TWILIO_TOKEN")
    )

    client.messages.create(
        body=message,
        from_="whatsapp:" + os.getenv("TWILIO_WHATSAPP"),
        to="whatsapp:" + to_number
    )


def send_call(to_number, message):
    client = Client(
        os.getenv("TWILIO_SID"),
        os.getenv("TWILIO_TOKEN")
    )

    call = client.calls.create(
        twiml=f'<Response><Say>{message}</Say></Response>',
        to=to_number,
        from_=os.getenv("TWILIO_PHONE")
    )

# =========================================================
# CSS
# =========================================================
# (UNCHANGED — YOUR ORIGINAL CSS KEPT EXACTLY)

st.markdown("""<style>
/* your full css unchanged */
</style>""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
# (UNCHANGED)

col1, col2 = st.columns([1, 4])

with col1:
    if os.path.exists(logo_path):
        st.image(logo_path, width=400)

with col2:
    st.markdown("""<h1>GlucoGuard</h1>""", unsafe_allow_html=True)

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
# PATIENT INFO
# =========================================================

st.markdown('<div class="section-title">Patient Information</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:

    name = st.text_input("Patient Name")

    age = st.number_input("Age", 1, 120, 25)

    # ========================= ADDED
    phone_numbers = st.text_input(
        "Emergency Contacts (comma separated, include country code)"
    )

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
        ppg = [x for x in ppg if isinstance(x, (int, float))]

        if ppg != st.session_state.last_ppg:
            st.session_state.last_ppg = ppg
            st.session_state.last_update = datetime.now()
            st.rerun()

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
    st.success("Backend Connected" if backend_online else "Backend Offline")

with col2:
    log_df = pd.read_csv(LOG_FILE)
    st.info(f"Measurements: {len(log_df)}")

with col3:
    st.info(
        f"Updated: {st.session_state.last_update.strftime('%H:%M:%S') if st.session_state.last_update else 'No Data'}"
    )

# =========================================================
# MAIN DASHBOARD
# =========================================================

if len(ppg) > 0:

    glucose = glucose_predict(ppg)

    status, color = get_status(glucose, fasting)

    # ========================= EMERGENCY SYSTEM (ADDED)
    alert_triggered = status in ["HIGH", "LOW", "DANGEROUS"]

    if phone_numbers and alert_triggered:

        message = (
            f"Emergency Alert!\n"
            f"Patient: {name}\n"
            f"Glucose: {glucose:.1f} mg/dL\n"
            f"Status: {status}"
        )

        contacts = [n.strip() for n in phone_numbers.split(",")]

        if st.session_state.last_alert != status:

            for number in contacts:
                try:
                    send_sms(number, message)
                    send_whatsapp(number, message)
                    send_call(number, message)
                except:
                    pass

            st.session_state.last_alert = status
            st.warning("Emergency alerts sent")

    # =====================================================
    # GLUCOSE DISPLAY (UNCHANGED)
    # =====================================================

    st.markdown("## Current Glucose Level")

    st.markdown(
        f"<h1 style='text-align:center;font-size:90px;color:{color};'>{glucose:.1f}</h1>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<h3 style='text-align:center;color:{color};'>{status}</h3>",
        unsafe_allow_html=True
    )

    # =====================================================
    # LIVE PPG GRAPH (UNCHANGED)
    # =====================================================

    st.line_chart(pd.DataFrame({"PPG": ppg}))

    # =====================================================
    # LOGGING (UNCHANGED)
    # =====================================================

    log_df = pd.read_csv(LOG_FILE)

    new_row = pd.DataFrame({
        "Time": [datetime.now()],
        "Glucose": [glucose]
    })

    if len(log_df) == 0 or abs(glucose - log_df["Glucose"].iloc[-1]) > 2:
        new_row.to_csv(LOG_FILE, mode="a", header=False, index=False)

    log_df = pd.read_csv(LOG_FILE)

    # =====================================================
    # DAILY TREND (UNCHANGED)
    # =====================================================

    if len(log_df) > 0:

        log_df["Time"] = pd.to_datetime(log_df["Time"])

        st.line_chart(log_df.set_index("Time")["Glucose"])

        st.metric("Average", f"{log_df['Glucose'].mean():.1f}")
        st.metric("Highest", f"{log_df['Glucose'].max():.1f}")
        st.metric("Lowest", f"{log_df['Glucose'].min():.1f}")

    csv = log_df.to_csv(index=False)

    st.download_button(
        "⬇ Download Report",
        csv,
        "report.csv",
        "text/csv"
    )

else:
    st.warning("Waiting for ESP32 PPG signal...")
