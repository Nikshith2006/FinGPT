import streamlit as st
import tempfile
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder

def voice_entry():

    st.subheader("🎤 Voice Entry")

    audio = mic_recorder()

    if audio:

        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(audio["bytes"])
            path=f.name

        recognizer = sr.Recognizer()

        with sr.AudioFile(path) as source:
            data = recognizer.record(source)

        text = recognizer.recognize_google(data)

        st.success(f"You said: {text}")