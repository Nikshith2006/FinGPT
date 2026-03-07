import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder


def parse_voice_expense(text):

    text = text.lower()

    amount = 0
    category = "Other"
    description = text
    date = datetime.today()

    nums = re.findall(r"\d+", text)
    if nums:
        amount = int(nums[0])

    if "food" in text or "pizza" in text or "burger" in text:
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

    return date, category, amount, description


def voice_entry(expenses):

    st.markdown("### 🎤 Voice Entry")

    audio = mic_recorder(
        start_prompt="🎤 Voice Entry",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        use_container_width=True
    )

    if audio is None:
        return

    st.info("Processing voice...")

    recognizer = sr.Recognizer()

    try:
        audio_data = sr.AudioData(
            audio["bytes"],
            sample_rate=audio["sample_rate"],
            sample_width=2
        )

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

        st.success("Expense added successfully")

        st.rerun()

    except sr.UnknownValueError:
        st.error("Could not understand audio")

    except Exception as e:
        st.error(f"Voice processing error: {e}")
