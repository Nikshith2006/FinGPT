import streamlit as st
from dotenv import load_dotenv

from features.auth import login
from features.dashboard import dashboard

if "voice_text" not in st.session_state:
st.session_state.voice_text = ""


st.set_page_config(page_title="FinGPT", layout="wide")

load_dotenv()

if "user" not in st.session_state:
    st.session_state.user = None

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

if st.session_state.user is None:
    login()
else:
    dashboard()

