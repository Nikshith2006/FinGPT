import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder


# -------- PARSE VOICE TEXT --------
def parse_voice_expense(text):

    text = text.lower()

    amount = 0
    category = "Other"
    description = text
    date = datetime.today()

    amt = re.findall(r'\d+', text)
    if amt:
        amount = int(amt[0])

    if "food" in text or "burger" in text or "pizza" in text:
        category = "Food"

    elif "rent" in text:
        category = "Rent"

    elif "bus" in text or "ticket" in text or "travel" in text:
        category = "Transport"

    elif "shopping" in text or "dress" in text:
        category = "Shopping"

    elif "movie" in text or "entertainment" in text:
        category = "Entertainment"

    today = datetime.today()

    if "day before yesterday" in text:
        date = today - timedelta(days=2)

    elif "yesterday" in text:
        date = today - timedelta(days=1)

    else:
        date = today

    return date, category, amount, description


# -------- VOICE ENTRY --------
def voice_entry(expenses):

    st.markdown("### 🎤 Smart Voice Entry")

    audio = mic_recorder(
        start_prompt="🎤 Voice Entry",
        stop_prompt="⏹ Stop",
        just_once=True,
        use_container_width=True
    )

    if audio:

        recognizer = sr.Recognizer()

        with sr.AudioFile(audio["filename"]) as source:
            audio_data = recognizer.record(source)

        try:
            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            date, category, amount, description = parse_voice_expense(text)

            new_row = pd.DataFrame({
                "Date":[date],
                "Category":[category],
                "Amount":[amount],
                "Description":[description],
                "User":[st.session_state.user]
            })

            expenses = pd.concat([expenses,new_row],ignore_index=True)

            expenses.to_csv("expenses.csv",index=False)

            st.success("✅ Expense added successfully")

            st.rerun()

        except:
            st.error("Voice not recognized. Try again.")
