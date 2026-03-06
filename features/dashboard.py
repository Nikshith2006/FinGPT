import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from features.voice_entry import voice_entry
from features.ai_assistant import ai_assistant


def dashboard():

    users = pd.read_csv("users.csv")
    expenses = pd.read_csv("expenses.csv")

    user = st.session_state.user

    user_data = users[users["Name"] == user].iloc[0]
    user_expenses = expenses[expenses["User"] == user].copy()

    if not user_expenses.empty:
        user_expenses["Date"] = pd.to_datetime(user_expenses["Date"])

    income = int(user_data["MonthlyIncome"])

    total_spent = user_expenses["Amount"].sum() if not user_expenses.empty else 0
    savings = income - total_spent

    # ---------- HEALTH SCORE ----------
    if income > 0:
        health_score = int((savings / income) * 1000)
    else:
        health_score = 0

    st.title(f"💰 Welcome {user}")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Income", income)
    col2.metric("Spent", total_spent)
    col3.metric("Savings", savings)
    col4.metric("Health Score", f"{health_score} (Average)")

    st.divider()

    # ---------- AI ASSISTANT ----------
    ai_assistant(user_expenses, income)

    # ---------- VOICE ENTRY ----------
    voice_entry(expenses, user)

    st.divider()

    # ---------- EXPENSE TABLE ----------
    st.subheader("📋 Expense Table")

    if not user_expenses.empty:

        user_expenses = user_expenses.reset_index()

        for i, row in user_expenses.iterrows():

            c1, c2, c3, c4, c5, c6 = st.columns([1,2,2,2,3,1])

            c1.write(i+1)
            c2.write(row["Date"].date())
            c3.write(row["Category"])
            c4.write(row["Amount"])
            c5.write(row["Description"])

            if c6.button("🗑", key=f"del{i}"):

                expenses = expenses.drop(row["index"])
                expenses.to_csv("expenses.csv", index=False)
                st.rerun()

    else:
        st.info("No expenses yet")

    st.divider()

    # ---------- CATEGORY PIE ----------
    st.subheader("Category Distribution")

    if not user_expenses.empty:

        cat = user_expenses.groupby("Category")["Amount"].sum()

        fig, ax = plt.subplots()
        ax.pie(cat, labels=cat.index, autopct="%1.1f%%")

        st.pyplot(fig)

    # ---------- DAILY SPENDING ----------
    st.subheader("Daily Spending")

    if not user_expenses.empty:

        daily = user_expenses.groupby(
            user_expenses["Date"].dt.date
        )["Amount"].sum()

        fig2, ax2 = plt.subplots()

        daily.plot(kind="bar", ax=ax2)

        ax2.set_ylabel("Amount")
        ax2.set_xlabel("Date")

        st.pyplot(fig2)

    # ---------- MONTH END PREDICTION ----------
    st.subheader("Month-End Prediction")

    if not user_expenses.empty:

        cum = user_expenses.groupby(
            user_expenses["Date"].dt.day
        )["Amount"].sum().cumsum()

        if len(cum) > 1:

            X = np.array(cum.index).reshape(-1,1)
            y = cum.values

            model = LinearRegression()
            model.fit(X,y)

            future = np.arange(1,31).reshape(-1,1)
            pred = model.predict(future)

            fig3, ax3 = plt.subplots()

            ax3.plot(cum.index, y, label="Actual")
            ax3.plot(range(1,31), pred, "--", label="Prediction")

            ax3.legend()

            st.pyplot(fig3)

    # ---------- SMART SUGGESTIONS ----------
    st.subheader("💡 Smart Suggestions")

    if total_spent > income:

        st.error("You are overspending this month!")

    elif total_spent > income * 0.8:

        st.warning("You are close to your budget limit")

    else:

        st.success("Great! Your spending is healthy")
