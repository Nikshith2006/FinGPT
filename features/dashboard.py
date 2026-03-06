import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.linear_model import LinearRegression

from features.voice_entry import voice_entry
from features.ai_assistant import ask_ai


def dashboard():

    users = pd.read_csv("users.csv")
    expenses = pd.read_csv("expenses.csv")

    user_data = users[users["Name"] == st.session_state.user].iloc[0]

    user_expenses = expenses[expenses["User"] == st.session_state.user].copy()

    # Fix date parsing
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

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
            "Date":[pd.to_datetime(exp_date)],
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

    # ================= METRICS =================

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

    m1, m2, m3, m4, m5 = st.columns(5)

    m1.metric("💰 Income", f"₹ {income}")
    m2.metric("📊 Budget", f"₹ {budget}")
    m3.metric("💸 Spent", f"₹ {total}")
    m4.metric("🏦 Savings", f"₹ {savings}")
    m5.metric("💚 Health Score", f"{score}/100", status)

    # ================= EXPENSE TABLE =================

    st.subheader("📊 Expense Manager")

    df = expenses[expenses["User"] == st.session_state.user].copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    df = df.sort_values(by="Date", ascending=False)

    df = df.reset_index(drop=True)

    df.insert(0,"S.No",range(1,len(df)+1))

    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        df[["S.No","Date","Category","Amount","Description"]],
        use_container_width=True,
        hide_index=True
    )

    # ================= CATEGORY CHART =================

    st.subheader("📊 Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty:

        fig1, ax1 = plt.subplots()

        ax1.pie(cat, labels=cat.index, autopct="%1.1f%%")

        st.pyplot(fig1)

    # ================= DAILY SPENDING =================

    st.subheader("📈 Daily Spending")

    daily = user_expenses.groupby(user_expenses["Date"].dt.date)["Amount"].sum()

    if not daily.empty:

        daily = daily.sort_index()

        fig2, ax2 = plt.subplots()

        ax2.plot(daily.index, daily.values, marker="o")

        ax2.set_xlabel("Date")

        ax2.set_ylabel("Amount")

        plt.xticks(rotation=45)

        st.pyplot(fig2)

    # ================= MONTHLY TREND =================

    st.subheader("📉 Monthly Trend")

    monthly = user_expenses.groupby(
        user_expenses["Date"].dt.to_period("M")
    )["Amount"].sum()

    if not monthly.empty:

        monthly = monthly.sort_index()

        monthly.index = monthly.index.astype(str)

        fig4, ax4 = plt.subplots()

        ax4.plot(monthly.index, monthly.values, marker="o")

        ax4.set_xlabel("Month")

        ax4.set_ylabel("Total Spending")

        ax4.grid(True)

        st.pyplot(fig4)

    # ================= PREDICTION =================

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

        fig3, ax3 = plt.subplots()

        ax3.plot(cum.index, y, label="Actual")

        ax3.plot(range(1,31), pred, "--", label="Prediction")

        ax3.set_xlabel("Day of Month")

        ax3.set_ylabel("Cumulative Spending")

        ax3.legend()

        st.pyplot(fig3)

    # ================= SMART SUGGESTIONS =================

    st.subheader("😊 Smart Suggestions")

    suggestions = []

    if not user_expenses.empty:

        highest = user_expenses.groupby("Category")["Amount"].sum().idxmax()

        suggestions.append(f"Highest spending category: {highest}")

    suggestions.append("Maintain at least 20% savings.")

    suggestions.append("Reduce unnecessary expenses.")

    suggestions.append("Review budget weekly.")

    suggestions.append("Avoid impulse purchases.")

    suggestions.append("Plan major expenses in advance.")

    suggestions.append("Track expenses daily for better control.")

    suggestions.append("Set monthly spending limits.")

    suggestions.append("Use savings goals to stay motivated.")

    suggestions.append("Monitor high spending categories.")

    suggestions.append("Balance needs vs wants before spending.")

    for s in suggestions:
        st.write(f"• {s}")

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
