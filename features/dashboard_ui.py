import streamlit as st
import pandas as pd
from features.ai_assistant import ask_ai


def show_metrics_ai_table(income, budget, user_expenses, expenses):

    # ================= DATE FIX =================

    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")
    expenses["Date"] = pd.to_datetime(expenses["Date"], errors="coerce")

    # ================= MONTH YEAR SELECTOR =================

    st.subheader("📊 Expense Manager")

    col1, col2, col3 = st.columns([2,2,6])

    with col1:
        selected_year = st.selectbox(
            "Year",
            sorted(user_expenses["Date"].dropna().dt.year.unique(), reverse=True)
        )

    with col2:
        selected_month = st.selectbox(
            "Month",
            list(range(1,13)),
            format_func=lambda x: pd.to_datetime(str(x), format="%m").strftime("%B")
        )

    # ================= FILTER DATA =================

    df = expenses[expenses["User"] == st.session_state.user].copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df[
        (df["Date"].dt.year == selected_year) &
        (df["Date"].dt.month == selected_month)
    ]

    df = df.sort_values("Date")

    df = df.reset_index()

    # ================= TABLE HEADER =================

    header = st.columns([1,2,2,2,4,1])

    header[0].markdown("**S.No**")
    header[1].markdown("**Date**")
    header[2].markdown("**Category**")
    header[3].markdown("**Amount**")
    header[4].markdown("**Description**")
    header[5].markdown("")

    # ================= ROWS =================

    for i, row in df.iterrows():

        cols = st.columns([1,2,2,2,4,1])

        cols[0].write(i+1)

        date_value = row["Date"].strftime("%Y-%m-%d") if pd.notna(row["Date"]) else "—"

        cols[1].write(date_value)

        cols[2].write(row["Category"])

        cols[3].write(row["Amount"])

        cols[4].write(row["Description"])

        if cols[5].button("🗑️", key=f"delete_{i}"):

            expenses = expenses.drop(row["index"])

            expenses.to_csv("expenses.csv", index=False)

            st.rerun()

    st.divider()

    # ================= METRICS =================

    monthly_expenses = df["Amount"].sum()

    savings = income - monthly_expenses

    score = 0
    status = "Unknown"

    if income > 0:

        ratio = monthly_expenses / income

        if ratio <= 0.5:
            score = 90
            status = "Excellent"

        elif ratio <= 0.7:
            score = 70
            status = "Good"

        elif ratio <= 0.9:
            score = 50
            status = "Warning"

        else:
            score = 30
            status = "Danger"

    m1,m2,m3,m4,m5 = st.columns(5)

    m1.metric("💰 Income",f"₹ {income}")
    m2.metric("📊 Budget",f"₹ {budget}")
    m3.metric("💸 Spent",f"₹ {monthly_expenses}")
    m4.metric("🏦 Savings",f"₹ {savings}")
    m5.metric("💚 Health Score",f"{score}/100",status)

    st.divider()

    # ================= AI ASSISTANT =================

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if question:

        answer = ask_ai(
            income,
            budget,
            monthly_expenses,
            question
        )

        st.write(answer)

    st.divider()
