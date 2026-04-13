import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS
import time

# CREATE MODELS FOR EACH API KEY
models = []

for key in GOOGLE_API_KEYS:
    try:
        genai.configure(api_key=key)
        models.append(genai.GenerativeModel("gemini-2.5-flash"))
    except:
        pass


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

        with st.spinner("Thinking... 🤔"):

            response_text = None
            error_message = None

            # 🔥 TRY ALL API KEYS ONE BY ONE
            for i, model in enumerate(models):

                try:
                    response = model.generate_content(context + question)

                    if response and hasattr(response, "text"):
                        response_text = response.text
                        break

                except Exception as e:
                    error_message = str(e)

                    # Only skip if quota error
                    if "429" in error_message:
                        continue
                    else:
                        st.error("❌ AI Assistant failed")
                        st.code(error_message)
                        return

            # ✅ SUCCESS
            if response_text:
                st.success(f"✅ Response from API Key {i+1}")
                st.write(response_text)

            else:
                st.error("🚫 All API keys exhausted for today")
                st.code(error_message)
