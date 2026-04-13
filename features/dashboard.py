import streamlit as st
import pandas as pd
from datetime import datetime

from features.ai_assistant import ai_financial_assistant
from features.dashboard_sections import (
    expense_table,
    charts_and_predictions,
    smart_suggestions
)

from database import expenses_sheet, users_sheet

# 🔥 IMPORTANT: CLEAR CACHE ALWAYS
st.cache_data.clear()


def dashboard():

    # ================= LOAD DATA =================
    users = pd.DataFrame(users_sheet.get_all_records())
    expenses = pd.DataFrame(expenses_sheet.get_all_records())

    # ================= CLEAN DATA =================
    expenses.columns = expenses.columns.str.strip()

    # 🔥 FINAL DATE FIX (HANDLE ALL FORMATS)
    expenses["Date"] = pd.to_datetime(
        expenses["Date"],
        errors="coerce"
    )

    # Convert to uniform format
    expenses["Date"] = expenses["Date"].dt.strftime("%Y-%m-%d")

    # Convert back to datetime for filtering
    expenses["Date"] = pd.to_datetime(
        expenses["Date"],
        errors="coerce"
    )

    # CLEAN USER COLUMN
    expenses["User"] = expenses["User"].astype(str).str.strip().str.lower()

    # ALSO CLEAN USERS SHEET
    users["Contact"] = users["Contact"].astype(str).str.strip().str.lower()

    current_user = str(st.session_state.user).strip().lower()

    # ================= USER DATA =================
    user_row = users[users["Contact"] == current_user]

    if user_row.empty:
        users_sheet.append_row([current_user, current_user, 0, 0])
        users = pd.DataFrame(users_sheet.get_all_records())
        users["Contact"] = users["Contact"].astype(str).str.strip().str.lower()
        user_row = users[users["Contact"] == current_user]

    user_data = user_row.iloc[0]

    # ================= HEADER =================
    col1, col2 = st.columns([9,1])

    with col1:
        st.title(f"💼 Finlet Dashboard | Welcome {current_user}")

    with col2:
        if st.button("🚪 Logout"):
            st.session_state.user = None
            st.rerun()

    # ================= MONTH FILTER =================
    st.subheader("📅 Monthly Financial Overview")

    today = datetime.today()

    col1, col2 = st.columns(2)

    with col1:
        month = st.selectbox(
            "Month",
            list(range(1,13)),
            index=today.month-1,
            format_func=lambda x: datetime(2000, x, 1).strftime("%B")
        )

    with col2:
        year = st.selectbox(
            "Year",
            list(range(today.year-5, today.year+1)),
            index=5
        )

    # ================= FILTER DATA =================
    user_expenses = expenses[
        (expenses["User"] == current_user) &
        (expenses["Date"].notna()) &
        (expenses["Date"].dt.month == month) &
        (expenses["Date"].dt.year == year)
    ]

    # DEBUG (you can remove later)
    st.write("Filtered rows:", len(user_expenses))

    # ================= SIDEBAR =================
    st.sidebar.title("⚙️ Financial Settings")

    income = st.sidebar.number_input(
        "💰 Monthly Income",
        value=int(user_data["MonthlyIncome"])
    )

    budget = st.sidebar.number_input(
        "🎯 Monthly Budget",
        value=int(user_data["MonthlyBudget"])
    )

    # UPDATE SHEET
    row_index = users[users["Contact"] == current_user].index[0] + 2

    users_sheet.update(f"C{row_index}", [[income]])
    users_sheet.update(f"D{row_index}", [[budget]])

    st.sidebar.divider()

    # ================= ADD EXPENSE =================
    st.sidebar.subheader("➕ Add Expense")

    exp_date = st.sidebar.date_input("📅 Date", datetime.today())

    exp_cat = st.sidebar.selectbox(
        "Category",
        ["Food","Rent","Shopping","Travel","Entertainment","Transport","Other"]
    )

    exp_amt = st.sidebar.number_input("Amount", min_value=1)

    exp_desc = st.sidebar.text_input("Description")

    if st.sidebar.button("Add Expense"):

        formatted_date = exp_date.strftime("%Y-%m-%d")

        expenses_sheet.append_row([
            formatted_date,
            exp_cat,
            int(exp_amt),
            exp_desc,
            current_user
        ])

        st.success("✅ Expense Added Successfully!")

        # 🔥 FORCE REFRESH
        st.cache_data.clear()

        st.rerun()

    # ================= METRICS =================
    total = user_expenses["Amount"].sum()
    savings = income - total

    health = max(0, 100 - (total / budget * 100)) if budget > 0 else 0

    m1,m2,m3,m4 = st.columns(4)

    m1.metric("💰 Income", f"₹{income}")
    m2.metric("💸 Spent", f"₹{total}")
    m3.metric("🏦 Savings", f"₹{savings}")
    m4.metric("💚 Health", f"{health:.0f}%")

    # ================= AI =================
    ai_financial_assistant(income, budget, total)

    # ================= TABLE =================
    expense_table(expenses, user_expenses)

    # ================= CHARTS =================
    charts_and_predictions(expenses, user_expenses)

    # ================= SUGGESTIONS =================
    smart_suggestions(total, budget)
