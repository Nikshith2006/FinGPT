import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv
import os
import tempfile
import json
import re
from dateutil import parser as date_parser
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from google import genai
from streamlit_oauth import OAuth2Component

# ---------------- CONFIG ----------------
st.set_page_config(page_title="FinGPT", layout="wide")
load_dotenv()

st.markdown("""
<style>
div.stButton > button {
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Gemini API
client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

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

# ---------------- FILE SETUP ----------------
if not os.path.exists("users.csv"):
    pd.DataFrame(columns=[
        "Name","Contact","MonthlyIncome","MonthlyBudget"
    ]).to_csv("users.csv", index=False)

if not os.path.exists("expenses.csv"):
    pd.DataFrame(columns=[
        "Date","Category","Amount","Description","User"
    ]).to_csv("expenses.csv", index=False)

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None

if "edit_mode" not in st.session_state:
    st.session_state.edit_mode = False

# ---------------- DATE DETECTION ----------------
def detect_spoken_date(text):
    text = text.lower()
    today = datetime.today()

    if "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    if "today" in text:
        return today.strftime("%Y-%m-%d")

    match = re.search(r"(\d+)\s+days?\s+ago", text)
    if match:
        return (today - timedelta(days=int(match.group(1)))).strftime("%Y-%m-%d")

    try:
        parsed = date_parser.parse(text, fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except:
        return today.strftime("%Y-%m-%d")

# ---------------- LOGIN PAGE ----------------
def login():

    st.markdown("""
    <h1 style='text-align:center;'>🔐 FinGPT</h1>
    <p style='text-align:center;color:gray;font-size:18px;'>
    Smart Personal Finance Assistant
    </p>
    """, unsafe_allow_html=True)

    users = pd.read_csv("users.csv")

    col1,col2,col3 = st.columns([1,2,1])

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

        st.markdown("<div style='text-align:center;margin:25px'>──── OR ────</div>", unsafe_allow_html=True)

        result = oauth2.authorize_button(
            name="Login with Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri="https://fingpt20.streamlit.app",
            scope="openid email profile",
            key="google",
        )

        if result and "token" in result:

            import requests

            userinfo = requests.get(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                headers={"Authorization": f"Bearer {result['token']['access_token']}"},
            ).json()

            name = userinfo["name"]
            email = userinfo["email"]

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

# ---------------- DASHBOARD ----------------
def dashboard():

    users = pd.read_csv("users.csv")
    expenses = pd.read_csv("expenses.csv")

    user_data = users[users["Name"] == st.session_state.user].iloc[0]

    user_expenses = expenses[expenses["User"] == st.session_state.user].copy()
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

    col1,col2 = st.columns([9,1])

    with col1:
        st.title(f"💼 FinGPT Dashboard | Welcome {st.session_state.user}")

    with col2:
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("⚙️ Financial Settings")

    income = st.sidebar.number_input("💰 Monthly Income", value=int(user_data["MonthlyIncome"]))
    budget = st.sidebar.number_input("📊 Monthly Budget", value=int(user_data["MonthlyBudget"]))

    users.loc[
        users["Name"] == st.session_state.user,
        ["MonthlyIncome","MonthlyBudget"]
    ] = [income,budget]

    users.to_csv("users.csv",index=False)

    st.sidebar.subheader("➕ Add Expense")

    exp_date = st.sidebar.date_input("Date", datetime.today())
    exp_cat = st.sidebar.selectbox("Category",["Food","Rent","Shopping","Travel","Entertainment","Transport"])
    exp_amt = st.sidebar.number_input("Amount",min_value=1)
    exp_desc = st.sidebar.text_input("Description")

    if st.sidebar.button("Add Expense"):
        new_row = pd.DataFrame({
            "Date":[exp_date.strftime("%Y-%m-%d")],
            "Category":[exp_cat],
            "Amount":[exp_amt],
            "Description":[exp_desc],
            "User":[st.session_state.user]
        })
        expenses = pd.concat([expenses,new_row],ignore_index=True)
        expenses.to_csv("expenses.csv",index=False)
        st.rerun()

    # ---------------- VOICE ENTRY ----------------
    st.subheader("🎤 Smart Voice Entry")

    audio = mic_recorder(
        start_prompt="🎙 Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        use_container_width=True
    )

    if audio:

        try:

            st.success("✅ Recording Finished")

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(audio["bytes"])
                audio_path = tmp.name

            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            detected_date = detect_spoken_date(text)
            text_lower = text.lower()

            amount_match = re.search(r"\d+", text_lower)
            amount = int(amount_match.group()) if amount_match else 0

            if "food" in text_lower:
                category = "Food"
            elif "rent" in text_lower:
                category = "Rent"
            elif "shopping" in text_lower:
                category = "Shopping"
            elif "travel" in text_lower:
                category = "Travel"
            elif "movie" in text_lower:
                category = "Entertainment"
            elif "bus" in text_lower:
                category = "Transport"
            else:
                category = "Food"

            if amount == 0:
                st.error("Could not detect amount.")
                st.stop()

            new_row = pd.DataFrame({
                "Date":[detected_date],
                "Category":[category],
                "Amount":[amount],
                "Description":[text],
                "User":[st.session_state.user]
            })

            expenses = pd.concat([expenses,new_row],ignore_index=True)
            expenses.to_csv("expenses.csv",index=False)

            st.success("Expense Added Successfully!")
            st.rerun()

        except Exception as e:
            st.error("Voice feature failed")
            st.write(e)

    # ---------------- AI ASSISTANT ----------------
    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if question:

        context = f"""
        Income: {income}
        Budget: {budget}
        Total Spent: {user_expenses['Amount'].sum()}
        """

        reply = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=context + question
        )

        st.write(reply.text)

    # ---------------- EXPENSE TABLE ----------------
    st.subheader("📊 Expense Manager")

    df = expenses[expenses["User"] == st.session_state.user].copy()

    for i,row in df.reset_index().iterrows():

        cols = st.columns([2,2,1,3,1])

        cols[0].write(row["Date"])
        cols[1].write(row["Category"])
        cols[2].write(row["Amount"])
        cols[3].write(row["Description"])

        if cols[4].button("🗑️",key=i):

            expenses = expenses.drop(row["index"])
            expenses.to_csv("expenses.csv",index=False)
            st.rerun()

    # ---------------- METRICS ----------------
    total = user_expenses["Amount"].sum()
    savings = income - total

    m1,m2,m3 = st.columns(3)

    m1.metric("Income",f"₹{income}")
    m2.metric("Spent",f"₹{total}")
    m3.metric("Savings",f"₹{savings}")

    # ---------------- CHARTS ----------------
    st.subheader("Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty:
        fig,ax = plt.subplots()
        ax.pie(cat,labels=cat.index,autopct="%1.1f%%")
        st.pyplot(fig)

# ---------------- MAIN ----------------
if st.session_state.user is None:
    login()
else:
    dashboard()
