import streamlit as st
import pandas as pd
from datetime import datetime
from features.ai_assistant import ai_financial_assistant
from features.dashboard_sections import (
    expense_table,
    charts_and_predictions,
    smart_suggestions
)

# NEW IMPORT FOR GOOGLE SHEETS
from database import expenses_sheet, users_sheet


def dashboard():

    # READ DATA FROM GOOGLE SHEETS
    users = pd.DataFrame(users_sheet.get_all_records())
    expenses = pd.DataFrame(expenses_sheet.get_all_records())

    # Ensure Date column is datetime
    expenses["Date"] = pd.to_datetime(expenses["Date"], errors="coerce")

    user_data = users[users["Name"] == st.session_state.user].iloc[0]

    # ---------------- HEADER ----------------

    col1, col2 = st.columns([9,1])

    with col1:
        st.title(f"💼 FinGPT Dashboard | Welcome {st.session_state.user}")

    with col2:
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # ---------------- MONTH YEAR FILTER ----------------

    st.subheader("📅 Monthly Financial Overview")

    today = datetime.today()

    month_names = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]

    current_month = today.month
    current_year = today.year

    years = list(range(current_year - 9, current_year + 1))

    colm1, colm2 = st.columns(2)

    with colm1:

        selected_month_name = st.selectbox(
            "📆 Month",
            month_names,
            index=current_month - 1
        )

        selected_month = month_names.index(selected_month_name) + 1

    with colm2:

        selected_year = st.selectbox(
            "📅 Year",
            years,
            index=years.index(current_year)
        )

    # ---------------- FILTER USER DATA ----------------

    user_expenses = expenses[
        (expenses["User"] == st.session_state.user) &
        (expenses["Date"].dt.month == selected_month) &
        (expenses["Date"].dt.year == selected_year)
    ].copy()

    # ---------------- SIDEBAR ----------------

    st.sidebar.title("⚙️ Financial Settings")

    income = st.sidebar.number_input(
        "💰 Monthly Income",
        value=int(user_data["MonthlyIncome"])
    )

    budget = st.sidebar.number_input(
        "🎯 Monthly Budget",
        value=int(user_data["MonthlyBudget"])
    )

    # UPDATE USER DATA IN GOOGLE SHEETS
    user_row = users[users["Name"] == st.session_state.user].index[0] + 2
    users_sheet.update(f"C{user_row}", [[income]])
    users_sheet.update(f"D{user_row}", [[budget]])

    st.sidebar.divider()

    # ---------------- MANUAL EXPENSE ENTRY ----------------

    st.sidebar.subheader("➕ Add Expense")

    exp_date = st.sidebar.date_input("📅 Date", datetime.today())

    exp_cat = st.sidebar.selectbox(
        "🏷 Category",
        ["Food","Rent","Shopping","Travel","Entertainment","Transport","Other"]
    )

    exp_amt = st.sidebar.number_input("💵 Amount", min_value=1)

    exp_desc = st.sidebar.text_input("📝 Description")

    if st.sidebar.button("Add Expense"):

        exp_date = pd.to_datetime(exp_date)

        # ADD NEW ROW TO GOOGLE SHEETS
        expenses_sheet.append_row([
            exp_date.strftime("%Y-%m-%d"),
            exp_cat,
            exp_amt,
            exp_desc,
            st.session_state.user
        ])

        st.success("Expense Added Successfully!")

        st.rerun()

    # ---------------- METRICS ----------------

    total = user_expenses["Amount"].sum()

    savings = income - total

    health_score = max(0, 100 - (total / budget * 100)) if budget > 0 else 0

    # -------- HEALTH SCORE LABEL --------

    if health_score >= 90:
        health_label = "Excellent"

    elif health_score >= 75:
        health_label = "Good"

    elif health_score >= 60:
        health_label = "Moderate"

    elif health_score >= 40:
        health_label = "Poor"

    else:
        health_label = "Bad"

    m1,m2,m3,m4 = st.columns(4)

    m1.metric("💰 Income", f"₹{income}")
    m2.metric("💸 Spent", f"₹{total}")
    m3.metric("🏦 Savings", f"₹{savings}")
    m4.metric("💚 Health Score", f"{health_score:.0f}% ({health_label})")

    # ---------------- AI FINANCIAL ASSISTANT ----------------

    ai_financial_assistant(income, budget, total)

    # ---------------- EXPENSE TABLE ----------------

    expense_table(expenses, user_expenses)

    # ---------------- CHARTS ----------------

    charts_and_predictions(expenses, user_expenses)

    # ---------------- SMART SUGGESTIONS ----------------

    smart_suggestions(total, budget)
