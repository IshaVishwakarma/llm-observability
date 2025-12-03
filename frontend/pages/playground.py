import streamlit as st
import requests
import os
import uuid
from dotenv import load_dotenv

# -----------------------------
# 🔧 App Config
# -----------------------------
st.set_page_config(page_title="LLM Observability Dashboard", layout="wide")

load_dotenv()
BACKEND = os.getenv("BACKEND_URL")


# -----------------------------
# 🆔 User Session ID
# -----------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.sidebar.success(f"🔑 Session: {st.session_state.session_id[:8]}...")

# -----------------------------
# ⚡ LLM Response State
# -----------------------------
if "last_response" not in st.session_state:
    st.session_state.last_response = None  # will store: {response, tokens_in...}

# -----------------------------
# 🧠 Playground UI
# -----------------------------
st.title("🧠 LLM Playground")

prompt = st.text_area("Enter your prompt", height=200)

col1, col2 = st.columns(2)

with col1:
    model = st.selectbox(
        "Model",
        [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "openai/gpt-oss-20b"
        ]
    )

with col2:
    temp = st.slider("Temperature", 0.0, 1.0, 0.7)

max_tokens = st.slider("Max Tokens", 32, 2048, 256)

# -----------------------------
# 🚀 Send query
# -----------------------------
if st.button("Send"):
    if not prompt.strip():
        st.warning("Enter a prompt")
        st.stop()

    with st.spinner("Thinking..."):
        payload = {
            "prompt": prompt,
            "model": model,
            "temperature": temp,
            "max_tokens": max_tokens,
            "session_id": st.session_state.session_id
        }

        response = requests.post(f"{BACKEND}/api/v1/llm/query", json=payload)

    if response.status_code == 200:
        st.session_state.last_response = response.json()
    else:
        st.error(f"Backend error: {response.text}")

# -----------------------------------
# 🌟 Show Response (if exists)
# -----------------------------------
if st.session_state.last_response:

    data = st.session_state.last_response

    st.subheader("💬 LLM Response")
    st.success(data["response"])

    st.info(f"Tokens → IN: {data['tokens_in']}  |  OUT: {data['tokens_out']}")
    st.info(f"Latency → {data['latency_ms']} ms")

    request_id = data["request_id"]

    st.subheader("⭐ Give Feedback")

    rating_key = f"rating_{request_id}"
    comment_key = f"comment_{request_id}"

    # ⭐ DO NOT manually set st.session_state[rating_key]
    # Streamlit handles it automatically.

    rating = st.radio(
        "Rate this response:",
        [1, 2, 3, 4, 5],
        horizontal=True,
        key=rating_key
    )

    comment = st.text_area(
        "Additional feedback:",
        key=comment_key
    )

    if st.button("Submit Feedback"):
        res_fb = requests.post(
            f"{BACKEND}/api/v1/llm/feedback",
            json={
                "request_id": request_id,
                "rating": rating,
                "comment": comment
            }
        )

        if res_fb.status_code == 200:
            st.success("Feedback submitted!")
        else:
            st.error("Failed to submit feedback")