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

# Professional Button Styling
st.markdown("""
<style>
div.stButton > button {
    border-radius: 10px;
    height: 3em;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
 
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
REFRESH_TOKEN_URL = TOKEN_URL

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
        "Name","Contact",
        "MonthlyIncome","MonthlyBudget"
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

    if "day before yesterday" in text:
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")
    elif "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in text:
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

        result = oauth2.authorize_button(
            name="Login with Google",
            icon="https://www.google.com/favicon.ico",
            redirect_uri="http://localhost:8501",
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
        if st.button("🚪 Logout", help="Sign out from FinGPT"):
            st.session_state.user = None
            st.rerun()

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("⚙️ Financial Settings")

    income = st.sidebar.number_input(
        "💰 Monthly Income",
        value=int(user_data["MonthlyIncome"])
    )

    budget = st.sidebar.number_input(
        "📊 Monthly Budget",
        value=int(user_data["MonthlyBudget"])
    )

    users.loc[
        users["Name"] == st.session_state.user,
        ["MonthlyIncome","MonthlyBudget"]
    ] = [income,budget]

    users.to_csv("users.csv",index=False)

    st.sidebar.divider()
    st.sidebar.subheader("➕ Add New Expense")

    exp_date = st.sidebar.date_input("📅 Date", datetime.today())
    exp_cat = st.sidebar.selectbox(
        "🏷 Category",
        ["Food","Rent","Shopping",
         "Travel","Entertainment","Transport"]
    )
    exp_amt = st.sidebar.number_input("💵 Amount", min_value=1)
    exp_desc = st.sidebar.text_input("📝 Description")

    if st.sidebar.button("➕ Add Expense"):
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

record_placeholder = st.empty()

audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹ Stop Recording",
    just_once=True,
    use_container_width=True
)

if audio:

    try:

        record_placeholder.markdown(
        """
        <div style="text-align:center;font-size:30px;color:green;">
        ✅ Recording Finished
        </div>
        """,
        unsafe_allow_html=True
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio["bytes"])
            audio_path = tmp.name

        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)
        except:
            st.error("Could not understand audio.")
            return

        st.success(f"You said: {text}")

        detected_date = detect_spoken_date(text)
        text_lower = text.lower()

        amount_match = re.search(r"\d+", text_lower)
        amount = int(amount_match.group()) if amount_match else 0

        if any(word in text_lower for word in ["food","dinner","lunch","breakfast"]):
            category = "Food"
        elif "rent" in text_lower:
            category = "Rent"
        elif any(word in text_lower for word in ["shopping","buy","clothes"]):
            category = "Shopping"
        elif any(word in text_lower for word in ["travel","trip"]):
            category = "Travel"
        elif any(word in text_lower for word in ["movie","entertainment"]):
            category = "Entertainment"
        elif any(word in text_lower for word in ["bus","metro","ticket"]):
            category = "Transport"
        else:
            category = "Food"

        if amount == 0:
            st.error("Could not detect amount.")
            return

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

    # ---------------- ASK FINGPT ----------------
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

    st.divider()

    # ---------------- TABLE ----------------
    st.subheader("📊 Expense Manager")

    col1,col2 = st.columns([9,1])

    with col2:
        if st.button("✏️"):
            st.session_state.edit_mode = not st.session_state.edit_mode

    df = expenses[expenses["User"] == st.session_state.user].copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Date"] = df["Date"].fillna(datetime.today())
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    if st.session_state.edit_mode:

        edited = st.data_editor(
            df[["Date","Category","Amount","Description"]],
            use_container_width=True
        )

        if st.button("💾 Save Changes"):
            expenses.loc[df.index,
                         ["Date","Category","Amount","Description"]] = edited
            expenses.to_csv("expenses.csv", index=False)
            st.session_state.edit_mode = False
            st.rerun()

    else:

        for i,row in df.reset_index().iterrows():

            cols = st.columns([2,2,1,3,1])

            cols[0].write(row["Date"])
            cols[1].write(row["Category"])
            cols[2].write(row["Amount"])
            cols[3].write(row["Description"])

            if cols[4].button("🗑️", key=f"del{i}"):

                expenses = expenses.drop(row["index"])
                expenses.to_csv("expenses.csv", index=False)
                st.rerun()

    # ---------------- METRICS ----------------
    total = user_expenses["Amount"].sum()
    savings = income - total

    m1,m2,m3 = st.columns(3)

    m1.metric("💰 Income",f"₹ {income}")
    m2.metric("💸 Spent",f"₹ {total}")
    m3.metric("🏦 Savings",f"₹ {savings}")

    # ---------------- CHARTS ----------------
    st.subheader("📊 Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty:
        fig1,ax1 = plt.subplots()
        ax1.pie(cat,labels=cat.index,autopct="%1.1f%%")
        st.pyplot(fig1)

    st.subheader("📈 Daily Spending")

    daily = user_expenses.groupby(
        user_expenses["Date"].dt.date
    )["Amount"].sum()

    if not daily.empty:
        fig2,ax2 = plt.subplots()
        daily.plot(kind="bar",ax=ax2)
        st.pyplot(fig2)

    st.subheader("🔮 Month-End Prediction")

    cum = user_expenses.groupby(
        user_expenses["Date"].dt.day
    )["Amount"].sum().cumsum()

    if len(cum) > 1:
        X = np.array(cum.index).reshape(-1,1)
        y = cum.values
        model = LinearRegression()
        model.fit(X,y)

        future = np.array(range(1,31)).reshape(-1,1)
        pred = model.predict(future)

        fig3,ax3 = plt.subplots()
        ax3.plot(cum.index,y)
        ax3.plot(range(1,31),pred,linestyle="--")
        st.pyplot(fig3)

# ---------------- MAIN ----------------
if st.session_state.user is None:
    login()
else:

    dashboard()




