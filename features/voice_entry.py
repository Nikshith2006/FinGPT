import streamlit as st
import speech_recognition as sr
import tempfile
import pandas as pd
import re
import time
from streamlit_mic_recorder import mic_recorder


def voice_entry(expenses, user, detect_spoken_date):


    # ---- SINGLE BUTTON ----
    if st.button("🎤 Voice Entry"):

        status = st.empty()

        status.markdown(
        "<h2 style='color:red;text-align:center;'>🔴 Recording...</h2>",
        unsafe_allow_html=True
        )

        # ---- Record Audio ----
        audio = mic_recorder(
            start_prompt="",
            stop_prompt="",
            just_once=True,
            key="voice_hidden"
        )

        time.sleep(5)

        status.markdown(
        "<h2 style='color:green;text-align:center;'>✅ Recording Finished</h2>",
        unsafe_allow_html=True
        )

        if not audio:
            st.error("No voice detected")
            return

        try:

            # ---- Save Audio ----
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp.write(audio["bytes"])
                audio_path = tmp.name

            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            # ---- Extract Amount ----
            amount_match = re.search(r"\d+", text)
            amount = int(amount_match.group()) if amount_match else 0

            text_lower = text.lower()

            # ---- Category Detection ----
            if any(word in text_lower for word in ["food","dinner","lunch","breakfast"]):
                category = "Food"
            elif "rent" in text_lower:
                category = "Rent"
            elif any(word in text_lower for word in ["shopping","buy","clothes"]):
                category = "Shopping"
            elif any(word in text_lower for word in ["travel","trip"]):
                category = "Travel"
            elif any(word in text_lower for word in ["movie","entertainment"]):
                category = "Entertainment"
            elif any(word in text_lower for word in ["bus","metro","ticket"]):
                category = "Transport"
            else:
                category = "Food"

            if amount == 0:
                st.error("Could not detect amount")
                return

            date = detect_spoken_date(text)

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
