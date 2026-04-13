import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY
import time

# SAFE CONFIG
try:
    genai.configure(api_key=GOOGLE_API_KEY)
except:
    st.error("API Key not configured")

# PRIMARY MODEL
model = genai.GenerativeModel("gemini-2.5-flash")

# ✅ FIXED BACKUP MODEL
backup_model = genai.GenerativeModel("gemini-1.5-pro")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    ask = st.button("Ask AI")

    if ask and question and question.strip():

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

                # TRY PRIMARY MODEL
                response = model.generate_content(context + question)

                if response and hasattr(response, "text"):
                    st.write(response.text)
                else:
                    st.warning("No response generated")

        except Exception as e:

            if "429" in str(e):

                st.warning("⚠️ Primary AI limit reached. Switching to backup model...")

                try:
                    response = backup_model.generate_content(context + question)

                    if response and hasattr(response, "text"):
                        st.write(response.text)
                    else:
                        st.warning("No response from backup model")

                except Exception as e2:
                    st.error("❌ Backup AI also failed")
                    st.code(str(e2))

            else:
                st.error("❌ AI Assistant failed")
                st.code(str(e))
