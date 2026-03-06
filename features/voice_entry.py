import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re


def parse_voice_expense(text):

    # safety: ensure text is string
    if not isinstance(text, str):
        return datetime.today(), "Other", 0, ""

    text = text.lower()

    amount = 0
    category = "Other"
    description = text
    date = datetime.today()

    # -------- Amount extraction --------
    amt = re.findall(r'\d+', text)

    if amt:
        amount = int(amt[0])

    # -------- Category detection --------
    if "food" in text or "burger" in text or "pizza" in text:
        category = "Food"

    elif "rent" in text:
        category = "Rent"

    elif "travel" in text or "bus" in text or "ticket" in text:
        category = "Transport"

    elif "shopping" in text or "dress" in text:
        category = "Shopping"

    elif "movie" in text or "entertainment" in text:
        category = "Entertainment"

    # -------- Date logic --------
    today = datetime.today()

    if "day before yesterday" in text:
        date = today - timedelta(days=2)

    elif "yesterday" in text:
        date = today - timedelta(days=1)

    else:
        date = today

    return date, category, amount, description


def voice_entry(expenses):

    st.markdown("### 🎤 Voice Entry")

    if "voice_active" not in st.session_state:
        st.session_state.voice_active = False

    if "voice_text" not in st.session_state:
        st.session_state.voice_text = ""

    # ---------- BUTTON ----------

    if st.button("🎤 Voice Entry"):
        st.session_state.voice_active = True

    # ---------- RECORDING UI ----------

    if st.session_state.voice_active:

        st.info("🎙 Recording... Speak now (5 seconds)")

        voice_html = """
        <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'en-IN';
        recognition.continuous = false;
        recognition.interimResults = false;

        recognition.start();

        setTimeout(() => {
            recognition.stop();
        }, 5000);

        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;

            const streamlitMessage = {
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: text
            };

            window.parent.postMessage(streamlitMessage, "*");
        };
        </script>
        """

        voice_text = st.components.v1.html(voice_html, height=0)

        if isinstance(voice_text, str):
            st.session_state.voice_text = voice_text

    # ---------- RECEIVE VOICE ----------

    voice_text = st.session_state.get("voice_text", "")

    if not isinstance(voice_text, str):
        voice_text = ""

    if voice_text:

        st.success(f"🗣 Recognized: {voice_text}")

        date, category, amount, description = parse_voice_expense(voice_text)

        new_row = pd.DataFrame({
            "Date": [date],
            "Category": [category],
            "Amount": [amount],
            "Description": [description],
            "User": [st.session_state.user]
        })

        expenses = pd.concat([expenses, new_row], ignore_index=True)

        expenses.to_csv("expenses.csv", index=False)

        st.session_state.voice_text = ""
        st.session_state.voice_active = False

        st.success("✅ Expense added from voice")

        st.rerun()
