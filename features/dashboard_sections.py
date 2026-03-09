import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
#import tempfile
import re
#import sounddevice as sd
#from scipy.io.wavfile import write
#import speech_recognition as sr
from sklearn.linear_model import LinearRegression
from utils import detect_spoken_date
from datetime import datetime, timedelta
import calendar


# ---------------- VOICE ENTRY ----------------
def voice_entry(expenses):

    st.subheader("")

    record_placeholder = st.empty()

    if st.button("🎙️ Voice Command"):

        try:

            fs = 16000
            duration = 5

            record_placeholder.markdown(
            """
            <div style="text-align:center;font-size:40px;color:red;">
            🎤 Recording...
            </div>
            """,
            unsafe_allow_html=True
            )

            recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
            sd.wait()

            record_placeholder.markdown(
            """
            <div style="text-align:center;font-size:30px;color:green;">
            ✅ Recording Finished
            </div>
            """,
            unsafe_allow_html=True
            )

            recording_int16 = (recording * 32767).astype("int16")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                write(tmp.name, fs, recording_int16)
                audio_path = tmp.name

            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)

            try:
                text = recognizer.recognize_google(audio)
            except:
                st.error("❌ Could not understand audio.")
                return expenses

            st.success(f"🗣 You said: {text}")

            text_lower = text.lower()

            full_expenses = pd.read_csv("data/expenses.csv")
            full_expenses["Date"] = pd.to_datetime(full_expenses["Date"], errors="coerce")

            today = pd.Timestamp.today()

            # ---------------- SPENDING THIS MONTH ----------------

            if "show my spending this month" in text_lower or "how much did i spend this month" in text_lower:

                this_month_expenses = full_expenses[
                    (full_expenses["User"] == st.session_state.user) &
                    (full_expenses["Date"].dt.month == today.month) &
                    (full_expenses["Date"].dt.year == today.year)
                ]

                total_spent = this_month_expenses["Amount"].sum()

                st.info(f"💰 You spent ₹{total_spent} this month.")

                return expenses


            categories = [
                "food","shopping","travel",
                "rent","transport","entertainment"
            ]

            for cat in categories:

                if f"show my {cat} expenses" in text_lower:

                    cat_expenses = full_expenses[
                        (full_expenses["User"] == st.session_state.user) &
                        (full_expenses["Category"].str.lower() == cat)
                    ]

                    total = cat_expenses["Amount"].sum()

                    st.info(f"📊 Your total {cat} expenses are ₹{total}")

                    return expenses


            if "show my savings" in text_lower:

                users = pd.read_csv("data/users.csv")
                user_data = users[users["Name"] == st.session_state.user].iloc[0]

                income = user_data["MonthlyIncome"]

                this_month_expenses = full_expenses[
                    (full_expenses["User"] == st.session_state.user) &
                    (full_expenses["Date"].dt.month == today.month) &
                    (full_expenses["Date"].dt.year == today.year)
                ]

                spent = this_month_expenses["Amount"].sum()

                savings = income - spent

                st.success(f"🏦 Your savings this month are ₹{savings}")

                return expenses


            if "show my financial health" in text_lower or "what is my health score" in text_lower:

                users = pd.read_csv("data/users.csv")
                user_data = users[users["Name"] == st.session_state.user].iloc[0]

                income = user_data["MonthlyIncome"]
                budget = user_data["MonthlyBudget"]

                this_month_expenses = full_expenses[
                    (full_expenses["User"] == st.session_state.user) &
                    (full_expenses["Date"].dt.month == today.month) &
                    (full_expenses["Date"].dt.year == today.year)
                ]

                spent = this_month_expenses["Amount"].sum()

                health_score = max(0, 100 - (spent / budget * 100)) if budget > 0 else 0

                if health_score >= 85:
                    label = "Excellent"
                elif health_score >= 70:
                    label = "Good"
                elif health_score >= 50:
                    label = "Moderate"
                elif health_score >= 30:
                    label = "Poor"
                else:
                    label = "Critical"

                st.success(f"💚 Your Financial Health Score is {health_score:.0f}% ({label})")

                return expenses


            amount_match = re.search(r"\d+", text_lower)
            amount = int(amount_match.group()) if amount_match else 0

            if amount == 0:
                st.error("⚠ Could not detect amount.")
                return expenses


            today_dt = datetime.today()

            days = {
                "monday":0,
                "tuesday":1,
                "wednesday":2,
                "thursday":3,
                "friday":4,
                "saturday":5,
                "sunday":6
            }

            detected_date = None

            if "today" in text_lower:
                detected_date = today_dt

            elif "yesterday" in text_lower:
                detected_date = today_dt - timedelta(days=1)

            elif "day before yesterday" in text_lower:
                detected_date = today_dt - timedelta(days=2)

            if detected_date is None:
                detected_date = detect_spoken_date(text_lower)

            detected_date = pd.to_datetime(detected_date)


            if "rent" in text_lower or "hostel" in text_lower:
                category = "Rent"

            elif "shopping" in text_lower or "buy" in text_lower or "amazon" in text_lower:
                category = "Shopping"

            elif "travel" in text_lower or "trip" in text_lower or "flight" in text_lower:
                category = "Travel"

            elif "movie" in text_lower or "netflix" in text_lower:
                category = "Entertainment"

            elif "bus" in text_lower or "metro" in text_lower or "petrol" in text_lower or "uber" in text_lower:
                category = "Transport"

            elif "food" in text_lower or "restaurant" in text_lower or "snacks" in text_lower or "biryani" in text_lower:
                category = "Food"

            else:
                category = "Other"


            clean_description = text_lower
            clean_description = " ".join(clean_description.split()).title()

            new_row = pd.DataFrame({
                "Date":[detected_date],
                "Category":[category],
                "Amount":[amount],
                "Description":[clean_description],
                "User":[st.session_state.user]
            })

            full_expenses = pd.concat([full_expenses, new_row], ignore_index=True)

            full_expenses.to_csv("data/expenses.csv", index=False)

            st.success("✅ Expense Added Successfully!")

            st.rerun()

        except Exception as e:

            st.error("Voice feature failed")
            st.write(e)

    return expenses


