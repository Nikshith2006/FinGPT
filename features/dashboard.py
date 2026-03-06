import streamlit as st
import pandas as pd
from features.ai_assistant import ai_assistant
from features.charts import show_charts
from features.voice_entry import voice_entry
from features.utils import detect_spoken_date

def dashboard():

    users = pd.read_csv("users.csv")
    expenses = pd.read_csv("expenses.csv")

    user_data = users[users["Name"] == st.session_state.user].iloc[0]

    income = int(user_data["MonthlyIncome"])
    budget = int(user_data["MonthlyBudget"])

    df = expenses[expenses["User"]==st.session_state.user]

    total = df["Amount"].sum()
    savings = income-total

    st.title(f"💰 Welcome {st.session_state.user}")

    c1,c2,c3 = st.columns(3)

    c1.metric("Income",income)
    c2.metric("Spent",total)
    c3.metric("Savings",savings)

    ai_assistant(income,budget,total)

    voice_entry(expenses, st.session_state.user, detect_spoken_date)


    show_charts(df)


