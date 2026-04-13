import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    savings = income - total

    # 🔥 suggestions
    if total > budget:
        suggestions = [
            "🚨 You are overspending. Cut down unnecessary expenses",
            "🛑 Avoid shopping and entertainment",
            "📊 Track every expense daily",
            "🍔 Reduce outside food",
            "💡 Focus on essential needs",
            "📉 Bring spending below budget"
        ]

    elif total > 0.8 * budget:
        suggestions = [
            "⚠️ You are close to your budget",
            "📊 Monitor daily spending",
            "🛍 Avoid impulse purchases",
            "🍽 Reduce eating out",
            "📅 Plan remaining expenses",
            "💡 Save small amounts"
        ]

    elif total > 0.5 * budget:
        suggestions = [
            "👍 Spending is moderate",
            "💰 Increase savings",
            "📊 Optimize expenses",
            "🛍 Avoid luxury purchases",
            "📈 Start investing",
            "💡 Plan future expenses"
        ]

    else:
        suggestions = [
            "🎉 Excellent financial management!",
            "💰 Saving well",
            "📈 Consider investing",
            "🛡 Build emergency fund",
            "📊 Track consistency",
            "🚀 Explore passive income"
        ]

    for s in suggestions:
        st.write("•", s)

    st.success(f"💰 Savings: ₹{savings}")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # 🔥 CLEAR FLAG (IMPORTANT FIX)
    if "clear_input" not in st.session_state:
        st.session_state.clear_input = False

    # 🔥 INPUT FIELD
    question = st.text_input(
        "Ask about your finances",
        value="" if st.session_state.clear_input else "",
        key="ai_input"
    )

    col1, col2 = st.columns([4,1])

    with col2:
        if st.button("❌ Clear"):
            st.session_state.clear_input = True
            st.rerun()

    # RESET FLAG AFTER RERUN
    if st.session_state.clear_input:
        st.session_state.clear_input = False

    # 🔥 ASK BUTTON
    if st.button("Ask AI"):

        if not question.strip():
            st.warning("Please enter a question")
            return

        # 🔥 SPINNER
        with st.spinner("Analyzing your finances... 🤔"):

            # ⚡ INSTANT FALLBACK
            fallback_advice(income, budget, total, question)

            # 🔥 TRY AI (OPTIONAL)
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
