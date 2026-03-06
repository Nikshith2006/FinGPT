import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
import time


# ================= PARSE VOICE TEXT =================

def parse_voice_expense(text):

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

    # -------- Date detection --------
    today = datetime.today()

    if "day before yesterday" in text:
        date = today - timedelta(days=2)

    elif "yesterday" in text:
        date = today - timedelta(days=1)

    else:
        date = today

    return date, category, amount, description


# ================= VOICE ENTRY =================

def voice_entry(expenses):

    st.markdown("### 🎤 Smart Voice Entry")

    if "recording" not in st.session_state:
        st.session_state.recording = False

    if "voice_result" not in st.session_state:
        st.session_state.voice_result = ""

    # ---------- BUTTON ----------

    if st.button("🎙 Start Recording"):
        st.session_state.recording = True
        st.session_state.voice_result = ""

    # ---------- RECORDING UI ----------

    if st.session_state.recording:

        st.markdown("## 🎤 Recording...")

        # Speech recognition JS
        voice_html = """
        <script>
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = "en-IN";
        recognition.interimResults = false;
        recognition.continuous = false;

        recognition.start();

        setTimeout(() => {
            recognition.stop();
        }, 5000);

        recognition.onresult = function(event){
            const text = event.results[0][0].transcript;

            const data = {
                isStreamlitMessage: true,
                type: "streamlit:setComponentValue",
                value: text
            };

            window.parent.postMessage(data, "*");
        }
        </script>
        """

        result = st.components.v1.html(voice_html, height=0)

        if isinstance(result, str):
            st.session_state.voice_result = result

        # animation delay
        time.sleep(5)

        st.success("✅ Recording Finished")

        st.session_state.recording = False

    # ---------- RESULT ----------

    voice_text = st.session_state.get("voice_result", "")

    if isinstance(voice_text, str) and voice_text != "":

        st.success(f"You said: {voice_text}")

        # Parse voice
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

        st.success("✅ Expense added successfully")

        st.session_state.voice_result = ""

        st.rerun()
