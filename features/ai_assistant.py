import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    if total > budget:
        st.error("🚨 You are overspending!")
        st.write("• Reduce unnecessary expenses")
    elif total > 0.8 * budget:
        st.warning("⚠️ You are near your budget limit")
    else:
        st.success("✅ Your spending is under control")

    st.write(f"💰 Savings: ₹{income - total}")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if st.button("Ask AI"):

        if not question.strip():
            st.warning("Please enter a question")
            return

        # ⚡ IMMEDIATE FALLBACK FIRST (VERY IMPORTANT)
        fallback_advice(income, budget, total, question)

        # 🔥 TRY AI IN BACKGROUND (NO BLOCKING UI)
        try:
            genai.configure(api_key=GOOGLE_API_KEYS[0])
            model = genai.GenerativeModel("gemini-2.5-flash")

            context = f"""
Income: {income}
Budget: {budget}
Spending: {total}
"""

            response = model.generate_content(context + question)

            if response and hasattr(response, "text") and response.text:
                st.subheader("🤖 AI Insight")
                st.write(response.text)

        except:
            pass
