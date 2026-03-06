import streamlit as st
import pandas as pd
from datetime import datetime

from features.voice_entry import voice_entry
from features.dashboard_ui import show_metrics_ai_table
from features.dashboard_charts import show_charts_and_suggestions


def dashboard():

    users = pd.read_csv("users.csv")
    expenses = pd.read_csv("expenses.csv")

    user_data = users[users["Name"] == st.session_state.user].iloc[0]

    col1, col2 = st.columns([9,1])

    with col1:
        st.title(f"💼 FinGPT Dashboard | Welcome {st.session_state.user}")

    with col2:
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # ================= SIDEBAR =================

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
    ] = [income, budget]

    users.to_csv("users.csv", index=False)

    st.sidebar.divider()

    st.sidebar.subheader("➕ Add New Expense")

    exp_date = st.sidebar.date_input("📅 Date", datetime.today())

    exp_cat = st.sidebar.selectbox(
        "🏷 Category",
        ["Food","Rent","Shopping","Travel","Entertainment","Transport"]
    )

    exp_amt = st.sidebar.number_input("💵 Amount", min_value=1)
    exp_desc = st.sidebar.text_input("📝 Description")

    if st.sidebar.button("➕ Add Expense"):

        new_row = pd.DataFrame({
            "Date":[exp_date],
            "Category":[exp_cat],
            "Amount":[exp_amt],
            "Description":[exp_desc],
            "User":[st.session_state.user]
        })

        expenses = pd.concat([expenses,new_row],ignore_index=True)

        expenses.to_csv("expenses.csv",index=False)

        st.rerun()

    # ================= VOICE ENTRY =================

    voice_entry(expenses)

    # refresh
    expenses = pd.read_csv("expenses.csv")
    user_expenses = expenses[expenses["User"] == st.session_state.user].copy()
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

    # ================= UI SECTION =================

    show_metrics_ai_table(income, budget, user_expenses, expenses)

    # ================= CHARTS SECTION =================

    show_charts_and_suggestions(income, user_expenses)
