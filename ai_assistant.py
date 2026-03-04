import streamlit as st
from google import genai

client = genai.Client(api_key=st.secrets["GOOGLE_API_KEY"])

def ai_assistant(income,budget,total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if question:

        context=f"""
        Income:{income}
        Budget:{budget}
        Spent:{total}
        """

        reply = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=context+question
        )

        st.write(reply.text)