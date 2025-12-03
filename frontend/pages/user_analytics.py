import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND = os.getenv("BACKEND_URL")

st.title("📈 User Session Analytics")

session_id = st.text_input("Enter Session ID", value=st.session_state.get("session_id", ""))

if st.button("Get Analytics"):
    res = requests.get(f"{BACKEND}/api/v1/user/analytics/{session_id}")

    if res.status_code == 200:
        data = res.json()

        st.subheader("📊 Overview")
        st.metric("Total Requests", data["total_requests"])
        st.metric("Total Tokens", data["total_tokens"])
        st.metric("Average Latency (ms)", data["avg_latency_ms"])
        st.metric("Top Model Used", data["top_model"])
    else:
        st.error("Failed to fetch user analytics")
