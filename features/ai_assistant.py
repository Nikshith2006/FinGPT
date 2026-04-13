import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    savings = income - total

    suggestions = []

    # 🔥 Generate multiple suggestions
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

    # ✅ Show all suggestions
    for s in suggestions:
        st.write("•", s)

    st.success(f"💰 Savings: ₹{savings}")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # 🔥 SESSION STATE FOR INPUT
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    col1, col2 = st.columns([4,1])

    with col1:
        question = st.text_input(
            "Ask about your finances",
            key="ai_input"
        )

    # 🔥 CLEAR BUTTON
    with col2:
        if st.button("❌ Clear"):
            st.session_state.ai_input = ""
            st.rerun()

    # 🔥 ASK BUTTON
    if st.button("Ask AI"):

        if not question.strip():
            st.warning("Please enter a question")
            return

        # 🔥 SPINNER (LOADING EFFECT)
        with st.spinner("Analyzing your finances... 🤔"):

            # ⚡ Show fallback instantly
            fallback_advice(income, budget, total, question)

            # 🔥 Try AI silently
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
