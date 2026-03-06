import streamlit as st
import pandas as pd
import os
import requests
from dotenv import load_dotenv
from streamlit_oauth import OAuth2Component

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

# Initialize OAuth
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
    <h1 style='text-align:center;'>🔐 FinGPT</h1>
    <p style='text-align:center;color:gray;font-size:18px;'>
    Smart Personal Finance Assistant
    </p>
    """,
    unsafe_allow_html=True
    )

    users = pd.read_csv("users.csv")

    # Center layout
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

                new_user = pd.DataFrame({
                    "Name":[name],
                    "Contact":[contact],
                    "MonthlyIncome":[0],
                    "MonthlyBudget":[0]
                })

                users = pd.concat([users,new_user],ignore_index=True)

                users.to_csv("users.csv",index=False)

                st.session_state.user = name
                st.rerun()

        st.markdown(
        """
        <div style="text-align:center;margin:25px 0;color:gray;">
        ───────────── OR ─────────────
        </div>
        """,
        unsafe_allow_html=True
        )

        # GOOGLE LOGIN BUTTON (CENTERED)
        result = oauth2.authorize_button(
            name="Login with Google",
            icon="https://www.google.com/favicon.ico",

            # IMPORTANT: Use deployed Streamlit URL
            redirect_uri="https://fingpt20.streamlit.app",

            scope="openid email profile",
            key="google",
            use_container_width=True
        )

        if result and "token" in result:

            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={
                    "Authorization": f"Bearer {result['token']['access_token']}"
                },
            ).json()

            name = userinfo["name"]
            email = userinfo["email"]

            users = pd.read_csv("users.csv")

            existing_user = users[
                (users["Name"] == name) &
                (users["Contact"] == email)
            ]

            if existing_user.empty:

                new_user = pd.DataFrame({
                    "Name":[name],
                    "Contact":[email],
                    "MonthlyIncome":[0],
                    "MonthlyBudget":[0]
                })

                users = pd.concat([users,new_user],ignore_index=True)

                users.to_csv("users.csv",index=False)

            st.session_state.user = name
            st.rerun()
