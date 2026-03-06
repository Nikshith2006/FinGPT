import streamlit as st
from google import genai


def ai_assistant(user_expenses, income):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if question:

        total_spent = 0

        if not user_expenses.empty:
            total_spent = user_expenses["Amount"].sum()

        context = f"""
        Monthly Income: {income}
        Total Spending: {total_spent}
        """

        try:
            client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=context + question
            )

            st.write(response.text)

        except Exception as e:

            st.error("AI assistant error")
            st.write(e)
