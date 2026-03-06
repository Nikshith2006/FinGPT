import streamlit as st
import pandas as pd
import re
import tempfile
import speech_recognition as sr
from datetime import datetime
from features.utils import detect_spoken_date

# Safe import for sounddevice (Streamlit Cloud fix)
try:
    import sounddevice as sd
    from scipy.io.wavfile import write
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False


def voice_entry(expenses):

    st.subheader("🎤 Smart Voice Entry")

    # If audio hardware is not available (Streamlit Cloud)
    if not AUDIO_AVAILABLE:
        st.info("🎤 Voice recording is not supported on this server.")
        st.info("Run the app locally to use voice input.")
        return

    record_placeholder = st.empty()

    if st.button("🎙️ Start Recording"):

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
            except Exception:
                st.error("Could not understand audio.")
                return

            st.success(f"You said: {text}")

            # Detect date
            detected_date = detect_spoken_date(text)

            text_lower = text.lower()

            # Detect amount
            amount_match = re.search(r"\d+", text_lower)
            amount = int(amount_match.group()) if amount_match else 0

            # Detect category
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

            elif any(word in text_lower for word in ["bus","metro","ticket","uber","taxi"]):
                category = "Transport"

            else:
                category = "Food"

            if amount == 0:
                st.error("Could not detect amount.")
                return

            # Save expense
            new_row = pd.DataFrame({
                "Date":[detected_date],
                "Category":[category],
                "Amount":[amount],
                "Description":[text],
                "User":[st.session_state.user]
            })

            expenses = pd.concat([expenses,new_row],ignore_index=True)

            expenses.to_csv("expenses.csv",index=False)

            st.success("Expense Added Successfully!")

            st.rerun()

        except Exception as e:
            st.error("Voice feature failed")
            st.write(e)
