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
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

    col1,col2 = st.columns([9,1])

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
    ] = [income,budget]

    users.to_csv("users.csv",index=False)

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
            "Date":[exp_date.strftime("%Y-%m-%d")],
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

    m1,m2,m3 = st.columns(3)

    m1.metric("💰 Income",f"₹ {income}")
    m2.metric("💸 Spent",f"₹ {total}")
    m3.metric("🏦 Savings",f"₹ {savings}")

    # ================= HEALTH SCORE =================

    st.subheader("💚 Financial Health Score")

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

        st.metric("Health Score", f"{score}/100", status)

    else:
        st.info("Enter your income to calculate health score")

    # ================= SMART SUGGESTIONS =================

    st.subheader("💡 Smart Suggestions")

    suggestions = []

    if income > 0:

        if total > budget:
            suggestions.append("⚠️ You exceeded your monthly budget")

        if savings < 0:
            suggestions.append("❗ Your spending is higher than your income")

        if "Food" in user_expenses["Category"].values:
            food_spend = user_expenses[
                user_expenses["Category"] == "Food"
            ]["Amount"].sum()

            if food_spend > income * 0.3:
                suggestions.append(
                    "🍔 High spending on food detected"
                )

        if "Shopping" in user_expenses["Category"].values:
            shop_spend = user_expenses[
                user_expenses["Category"] == "Shopping"
            ]["Amount"].sum()

            if shop_spend > income * 0.25:
                suggestions.append(
                    "🛍 Try reducing shopping expenses"
                )

    if suggestions:
        for s in suggestions:
            st.write(s)
    else:
        st.success("Your spending looks healthy 👍")

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

    col1,col2 = st.columns([9,1])

    with col2:
        if st.button("✏️"):
            st.session_state.edit_mode = not st.session_state.edit_mode

    df = expenses[expenses["User"] == st.session_state.user].copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Date"] = df["Date"].fillna(datetime.today())
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    if st.session_state.edit_mode:

        edited = st.data_editor(
            df[["Date","Category","Amount","Description"]],
            use_container_width=True
        )

        if st.button("💾 Save Changes"):

            expenses.loc[
                df.index,
                ["Date","Category","Amount","Description"]
            ] = edited

            expenses.to_csv("expenses.csv", index=False)

            st.session_state.edit_mode = False

            st.rerun()

    else:

        for i,row in df.reset_index().iterrows():

            cols = st.columns([2,2,1,3,1])

            cols[0].write(row["Date"])
            cols[1].write(row["Category"])
            cols[2].write(row["Amount"])
            cols[3].write(row["Description"])

            if cols[4].button("🗑️", key=f"del{i}"):

                expenses = expenses.drop(row["index"])
                expenses.to_csv("expenses.csv", index=False)

                st.rerun()

    # ================= CATEGORY CHART =================

    st.subheader("📊 Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty:

        fig1,ax1 = plt.subplots()

        ax1.pie(
            cat,
            labels=cat.index,
            autopct="%1.1f%%"
        )

        st.pyplot(fig1)

    # ================= DAILY SPENDING =================

    st.subheader("📈 Daily Spending")

    daily = user_expenses.groupby(
        user_expenses["Date"].dt.date
    )["Amount"].sum()

    if not daily.empty:

        fig2,ax2 = plt.subplots()

        daily.plot(kind="bar",ax=ax2)

        st.pyplot(fig2)

    # ================= MONTHLY TREND =================

    st.subheader("📉 Monthly Trend")

    monthly = user_expenses.groupby(
        user_expenses["Date"].dt.to_period("M")
    )["Amount"].sum()

    if not monthly.empty:

        fig4,ax4 = plt.subplots()

        monthly.plot(marker="o",ax=ax4)

        ax4.set_ylabel("Spending")

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

        fig3,ax3 = plt.subplots()

        ax3.plot(cum.index,y,label="Actual")

        ax3.plot(range(1,31),pred,"--",label="Prediction")

        ax3.legend()

        st.pyplot(fig3)
