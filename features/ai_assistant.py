import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS
import time


def fallback_advice(income, budget, total, question):
    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial overview:")

    if total > budget:
        st.error("🚨 You are overspending!")
    elif total > 0.8 * budget:
        st.warning("⚠️ Close to budget limit")
    else:
        st.success("✅ Good financial control")

    st.write(f"💰 Savings: ₹{income - total}")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances", key="ai_input")

    # 🔥 STORE BUTTON STATE
    if "ask_clicked" not in st.session_state:
        st.session_state.ask_clicked = False

    if st.button("Ask AI"):
        st.session_state.ask_clicked = True

    # 🔥 RUN LOGIC AFTER CLICK
    if st.session_state.ask_clicked:

        if not question.strip():
            st.warning("Please enter a question")
            return

        context = f"""
Income: {income}
Budget: {budget}
Spending: {total}
"""

        prompt = context + question

        response_text = None

        # ⏱️ LIMIT WAIT TIME
        start = time.time()
        MAX_WAIT = 3

        for key in GOOGLE_API_KEYS:

            if time.time() - start > MAX_WAIT:
                break

            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-2.5-flash")

                response = model.generate_content(prompt)

                if response and hasattr(response, "text"):
                    response_text = response.text
                    break

            except:
                continue

        # ✅ ALWAYS SHOW RESULT
        if response_text:
            st.write(response_text)
        else:
            fallback_advice(income, budget, total, question)

        # 🔥 RESET BUTTON STATE (important)
        st.session_state.ask_clicked = False
