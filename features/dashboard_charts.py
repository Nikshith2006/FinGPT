import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def show_charts_and_suggestions(income, user_expenses):

    # ================= CATEGORY CHART =================

    st.subheader("📊 Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty:

        fig1,ax1 = plt.subplots()

        ax1.pie(cat,labels=cat.index,autopct="%1.1f%%")

        st.pyplot(fig1)

    # ================= DAILY SPENDING =================

    st.subheader("📊 Daily Spending")

    daily = user_expenses.groupby(user_expenses["Date"].dt.date)["Amount"].sum()

    if not daily.empty:

        daily = daily.sort_index()

        fig2,ax2 = plt.subplots()

        ax2.bar(daily.index,daily.values)

        ax2.set_xlabel("Date")
        ax2.set_ylabel("Amount")

        plt.xticks(rotation=90)

        st.pyplot(fig2)

    # ================= MONTHLY TREND =================

    st.subheader("📉 Monthly Trend")

    monthly = user_expenses.groupby(user_expenses["Date"].dt.day)["Amount"].sum()

    if not monthly.empty:

        monthly = monthly.sort_index()

        fig3,ax3 = plt.subplots()

        ax3.plot(monthly.index,monthly.values,marker="o")

        ax3.set_xlabel("Date")
        ax3.set_ylabel("Amount")

        ax3.grid(True)

        st.pyplot(fig3)

    # ================= PREDICTION =================

    st.subheader("🔮 Month-End Prediction")

    cum = user_expenses.groupby(user_expenses["Date"].dt.day)["Amount"].sum().cumsum()

    if len(cum) > 1:

        X = np.array(cum.index).reshape(-1,1)

        y = cum.values

        model = LinearRegression()

        model.fit(X,y)

        future = np.array(range(1,31)).reshape(-1,1)

        pred = model.predict(future)

        fig4,ax4 = plt.subplots()

        ax4.plot(cum.index,y,label="Actual")

        ax4.plot(range(1,31),pred,"--",label="Prediction")

        ax4.set_xlabel("Day")
        ax4.set_ylabel("Cumulative Spending")

        ax4.legend()

        st.pyplot(fig4)

    st.divider()

    # ================= SMART SUGGESTIONS =================

    st.subheader("💡 Smart Suggestions")

    total = user_expenses["Amount"].sum()

    suggestions = []

    if not cat.empty:
        suggestions.append(f"Highest spending category: {cat.idxmax()}")

    if income - total < 0:
        suggestions.append("You are overspending. Reduce unnecessary expenses.")

    suggestions.append("Review budget weekly.")
    suggestions.append("Avoid impulse purchases.")
    suggestions.append("Plan major expenses in advance.")
    suggestions.append("Track expenses daily for better control.")
    suggestions.append("Set monthly spending limits.")
    suggestions.append("Use savings goals to stay motivated.")

    for s in suggestions:
        st.write(f"• {s}")
