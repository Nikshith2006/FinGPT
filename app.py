import streamlit as st
from features.auth import login_page
from features.dashboard import dashboard

st.set_page_config(page_title="FinGPT", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    dashboard()
else:
    login_page()
