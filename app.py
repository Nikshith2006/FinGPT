import streamlit as st
from features.auth import login
from features.dashboard import dashboard

st.set_page_config(page_title="FinGPT", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    login()
else:
    dashboard()
