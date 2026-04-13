import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY
import time

# SAFE CONFIG
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key not configured")

# SAME MODEL
model = genai.GenerativeModel("gemini-2.5-flash")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    ask = st.button("Ask AI")

    # 🔥 INIT SESSION STATES
    if "last_ai_call" not in st.session_state:
        st.session_state.last_ai_call = 0

    if "last_question" not in st.session_state:
        st.session_state.last_question = ""

    if "last_response" not in st.session_state:
        st.session_state.last_response = ""

    # ✅ SHOW PREVIOUS RESPONSE (prevents re-call)
    if st.session_state.last_response:
        st.write(st.session_state.last_response)

    if ask and question and question.strip():

        # 🔥 PREVENT SAME QUESTION SPAM
        if question == st.session_state.last_question:
            st.warning("⚠️ You already asked this. Showing previous answer.")
            return

        current_time = time.time()

        # 🔥 STRONG COOLDOWN (60 sec)
        if current_time - st.session_state.last_ai_call < 60:
            remaining = int(60 - (current_time - st.session_state.last_ai_call))
            st.warning(f"⏳ Please wait {remaining}s before next request")
            return

        context = f"""
You are a personal finance assistant.

User Financial Data:
Monthly Income: {income}
Monthly Budget: {budget}
Current Spending: {total}

Give helpful financial advice based on this data.
"""

        try:
            with st.spinner("Thinking... 🤔"):

                response = model.generate_content(context + question)

                # ✅ SAVE STATE (VERY IMPORTANT)
                st.session_state.last_ai_call = time.time()
                st.session_state.last_question = question

                if response and hasattr(response, "text"):
                    st.session_state.last_response = response.text
                    st.write(response.text)
                else:
                    st.warning("No response generated")

        except Exception as e:

            if "429" in str(e):
                st.error("🚫 Rate limit hit. Wait 1 minute or reduce usage.")
            else:
                st.error("❌ AI Assistant failed")

            st.code(str(e))
