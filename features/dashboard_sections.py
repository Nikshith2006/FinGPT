import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import calendar


# ---------------- EXPENSE TABLE ----------------

def expense_table(expenses, user_expenses):

    st.subheader("📊 Expense Table")

    # ✅ SAFE COPY (fix warning)
    user_expenses = user_expenses.copy()

    # Ensure datetime
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

    df = user_expenses.copy()

    # Remove User column if present
    if "User" in df.columns:
        df = df.drop(columns=["User"])

    # Sort by date
    df = df.sort_values(by="Date", ascending=True)

    # Format date
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Reset index for S.No
    df = df.reset_index(drop=True)
    df.index = df.index + 1
    df.index.name = "S.No"

    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        height=400
    )


# ---------------- CHARTS ----------------

def charts_and_predictions(expenses, user_expenses):

    # ✅ SAFE COPY
    expenses = expenses.copy()
    user_expenses = user_expenses.copy()

    expenses["Date"] = pd.to_datetime(expenses["Date"], errors="coerce")
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

    # ---------------- CATEGORY PIE ----------------

    st.subheader("📊 Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty and cat.sum() > 0:

        fig1, ax1 = plt.subplots()
        ax1.pie(cat, labels=cat.index, autopct="%1.1f%%")

        st.pyplot(fig1)

    else:
        st.info("No category data to display.")

    # ---------------- DAILY BAR ----------------

    st.subheader("📈 Daily Spending")

    daily = user_expenses.groupby(
        user_expenses["Date"].dt.date
    )["Amount"].sum()

    if not daily.empty:

        fig2, ax2 = plt.subplots()
        daily.plot(kind="bar", ax=ax2)

        st.pyplot(fig2)

    else:
        st.info("No daily spending data.")

    # ---------------- MONTHLY TREND ----------------

    st.subheader("📉 Monthly Trend")

    if user_expenses.empty:
        st.info("No monthly data available.")
    else:

        selected_year = user_expenses["Date"].dt.year.iloc[0]

        yearly_data = expenses[
            (expenses["User"] == st.session_state.user) &
            (expenses["Date"].dt.year == selected_year)
        ]

        monthly = yearly_data.groupby(
            yearly_data["Date"].dt.month
        )["Amount"].sum()

        monthly = monthly.reindex(range(1,13), fill_value=0)

        month_names = [
            "Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"
        ]

        fig3, ax3 = plt.subplots()

        ax3.plot(month_names, monthly.values, marker="o")

        ax3.set_xlabel("Month")
        ax3.set_ylabel("Total Spending")

        st.pyplot(fig3)

    # ---------------- PREDICTION ----------------

    st.subheader("🔮 Month-End Prediction")

    cum = user_expenses.groupby(
        user_expenses["Date"].dt.day
    )["Amount"].sum().cumsum()

    if len(cum) > 1 and cum.notnull().all():

        X = np.array(cum.index).reshape(-1,1)
        y = cum.values

        model = LinearRegression()
        model.fit(X,y)

        future = np.array(range(1,31)).reshape(-1,1)
        pred = model.predict(future)

        fig4, ax4 = plt.subplots()

        ax4.plot(cum.index, y, label="Actual")
        ax4.plot(range(1,31), pred, linestyle="--", label="Prediction")

        ax4.legend()

        st.pyplot(fig4)

    else:
        st.info("Not enough data for prediction.")


# ---------------- SMART SUGGESTIONS ----------------

def smart_suggestions(total, budget):

    st.subheader("💡 Smart Suggestions")

    if budget == 0:
        st.warning("⚠ Please set a monthly budget first.")
        return

    percent = (total / budget) * 100

    if percent > 100:

        st.error("🚨 You exceeded your monthly budget!")

        st.write("• 💳 Reduce unnecessary shopping.")
        st.write("• 🍔 Limit food delivery expenses.")
        st.write("• 📊 Track daily expenses carefully.")

    elif percent > 80:

        st.warning("⚠ You already spent more than 80% of your budget.")

        st.write("• 📉 Reduce entertainment spending.")
        st.write("• 🛍 Avoid impulse shopping.")
        st.write("• 💰 Try saving remaining income.")

    elif percent > 50:

        st.info("📊 You used around half of your budget.")

        st.write("• 👍 Your spending is balanced.")
        st.write("• 💡 Keep tracking expenses daily.")

    else:

        st.success("✅ Excellent! Your spending is healthy this month.")

        st.write("• 💰 You are saving well.")
        st.write("• 📈 Consider investing some savings.")
        st.write("• 🧠 Maintain this spending discipline.")
