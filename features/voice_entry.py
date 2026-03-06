import streamlit as st
import speech_recognition as sr
import pandas as pd
import tempfile
import re
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from features.utils import detect_spoken_date


def voice_entry(expenses):

    st.info("🎤 Voice Entry")

    ctx = webrtc_streamer(
        key="speech",
        mode=WebRtcMode.SENDONLY,
        audio_receiver_size=1024,
        media_stream_constraints={"audio": True, "video": False},
    )

    if ctx.audio_receiver:

        try:

            audio_frames = ctx.audio_receiver.get_frames(timeout=1)

            if audio_frames:

                recognizer = sr.Recognizer()

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:

                    for frame in audio_frames:
                        tmp.write(frame.to_ndarray().tobytes())

                    audio_path = tmp.name

                with sr.AudioFile(audio_path) as source:
                    audio = recognizer.record(source)

                text = recognizer.recognize_google(audio)

                st.success(f"You said: {text}")

                text_lower = text.lower()

                detected_date = detect_spoken_date(text)

                amount_match = re.search(r"\d+", text_lower)
                amount = int(amount_match.group()) if amount_match else 0

                if "food" in text_lower or "lunch" in text_lower:
                    category = "Food"
                elif "rent" in text_lower:
                    category = "Rent"
                elif "shopping" in text_lower:
                    category = "Shopping"
                elif "travel" in text_lower:
                    category = "Travel"
                elif "movie" in text_lower:
                    category = "Entertainment"
                elif "bus" in text_lower or "uber" in text_lower:
                    category = "Transport"
                else:
                    category = "Food"

                if amount == 0:
                    st.error("Amount not detected")
                    return

                new_row = pd.DataFrame({
                    "Date":[detected_date],
                    "Category":[category],
                    "Amount":[amount],
                    "Description":[text],
                    "User":[st.session_state.user]
                })

                expenses = pd.concat([expenses,new_row],ignore_index=True)

                expenses.to_csv("expenses.csv",index=False)

                st.success("Expense added successfully")

                st.rerun()

        except Exception as e:
            st.warning("Speak clearly after clicking start")
