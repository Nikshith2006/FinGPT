import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    savings = income - total

    suggestions = []

    if total > budget:
        suggestions = [
            "🚨 You are overspending. Cut down unnecessary expenses",
            "🛑 Avoid shopping and entertainment for a few days",
            "📊 Track every expense daily",
            "🍔 Reduce food delivery / outside food",
            "💡 Focus only on essential needs",
            "📉 Try to bring spending below budget immediately"
        ]

    elif total > 0.8 * budget:
        suggestions = [
            "⚠️ You are close to your budget limit",
            "📊 Monitor daily spending carefully",
            "🛍 Avoid impulse purchases",
            "🍽 Reduce eating out",
            "📅 Plan remaining month expenses",
            "💡 Try to save at least small amount"
        ]

    elif total > 0.5 * budget:
        suggestions = [
            "👍 Your spending is moderate",
            "💰 Try increasing your savings",
            "📊 Optimize unnecessary expenses",
            "🛍 Avoid luxury purchases",
            "📈 Start small investments",
            "💡 Plan ahead for upcoming expenses"
        ]

    else:
        suggestions = [
            "🎉 Excellent financial management!",
            "💰 You are saving well",
            "📈 Consider investing your savings",
            "🛡 Build an emergency fund",
            "📊 Track spending for consistency",
            "🚀 Explore passive income ideas"
        ]

    for s in suggestions:
        st.write("•", s)

    st.success(f"💰 Savings: ₹{savings}")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    if st.button("Ask AI") or (question and st.session_state.get("enter_pressed", False)):

        if not question.strip():
            st.warning("Please enter a question")
            return

        with st.spinner("Analyzing your finances... 🤔"):

            # 🔥 TRY AI FIRST
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

                else:
                    # fallback if empty response
                    fallback_advice(income, budget, total, question)

            except:
                # 🔥 AUTO FALLBACK
                fallback_advice(income, budget, total, question)
