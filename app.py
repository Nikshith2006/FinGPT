import streamlit as st
from dotenv import load_dotenv

from features.auth import login
from features.dashboard import dashboard

# ================= VOICE SESSION =================

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

# ================= PAGE CONFIG =================

st.set_page_config(page_title="FinGPT", layout="wide")

load_dotenv()

# ================= USER SESSION =================

if "user" not in st.session_state:
    st.session_state.user = None

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# ================= APP ROUTING =================

if st.session_state.user is None:
    login()
else:
    dashboard()
