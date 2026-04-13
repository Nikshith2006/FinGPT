import streamlit as st
import pandas as pd
from datetime import datetime, date
from features.ai_assistant import ai_financial_assistant
from features.dashboard_sections import (
    expense_table,
    charts_and_predictions,
    smart_suggestions
)

from database import expenses_sheet, users_sheet


def dashboard():

    # ================= LOAD DATA =================

    users = pd.DataFrame(users_sheet.get_all_records())
    expenses = pd.DataFrame(expenses_sheet.get_all_records())

    # ================= FIX DATE ISSUE =================
    expenses["Date"] = pd.to_datetime(
        expenses["Date"],
        format="mixed",
        errors="coerce"
    )

    # -------- FIX: HANDLE NEW USER LOGIN --------

    user_row_data = users[users["Name"] == st.session_state.user]

    if user_row_data.empty:
        users_sheet.append_row([
            st.session_state.user,
            "",
            0,
            0
        ])

        users = pd.DataFrame(users_sheet.get_all_records())
        user_row_data = users[users["Name"] == st.session_state.user]

    user_data = user_row_data.iloc[0]

    # ---------------- HEADER ----------------

    col1, col2 = st.columns([9,1])

    with col1:
        st.title(f"💼 Finlet Dashboard | Welcome {st.session_state.user}")

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

    user_row = users[users["Name"] == st.session_state.user].index[0] + 2
    users_sheet.update(f"C{user_row}", [[income]])
    users_sheet.update(f"D{user_row}", [[budget]])

    st.sidebar.divider()

    # ---------------- ADD EXPENSE (🔥 FINAL FIX) ----------------

    st.sidebar.subheader("➕ Add Expense")

    # ✅ FIX: Force today's date on every load
    if "expense_date" not in st.session_state:
        st.session_state.expense_date = date.today()

    with st.sidebar.form("expense_form", clear_on_submit=True):

        exp_date = st.date_input(
            "📅 Date",
            value=st.session_state.expense_date
        )

        exp_cat = st.selectbox(
            "🏷 Category",
            ["Food","Rent","Shopping","Travel","Entertainment","Transport","Other"]
        )

        exp_amt = st.number_input("💵 Amount", min_value=1)

        exp_desc = st.text_input("📝 Description")

        submitted = st.form_submit_button("Add Expense")

    if submitted:

        # ✅ After submit → reset to today again
        st.session_state.expense_date = date.today()

        exp_datetime = datetime.combine(exp_date, datetime.now().time())

        expenses_sheet.append_row([
            exp_datetime.strftime("%Y-%m-%d %H:%M:%S.%f"),
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

    # ---------------- AI ----------------

    ai_financial_assistant(income, budget, total)

    # ---------------- TABLE ----------------

    expense_table(expenses, user_expenses)

    # ---------------- CHARTS ----------------

    charts_and_predictions(expenses, user_expenses)

    # ---------------- SUGGESTIONS ----------------

    smart_suggestions(total, budget)