# ---------------- EXPENSE TABLE ----------------

def expense_table(expenses, user_expenses):

    st.subheader("📊 Expense Manager")

    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

    df = user_expenses.copy()

    df = df.sort_values(by="Date", ascending=True)

    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    header = st.columns([1,2,2,1,3])

    header[0].markdown("**S.No**")
    header[1].markdown("**Date**")
    header[2].markdown("**Category**")
    header[3].markdown("**Amount**")
    header[4].markdown("**Description**")

    for i,row in df.reset_index().iterrows():

        cols = st.columns([1,2,2,1,3])

        cols[0].write(i+1)
        cols[1].write(row["Date"])
        cols[2].write(row["Category"])
        cols[3].write(f"₹{row['Amount']}")
        cols[4].write(row["Description"])


# ---------------- CHARTS ----------------

def charts_and_predictions(expenses, user_expenses):

    expenses["Date"] = pd.to_datetime(expenses["Date"], errors="coerce")
    user_expenses["Date"] = pd.to_datetime(user_expenses["Date"], errors="coerce")

    st.subheader("📊 Category Distribution")

    cat = user_expenses.groupby("Category")["Amount"].sum()

    if not cat.empty:

        fig1, ax1 = plt.subplots()

        ax1.pie(cat, labels=cat.index, autopct="%1.1f%%")

        st.pyplot(fig1)

    else:
        st.info("No expenses for this month.")

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

    st.subheader("📉 Monthly Trend")

    if not user_expenses.empty:

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

    else:
        st.info("No monthly data for this year.")

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
