import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS
import time


def fallback_advice(income, budget, total, question):
    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    if total > budget:
        st.error("🚨 You are overspending!")
        st.write("• Reduce unnecessary expenses")
    elif total > 0.8 * budget:
        st.warning("⚠️ Near budget limit")
    else:
        st.success("✅ Good financial control")

    st.write(f"💰 Savings: ₹{income - total}")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    ask = st.button("Ask AI")

    if ask:

        if not question.strip():
            st.warning("Please enter a question")
            return

        context = f"""
Income: {income}
Budget: {budget}
Spending: {total}
"""

        prompt = context + question

        # ⏱️ MAX WAIT TIME (VERY IMPORTANT)
        MAX_WAIT = 3  # seconds

        start_time = time.time()
        response_text = None

        # 🔥 TRY KEYS BUT DON'T WAIT LONG
        for key in GOOGLE_API_KEYS:

            if time.time() - start_time > MAX_WAIT:
                break  # stop waiting

            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel("gemini-2.5-flash")

                response = model.generate_content(prompt)

                if response and hasattr(response, "text"):
                    response_text = response.text
                    break

            except:
                continue

        # ✅ FAST RESPONSE SYSTEM
        if response_text:
            st.write(response_text)
        else:
            fallback_advice(income, budget, total, question)
