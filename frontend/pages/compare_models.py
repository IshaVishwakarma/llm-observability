

import streamlit as st
import requests
import os
from dotenv import load_dotenv
if "session_id" not in st.session_state:
    import uuid
    st.session_state.session_id = str(uuid.uuid4())

load_dotenv()
BACKEND = os.getenv("BACKEND_URL")

st.title("🔍 Compare Two LLM Models")

prompt = st.text_area("Enter your prompt", height=150)

col1, col2 = st.columns(2)

with col1:
    model_a = st.selectbox("Model A", [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-20b"
    ])

with col2:
    model_b = st.selectbox("Model B", [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "openai/gpt-oss-20b"
    ])

temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
max_tokens = st.slider("Max Tokens", 32, 2048, 256)

if st.button("Compare Models"):
    with st.spinner("Running both models..."):
        res = requests.post(
    f"{BACKEND}/api/v1/llm/compare",
    json={
        "prompt": prompt,
        "model_a": model_a,
        "model_b": model_b,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "session_id": st.session_state.session_id   # ← FIXED
    }
)


        if res.status_code != 200:
            st.error("❌ Backend error")
            st.write(res.text)
            st.stop()

        data = res.json()

        # Backend must return model_a and model_b keys
        if "model_a" not in data or "model_b" not in data:
            st.error("❌ Invalid backend response format")
            st.write(data)
            st.stop()

        resultA = data["model_a"]
        resultB = data["model_b"]

        colA, colB = st.columns(2)

        # ------------------------------
        # MODEL A PANEL
        # ------------------------------
        with colA:
            st.subheader(f"🟥 Model A: {resultA.get('name')}")
            st.write(resultA.get("response", "No response"))
            st.info(f"Tokens In: {resultA.get('tokens_in')}")
            st.info(f"Tokens Out: {resultA.get('tokens_out')}")
            st.info(f"Latency: {resultA.get('latency')} ms")

        # ------------------------------
        # MODEL B PANEL
        # ------------------------------
        with colB:
            st.subheader(f"🟦 Model B: {resultB.get('name')}")
            st.write(resultB.get("response", "No response"))
            st.success(f"Tokens In: {resultB.get('tokens_in')}")
            st.success(f"Tokens Out: {resultB.get('tokens_out')}")
            st.success(f"Latency: {resultB.get('latency')} ms")
