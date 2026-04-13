import streamlit as st
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from streamlit_oauth import OAuth2Component

# ✅ NEW: import Google Sheets
from database import users_sheet

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# OAuth setup
oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    TOKEN_URL
)


def login():

    st.markdown(
    """
    <h1 style='text-align:center;'>🔐 Finlet</h1>
    <p style='text-align:center;color:gray;font-size:18px;'>
    Smart Budget Monitoring System
    </p>
    """,
    unsafe_allow_html=True
    )

    # ✅ LOAD USERS FROM GOOGLE SHEETS (instead of CSV)
    users = pd.DataFrame(users_sheet.get_all_records())

    # CENTER LOGIN CARD
    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        name = st.text_input("👤 Name")
        contact = st.text_input("📧 Email or Phone")

        if st.button("Login", use_container_width=True):

            existing_user = users[
                (users["Name"] == name) &
                (users["Contact"] == contact)
            ]

            if not existing_user.empty:

                st.session_state.user = name
                st.rerun()

            else:

                # ✅ SAVE TO GOOGLE SHEETS (instead of CSV)
                users_sheet.append_row([
                    name,
                    contact,
                    0,
                    0
                ])

                st.session_state.user = name
                st.rerun()

        # OR divider
        st.markdown(
        """
        <div style="text-align:center;margin:25px 0;color:gray;">
        ─────── OR ───────
        </div>
        """,
        unsafe_allow_html=True
        )

        # GOOGLE LOGIN BUTTON (CENTERED)
        result = oauth2.authorize_button(
            name="Login with Google",
            icon="https://www.google.com/favicon.ico",

            # Local run
            redirect_uri="https://fingpt20.streamlit.app",

            scope="openid email profile",
            key="google",

            use_container_width=True
        )

        if result and "token" in result:

            # ✅ UPDATED API (gets real name properly)
            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={
                    "Authorization": f"Bearer {result['token']['access_token']}"
                },
            ).json()

            name = userinfo.get("name", "")
            email = userinfo.get("email", "")

            # ✅ RELOAD USERS FROM SHEETS
            users = pd.DataFrame(users_sheet.get_all_records())

            existing_user = users[
                (users["Name"] == name) &
                (users["Contact"] == email)
            ]

            if existing_user.empty:

                # ✅ SAVE TO GOOGLE SHEETS
                users_sheet.append_row([
                    name,
                    email,
                    0,
                    0
                ])

            st.session_state.user = name

            st.rerun()
