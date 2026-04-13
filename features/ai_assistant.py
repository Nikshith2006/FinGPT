import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


# 🔥 MUST BE ABOVE (IMPORTANT)
def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    savings = income - total

    if total > budget:
        suggestions = [
            "🚨 You are overspending. Cut unnecessary expenses",
            "🛑 Avoid shopping temporarily",
            "📊 Track daily expenses",
            "🍔 Reduce outside food",
            "💡 Focus on essentials",
            "📉 Bring spending under control"
        ]

    elif total > 0.8 * budget:
        suggestions = [
            "⚠️ Close to budget limit",
            "📊 Monitor daily spending",
            "🛍 Avoid impulse buying",
            "🍽 Reduce eating out",
            "📅 Plan remaining expenses",
            "💡 Try to save small amount"
        ]

    elif total > 0.5 * budget:
        suggestions = [
            "👍 Spending is moderate",
            "💰 Increase savings",
            "📊 Optimize expenses",
            "🛍 Avoid luxury items",
            "📈 Start investing",
            "💡 Plan ahead"
        ]

    else:
        suggestions = [
            "🎉 Excellent financial management!",
            "💰 Saving well",
            "📈 Consider investing",
            "🛡 Build emergency fund",
            "📊 Maintain consistency",
            "🚀 Explore passive income"
        ]

    for s in suggestions:
        st.write("•", s)

    st.success(f"💰 Savings: ₹{savings}")


# 🔥 MAIN FUNCTION
def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # SESSION STATE
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    # INPUT
    question = st.text_input(
        "Ask about your finances",
        key="ai_input"
    )

    # BUTTONS (ALIGNED)
    col1, col2, col3 = st.columns([1,1,6])

    with col1:
        ask_clicked = st.button("Ask AI")

    with col2:
        clear_clicked = st.button("❌ Clear")

    # CLEAR BUTTON FIX
    if clear_clicked:
        st.session_state.ai_input = ""
        st.rerun()

    # ASK BUTTON
    if ask_clicked:

        if not question.strip():
            st.warning("Please enter a question")
            return

        # ✅ SPINNER ONLY FOR FALLBACK
        with st.spinner("Analyzing your finances... 🤔"):
            fallback_advice(income, budget, total, question)

        # 🔥 TRY AI WITHOUT SPINNER (NO HANG)
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
