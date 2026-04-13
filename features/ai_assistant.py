import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY


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

    if question and question.strip():

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

                if response and hasattr(response, "text"):
                    st.write(response.text)
                else:
                    st.warning("No response generated")

        except Exception as e:

            st.error("❌ AI Assistant failed")
            st.code(str(e))   # shows real error
