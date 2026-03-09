import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEY


genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if question:

        context = f"""
You are a personal finance assistant.

User Financial Data:
Monthly Income: {income}
Monthly Budget: {budget}
Current Spending: {total}

Give helpful financial advice based on this data.
"""

        try:

            response = model.generate_content(context + question)

            st.write(response.text)

        except Exception as e:

            st.error("AI Assistant failed")
            st.write(e)
