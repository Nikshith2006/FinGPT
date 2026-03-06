import streamlit as st
import speech_recognition as sr
import tempfile
import pandas as pd
import numpy as np
import re
import time
import wave
from streamlit_mic_recorder import mic_recorder


def voice_entry(expenses, user, detect_spoken_date):

    # Click once to start recording
    if st.button("🎤 Voice Entry"):

        # Animation
        status = st.empty()
        status.markdown(
            "<h3 style='color:red;text-align:center;'>🔴 Recording... (5 seconds)</h3>",
            unsafe_allow_html=True
        )

        # record audio
        audio = mic_recorder(just_once=True, key="voice_auto")

        time.sleep(5)

        status.markdown(
            "<h3 style='color:green;text-align:center;'>✅ Recording Finished</h3>",
            unsafe_allow_html=True
        )

        if not audio:
            st.error("No audio detected")
            return

        try:

            # Convert bytes to WAV properly
            audio_bytes = audio["bytes"]

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                with wave.open(tmp.name, "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(44100)
                    wf.writeframes(audio_bytes)

                audio_path = tmp.name

            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            # Extract amount
            amount_match = re.search(r"\d+", text)
            amount = int(amount_match.group()) if amount_match else 0

            text_lower = text.lower()

            # Detect category
            if any(w in text_lower for w in ["food", "lunch", "dinner", "breakfast"]):
                category = "Food"
            elif "rent" in text_lower:
                category = "Rent"
            elif any(w in text_lower for w in ["shopping", "buy", "clothes"]):
                category = "Shopping"
            elif any(w in text_lower for w in ["travel", "trip"]):
                category = "Travel"
            elif any(w in text_lower for w in ["movie", "entertainment"]):
                category = "Entertainment"
            elif any(w in text_lower for w in ["bus", "metro", "ticket"]):
                category = "Transport"
            else:
                category = "Food"

            if amount == 0:
                st.error("Could not detect amount")
                return

            date = detect_spoken_date(text)

            new_row = pd.DataFrame({
                "Date": [date],
                "Category": [category],
                "Amount": [amount],
                "Description": [text],
                "User": [user]
            })

            expenses = pd.concat([expenses, new_row], ignore_index=True)
            expenses.to_csv("expenses.csv", index=False)

            st.success("Expense added successfully!")
            st.rerun()

        except Exception as e:
            st.error("Voice recognition failed")
            st.write(e)


