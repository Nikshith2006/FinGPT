import streamlit as st
import tempfile
import speech_recognition as sr
from streamlit_mic_recorder import mic_recorder


def voice_entry():

    st.subheader("🎤 Voice Entry")

    audio = mic_recorder(
        start_prompt="🎙 Start Recording",
        stop_prompt="⏹ Stop Recording",
        just_once=True,
        use_container_width=True
    )

    if audio is not None:

        try:

            st.success("✅ Recording Finished")

            # Save audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                f.write(audio["bytes"])
                audio_path = f.name

            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            text = recognizer.recognize_google(audio_data)

            st.success(f"You said: {text}")

            return text

        except sr.UnknownValueError:
            st.error("Could not understand audio")

        except sr.RequestError:
            st.error("Speech recognition service unavailable")

        except Exception as e:
            st.error("Voice feature failed")
            st.write(e)

    return None
