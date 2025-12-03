import streamlit as st
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh
import plotly.express as px

# Load backend URL
load_dotenv()
BACKEND = os.getenv("BACKEND_URL")

# Page Settings
st.set_page_config(page_title="LLM Observability Dashboard", layout="wide")
st.title("📊 LLM Observability Dashboard")

st.info("This page refreshes every 10 seconds for real-time monitoring.")

# Auto-refresh
st_autorefresh(interval=10000, key="logs_auto_refresh")


st.subheader("📌 Summary Metrics")

try:
    summary_res = requests.get(f"{BACKEND}/api/v1/metrics/summary")
    if summary_res.status_code == 200:
        summary = summary_res.json()
    else:
        summary = {}
        st.error("Could not fetch summary metrics.")
except Exception as e:
    summary = {}
    st.error(f"Error fetching summary: {e}")


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📥 Total Requests", summary.get("total_requests", 0))

with col2:
    st.metric("✅ Success Rate", f"{summary.get('success_rate', 0)}%")

with col3:
    st.metric("⚡ Avg Latency (ms)", summary.get("avg_latency_ms", 0))

with col4:
    total_tokens = (summary.get("tokens_in", 0) + summary.get("tokens_out", 0))
    st.metric("🔢 Total Tokens", total_tokens)


st.subheader("📈 Token Usage Trend")

try:
    token_res = requests.get(f"{BACKEND}/api/v1/metrics/token-trend")
    if token_res.status_code == 200:
        token_data = token_res.json().get("data", [])
        df_tokens = pd.DataFrame(token_data)

        if not df_tokens.empty:
            fig = px.line(df_tokens, x="timestamp", y=["tokens_in", "tokens_out"], title="Token Trend")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No token data available.")
    else:
        st.error("Failed to load token trend.")
except Exception as e:
    st.error(f"Token trend error: {e}")


st.subheader("⏱️ Latency Trend")

try:
    latency_res = requests.get(f"{BACKEND}/api/v1/metrics/latency-trend")
    if latency_res.status_code == 200:
        latency_data = latency_res.json().get("data", [])
        df_latency = pd.DataFrame(latency_data)

        if not df_latency.empty:
            fig2 = px.line(df_latency, x="timestamp", y="latency_ms", title="Latency Trend")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No latency data available.")
    else:
        st.error("Failed to load latency trend.")
except Exception as e:
    st.error(f"Latency trend error: {e}")


st.subheader("❌ Error Trend")

try:
    err_res = requests.get(f"{BACKEND}/api/v1/metrics/error-trend")
    if err_res.status_code == 200:
        err_data = err_res.json().get("data", [])
        df_errors = pd.DataFrame(err_data)

        if not df_errors.empty:
            st.dataframe(df_errors, use_container_width=True)
        else:
            st.info("No errors found.")
    else:
        st.error("Failed to load error trend.")
except Exception as e:
    st.error(f"Error trend error: {e}")


st.subheader("🚨 Live Alerts")

try:
    alerts_res = requests.get(f"{BACKEND}/api/v1/alerts")
    if alerts_res.status_code == 200:
        alerts = alerts_res.json().get("alerts", [])
        if alerts:
            for alert in alerts:
                if alert['type'] == "latency":
                    st.warning(alert["message"])
                elif alert['type'] == "error_rate":
                    st.error(alert["message"])
                else:
                    st.info(alert["message"])
        else:
            st.success("No alerts. Everything looks good!")
    else:
        st.error("Failed to fetch alerts.")
except Exception as e:
    st.error(f"Alerts error: {e}")


st.subheader("🧾 Latest Logs")

try:
    log_res = requests.get(f"{BACKEND}/api/v1/logs?limit=100")
    if log_res.status_code == 200:
        logs = log_res.json().get("logs", [])
        df_logs = pd.DataFrame(logs)
        st.dataframe(df_logs, use_container_width=True)
    else:
        st.error("Failed to load logs.")
except Exception as e:
    st.error(f"Logs error: {e}")
