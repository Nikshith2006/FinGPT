import streamlit as st
from config import client


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
            # FIXED GEMINI CALL
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=context + question
            )

            st.write(response.text)

        except Exception as e:

            st.error("AI Assistant failed")
            st.write(e)
