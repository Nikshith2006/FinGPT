import streamlit as st
import pandas as pd
import requests
from streamlit_oauth import OAuth2Component

GOOGLE_CLIENT_ID = st.secrets["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = st.secrets["GOOGLE_CLIENT_SECRET"]

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"

oauth2 = OAuth2Component(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    AUTHORIZE_URL,
    TOKEN_URL,
    TOKEN_URL
)

def login():

    st.title("🔐 FinGPT Login")

    users = pd.read_csv("users.csv")

    name = st.text_input("Name")
    contact = st.text_input("Email / Phone")

    if st.button("Login"):

        existing = users[(users["Name"]==name)&(users["Contact"]==contact)]

        if existing.empty:
            new = pd.DataFrame({
                "Name":[name],
                "Contact":[contact],
                "MonthlyIncome":[0],
                "MonthlyBudget":[0]
            })

            users = pd.concat([users,new],ignore_index=True)
            users.to_csv("users.csv",index=False)

        st.session_state.user=name
        st.rerun()

    st.markdown("### OR")

    result = oauth2.authorize_button(
        name="Login with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri="https://fingpt20.streamlit.app",
        scope="openid email profile",
        key="google"
    )

    if result and "token" in result:

        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization":f"Bearer {result['token']['access_token']}"}
        ).json()

        st.session_state.user = userinfo["name"]
        st.rerun()