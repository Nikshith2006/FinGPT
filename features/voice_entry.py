import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder
import tempfile


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
    elif "bus" in text or "travel" in text or "ticket" in text:
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

    st.subheader("🎤 Voice Entry")

    audio = mic_recorder(
        start_prompt="🎤 Start Recording",
        stop_prompt="⏹ Stop",
        just_once=True,
        use_container_width=True
    )

    if audio is None:
        return

    st.info("Processing voice...")

    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio["bytes"])
        temp_path = f.name

    with sr.AudioFile(temp_path) as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(audio_data)

        st.success(f"You said: {text}")

        date, category, amount, description = parse_voice_expense(text)

        new_row = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Amount": [amount],
            "Description": [description],
            "User": [st.session_state.user]
        })

        expenses = pd.concat([expenses, new_row], ignore_index=True)
        expenses.to_csv("expenses.csv", index=False)

        st.success("Expense added successfully")
        st.rerun()

    except sr.UnknownValueError:
        st.error("Could not understand the audio")

    except Exception as e:
        st.error(f"Voice error: {e}")
