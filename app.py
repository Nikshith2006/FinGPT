import streamlit as st
from dotenv import load_dotenv
import os

from features.auth import login
from features.dashboard import dashboard

st.set_page_config(page_title="FinGPT", layout="wide")

load_dotenv()

# Session setup
if "user" not in st.session_state:
    st.session_state.user = None

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# Routing
if st.session_state.user is None:
    login()
else:
    dashboard()
