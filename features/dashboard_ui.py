import streamlit as st
import pandas as pd

from features.ai_assistant import ask_ai


def show_metrics_ai_table(income, budget, user_expenses, expenses):

    total = user_expenses["Amount"].sum()
    savings = income - total

    score = 0
    status = "Unknown"

    if income > 0:

        ratio = total / income

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
    m3.metric("💸 Spent",f"₹ {total}")
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
            user_expenses["Amount"].sum(),
            question
        )

        st.write(answer)

    st.divider()

    # ================= EXPENSE TABLE =================

    st.subheader("📊 Expense Manager")

    df = expenses[expenses["User"] == st.session_state.user].copy()

    df["Date"] = pd.to_datetime(df["Date"],errors="coerce")

    df = df.sort_values("Date")

    df = df.reset_index(drop=True)

    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        df[["Date","Category","Amount","Description"]],
        use_container_width=True
    )

    st.divider()
