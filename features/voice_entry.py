import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import time


# ---------------- PARSE VOICE ----------------

def parse_voice_expense(text):

    if not isinstance(text, str):
        return datetime.today(), "Other", 0, ""

    text = text.lower()

    amount = 0
    category = "Other"
    description = text
    date = datetime.today()

    # amount detection
    amt = re.findall(r'\d+', text)
    if amt:
        amount = int(amt[0])

    # category detection
    if "food" in text or "burger" in text or "pizza" in text:
        category = "Food"

    elif "rent" in text:
        category = "Rent"

    elif "bus" in text or "ticket" in text or "travel" in text:
        category = "Transport"

    elif "dress" in text or "shopping" in text:
        category = "Shopping"

    elif "movie" in text or "entertainment" in text:
        category = "Entertainment"

    # date detection
    today = datetime.today()

    if "day before yesterday" in text:
        date = today - timedelta(days=2)

    elif "yesterday" in text:
        date = today - timedelta(days=1)

    else:
        date = today

    return date, category, amount, description


# ---------------- VOICE ENTRY ----------------

def voice_entry(expenses):

    st.markdown("## 🎤 Smart Voice Entry")

    if "voice_recording" not in st.session_state:
        st.session_state.voice_recording = False

    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""

    # ---------------- BUTTON ----------------

    if st.button("🎤 Start Recording"):
        st.session_state.voice_recording = True
        st.session_state.voice_text = ""

    # ---------------- RECORDING ----------------

    if st.session_state.voice_recording:

        st.markdown(
            "<h2 style='color:red;'>🎤 Recording...</h2>",
            unsafe_allow_html=True
        )

        voice_html = """
        <script>

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.lang = "en-IN";
        recognition.interimResults = false;
        recognition.continuous = false;

        recognition.start();

        setTimeout(()=>{
            recognition.stop();
        },5000);

        recognition.onresult = function(event){

            const text = event.results[0][0].transcript;

            const streamlitMessage = {
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: text
            };

            window.parent.postMessage(streamlitMessage,"*");

        };

        </script>
        """

        result = st.components.v1.html(voice_html, height=0)

        time.sleep(5)

        st.success("✅ Recording Finished")

        st.session_state.voice_recording = False

        if isinstance(result, str):
            st.session_state.voice_text = result

    # ---------------- RESULT ----------------

    voice_text = st.session_state.get("voice_text", "")

    if isinstance(voice_text, str) and voice_text != "":

        st.success(f"You said: {voice_text}")

        date, category, amount, description = parse_voice_expense(voice_text)

        new_row = pd.DataFrame({
            "Date":[date],
            "Category":[category],
            "Amount":[amount],
            "Description":[description],
            "User":[st.session_state.user]
        })

        expenses = pd.concat([expenses,new_row],ignore_index=True)

        expenses.to_csv("expenses.csv",index=False)

        st.success("✅ Expense added to table")

        st.session_state.voice_text = ""

        st.rerun()
