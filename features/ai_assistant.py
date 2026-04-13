import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY
import time   # ✅ NEW

# SAFE CONFIG
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key not configured")

# SAME MODEL (as you requested)
model = genai.GenerativeModel("gemini-2.5-flash")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    # ✅ NEW: Button to prevent auto multiple calls
    ask = st.button("Ask AI")

    # ✅ NEW: Track last request time
    if "last_ai_call" not in st.session_state:
        st.session_state.last_ai_call = 0

    if ask and question and question.strip():

        current_time = time.time()

        # ✅ NEW: Cooldown (40 seconds)
        if current_time - st.session_state.last_ai_call < 40:
            remaining = int(40 - (current_time - st.session_state.last_ai_call))
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

                # ✅ SAVE TIME AFTER SUCCESS
                st.session_state.last_ai_call = time.time()

                if response and hasattr(response, "text"):
                    st.write(response.text)
                else:
                    st.warning("No response generated")

        except Exception as e:

            # ✅ HANDLE QUOTA ERROR CLEANLY
            if "429" in str(e):
                st.error("🚫 Rate limit reached. Please wait ~40 seconds.")
            else:
                st.error("❌ AI Assistant failed")

            st.code(str(e))   # shows real error
