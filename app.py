import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from dotenv import load_dotenv
import os
import tempfile
import re
from dateutil import parser as date_parser
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from google import genai
from streamlit_oauth import OAuth2Component

# ---------------- CONFIG ----------------
st.set_page_config(page_title="FinGPT", layout="wide")
load_dotenv()

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
    pd.DataFrame(columns=["Name","Contact","MonthlyIncome","MonthlyBudget"]).to_csv("users.csv", index=False)

if not os.path.exists("expenses.csv"):
    pd.DataFrame(columns=["Date","Category","Amount","Description","User"]).to_csv("expenses.csv", index=False)

# ---------------- SESSION ----------------
if "user" not in st.session_state:
    st.session_state.user = None


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


# ---------------- HEALTH SCORE ----------------
def calculate_health_score(income, spent):
    if income == 0:
        return 300
    ratio = spent / income
    score = 900 - int(ratio * 600)
    return max(300, min(score, 900))


# ---------------- LOGIN ----------------
def login():

    st.markdown("<h1 style='text-align:center;color:#00f5d4;'>🔐 FinGPT</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;'>Smart Personal Finance Assistant</h4>", unsafe_allow_html=True)

    users = pd.read_csv("users.csv")

    name = st.text_input("👤 Name")
    contact = st.text_input("📧 Email or Phone")

    if st.button("Login"):

        existing_user = users[(users["Name"] == name) & (users["Contact"] == contact)]

        if existing_user.empty:
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

    st.markdown("### OR")

    result = oauth2.authorize_button(
        name="Login with Google",
        icon="https://www.google.com/favicon.ico",
        redirect_uri="https://fingpt20.streamlit.app",
        scope="openid email profile",
        key="google"
    )

    if result and "token" in result:

        import requests

        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v1/userinfo",
            headers={"Authorization": f"Bearer {result['token']['access_token']}"},
        ).json()

        name = userinfo["name"]
        email = userinfo["email"]

        if not ((users["Name"] == name) & (users["Contact"] == email)).any():

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

    df = expenses[expenses["User"] == st.session_state.user].copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    st.markdown(f"<h1 style='color:#00f5d4;'>💰 Welcome {st.session_state.user}</h1>", unsafe_allow_html=True)

    # -------- Sidebar --------
    st.sidebar.header("⚙ Financial Settings")

    income = st.sidebar.number_input("💵 Monthly Income", value=int(user_data["MonthlyIncome"]), min_value=0)
    budget = st.sidebar.number_input("🎯 Monthly Budget", value=int(user_data["MonthlyBudget"]), min_value=0)

    users.loc[users["Name"] == st.session_state.user,["MonthlyIncome","MonthlyBudget"]] = [income,budget]
    users.to_csv("users.csv",index=False)

    st.sidebar.header("➕ Add Expense")

    with st.sidebar.form("add_expense"):
        date = st.date_input("Date", datetime.today())
        category = st.selectbox("Category",["Food","Rent","Shopping","Travel","Entertainment","Transport"])
        amount = st.number_input("Amount", min_value=1)
        desc = st.text_input("Description")

        submit = st.form_submit_button("Add Expense")

        if submit:

            new_row = pd.DataFrame({
                "Date":[date.strftime("%Y-%m-%d")],
                "Category":[category],
                "Amount":[amount],
                "Description":[desc],
                "User":[st.session_state.user]
            })

            expenses = pd.concat([expenses,new_row],ignore_index=True)
            expenses.to_csv("expenses.csv",index=False)

            st.rerun()

    # -------- Voice Entry --------
    st.subheader("🎤 Voice Entry")

    audio = mic_recorder(start_prompt="🎙 Start Recording", stop_prompt="⏹ Stop Recording", just_once=True)

    if audio:

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            audio_path = tmp.name

        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)

        st.success(f"You said: {text}")

    # -------- AI Assistant --------
    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if question:

        context = f"""
        Income: {income}
        Budget: {budget}
        Total Spent: {df['Amount'].sum()}
        """

        reply = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=context + question
        )

        st.write(reply.text)

    if df.empty:
        st.warning("No expense data available.")
        return

    total_spent = df["Amount"].sum()
    savings = income - total_spent

    health_score = calculate_health_score(income,total_spent)

    if health_score >= 750:
        rating="Excellent"
    elif health_score >=650:
        rating="Good"
    elif health_score >=550:
        rating="Average"
    else:
        rating="Poor"

    # -------- Metrics --------
    col1,col2,col3,col4 = st.columns(4)

    col1.metric("💰 Income",f"₹ {income}")
    col2.metric("💸 Total Spent",f"₹ {total_spent}")
    col3.metric("💵 Savings",f"₹ {savings}")
    col4.metric("🏦 Health Score",f"{health_score} ({rating})")

    if budget>0:
        st.progress(min(total_spent/budget,1.0))

    # -------- Expense Table --------
    st.subheader("📋 Expense Table")

    for i,row in df.reset_index().iterrows():

        c1,c2,c3,c4,c5 = st.columns([2,2,1,3,1])

        c1.write(row["Date"].date())
        c2.write(row["Category"])
        c3.write(row["Amount"])
        c4.write(row["Description"])

        if c5.button("🗑",key=i):

            expenses = expenses.drop(row["index"])
            expenses.to_csv("expenses.csv",index=False)

            st.rerun()

    # -------- Charts --------
    st.subheader("📊 Category Distribution")

    cat = df.groupby("Category")["Amount"].sum()

    fig1,ax1 = plt.subplots()
    ax1.pie(cat,labels=cat.index,autopct="%1.1f%%")
    st.pyplot(fig1)

    st.subheader("📈 Daily Spending")

    daily = df.groupby(df["Date"].dt.date)["Amount"].sum()

    fig2,ax2 = plt.subplots()
    daily.plot(kind="bar",ax=ax2)
    st.pyplot(fig2)

    st.subheader("📉 Monthly Trend")

    monthly = df.groupby(df["Date"].dt.day)["Amount"].sum()

    fig3,ax3 = plt.subplots()
    monthly.plot(marker="o",ax=ax3)
    st.pyplot(fig3)

    # -------- Month End Prediction --------
    st.subheader("🔮 Month-End Prediction")

    cum = df.groupby(df["Date"].dt.day)["Amount"].sum().cumsum()

    if len(cum)>1:

        X = np.array(cum.index).reshape(-1,1)
        y = cum.values

        model = LinearRegression()
        model.fit(X,y)

        future_days = np.array(range(1,31)).reshape(-1,1)
        predictions = model.predict(future_days)

        fig4,ax4 = plt.subplots()

        ax4.plot(cum.index,y,label="Actual Spending")
        ax4.plot(range(1,31),predictions,"--",label="Prediction")

        ax4.legend()

        st.pyplot(fig4)

    # -------- Smart Suggestions --------
    st.subheader("🤖 Smart Suggestions")

    highest = cat.idxmax()

    suggestions=[
        f"Highest spending category: {highest}",
        "Maintain at least 20% savings.",
        "Reduce unnecessary expenses.",
        "Review budget weekly.",
        "Avoid impulse purchases.",
        "Plan major expenses in advance."
    ]

    for s in suggestions:
        st.write("•",s)

    if st.button("Logout"):
        st.session_state.user=None
        st.rerun()


# ---------------- MAIN ----------------
if st.session_state.user is None:
    login()
else:
    dashboard()
