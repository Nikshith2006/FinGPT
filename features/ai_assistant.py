import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


# ---------------- FALLBACK ----------------
def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    savings = income - total

    if total > budget:
        suggestions = [
            "🚨 You are overspending. Cut unnecessary expenses",
            "🛑 Avoid shopping temporarily",
            "📊 Track daily expenses strictly",
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


# ---------------- MAIN ----------------
def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # SESSION STATE
    if "ai_output" not in st.session_state:
        st.session_state.ai_output = None

    if "input_key" not in st.session_state:
        st.session_state.input_key = "input_1"

    # INPUT
    question = st.text_input(
        "Ask about your finances",
        key=st.session_state.input_key
    )

    # BUTTONS
    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        ask_clicked = st.button("Ask AI")

    with col3:
        clear_clicked = st.button("❌ Clear")

    # CLEAR BUTTON
    if clear_clicked:
        st.session_state.input_key = (
            "input_2" if st.session_state.input_key == "input_1" else "input_1"
        )
        st.session_state.ai_output = None
        st.rerun()

    # ASK BUTTON
    if ask_clicked:

        if not question.strip():
            st.warning("Please enter a question")
            return

        # 🔥 SPINNER (SHORT + SAFE)
        with st.spinner("Analyzing your finances... 🤔"):

            # SHOW SUGGESTIONS IMMEDIATELY
            fallback_advice(income, budget, total, question)

            # SAVE OUTPUT
            st.session_state.ai_output = ("fallback", question)

        # 🔥 TRY AI (OPTIONAL, NO BLOCK UI)
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

    # SHOW PREVIOUS OUTPUT
    elif st.session_state.ai_output:

        mode, data = st.session_state.ai_output

        if mode == "fallback":
            fallback_advice(income, budget, total, data)
