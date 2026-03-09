import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from auth import login
from features.dashboard import dashboard

st.set_page_config(page_title="FinGPT", layout="wide")

if "user" not in st.session_state:
    st.session_state.user=None

if st.session_state.user is None:
    login()
else:
    dashboard()

