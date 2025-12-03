import streamlit as st
from streamlit_option_menu import option_menu

# MUST be first
st.set_page_config(page_title="LLM Observability Dashboard", layout="wide")

# Hide default Streamlit multipage sidebar
HIDE = """
<style>
section[data-testid="stSidebarNav"] {display: none;}
</style>
"""
st.markdown(HIDE, unsafe_allow_html=True)

# Sidebar Navigation
with st.sidebar:
    selected = option_menu(
        "Navigation",
        ["LLM Playground", "Logs Dashboard" , "Compare Models" ,"User Analytics"],
        icons=["robot", "table"],
        default_index=0,
    )

# Correct paths: pages/ is mandatory in Streamlit
if selected == "LLM Playground":
    st.switch_page("pages/playground.py")

elif selected == "Logs Dashboard":
    st.switch_page("pages/dashboard_logs.py")

elif selected == "Compare Models":
    st.switch_page("pages/compare_models.py")

elif selected == "User Analytics":
    st.switch_page("pages/user_analytics.py")
