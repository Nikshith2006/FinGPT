import streamlit as st
import speech_recognition as sr
import tempfile
import time
from streamlit_mic_recorder import mic_recorder


def voice_entry(expenses, user, detect_spoken_date):

    st.subheader("🎤 Voice Entry")

    audio = mic_recorder(
        start_prompt="🎙 Start Recording",
        stop_prompt="⏹ Stop",
        just_once=True,
        key="voice"
    )

    if audio:

        # -------- Recording Animation --------
        record_placeholder = st.empty()

        record_placeholder.markdown(
        """
        <div style="text-align:center;font-size:30px;color:red;">
        🔴 Recording... (5 seconds)
        </div>
        """,
        unsafe_allow_html=True
        )

        time.sleep(5)

        record_placeholder.markdown(
        """
        <div style="text-align:center;font-size:30px;color:green;">
        ✅ Recording Finished
        </div>
        """,
        unsafe_allow_html=True
        )

        try:

            # -------- Save Audio --------
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio["bytes"])
                audio_path = tmp.name

            recognizer = sr.Recognizer()

            # -------- Speech Recognition --------
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            # -------- Extract Amount --------
            import re
            amount_match = re.search(r"\d+", text)
            amount = int(amount_match.group()) if amount_match else 0

            # -------- Detect Category --------
            text_lower = text.lower()

            if "food" in text_lower or "dinner" in text_lower or "lunch" in text_lower:
                category = "Food"
            elif "rent" in text_lower:
                category = "Rent"
            elif "shopping" in text_lower or "buy" in text_lower:
                category = "Shopping"
            elif "travel" in text_lower or "trip" in text_lower:
                category = "Travel"
            elif "movie" in text_lower:
                category = "Entertainment"
            elif "bus" in text_lower or "metro" in text_lower:
                category = "Transport"
            else:
                category = "Food"

            if amount == 0:
                st.error("Could not detect amount")
                return

            date = detect_spoken_date(text)

            import pandas as pd

            new_row = pd.DataFrame({
                "Date":[date],
                "Category":[category],
                "Amount":[amount],
                "Description":[text],
                "User":[user]
            })

            expenses = pd.concat([expenses,new_row],ignore_index=True)
            expenses.to_csv("expenses.csv",index=False)

            st.success("Expense added successfully!")

            st.rerun()

        except Exception as e:

            st.error("Voice recognition failed")
            st.write(e)
