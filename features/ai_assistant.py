import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


# ---------------- FALLBACK SUGGESTIONS ----------------
def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    savings = income - total

    # 🔥 Generate 5–6 suggestions
    if total > budget:
        suggestions = [
            "🚨 You are overspending. Cut unnecessary expenses",
            "🛑 Avoid shopping temporarily",
            "📊 Track daily expenses strictly",
            "🍔 Reduce outside food and delivery",
            "💡 Focus only on essential needs",
            "📉 Bring spending under budget immediately"
        ]

    elif total > 0.8 * budget:
        suggestions = [
            "⚠️ You are close to your budget limit",
            "📊 Monitor your daily expenses carefully",
            "🛍 Avoid impulse purchases",
            "🍽 Reduce eating out",
            "📅 Plan remaining month expenses wisely",
            "💡 Try to save at least small amounts"
        ]

    elif total > 0.5 * budget:
        suggestions = [
            "👍 Your spending is moderate",
            "💰 Try increasing your savings",
            "📊 Optimize unnecessary expenses",
            "🛍 Avoid luxury purchases",
            "📈 Start small investments",
            "💡 Plan future expenses better"
        ]

    else:
        suggestions = [
            "🎉 Excellent financial management!",
            "💰 You are saving well",
            "📈 Consider investing your savings",
            "🛡 Build an emergency fund",
            "📊 Maintain consistent tracking",
            "🚀 Explore passive income ideas"
        ]

    for s in suggestions:
        st.write("•", s)

    st.success(f"💰 Estimated Savings: ₹{savings}")


# ---------------- MAIN FUNCTION ----------------
def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # 🔥 Session state for output
    if "ai_output" not in st.session_state:
        st.session_state.ai_output = None

    if "input_key" not in st.session_state:
        st.session_state.input_key = "input_1"

    # 🔥 INPUT FIELD
    question = st.text_input(
        "Ask about your finances",
        key=st.session_state.input_key
    )

    # 🔥 BUTTONS (Aligned Properly)
    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        ask_clicked = st.button("Ask AI")

    with col3:
        clear_clicked = st.button("❌ Clear")

    # 🔥 CLEAR BUTTON
    if clear_clicked:
        st.session_state.input_key = (
            "input_2" if st.session_state.input_key == "input_1" else "input_1"
        )
        st.session_state.ai_output = None
        st.rerun()

    # 🔥 ASK BUTTON
    if ask_clicked:

        if not question.strip():
            st.warning("Please enter a question")
            return

        # ✅ Spinner (short & clean)
        with st.spinner("Analyzing your finances... 🤔"):

            # Save fallback output
            st.session_state.ai_output = ("fallback", question)

        # 🔥 Try AI silently (no blocking UI)
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
                st.session_state.ai_output = ("ai", response.text)

        except:
            pass

    # 🔥 DISPLAY OUTPUT (prevents graph disappearing)
    if st.session_state.ai_output:

        mode, data = st.session_state.ai_output

        if mode == "fallback":
            fallback_advice(income, budget, total, data)

        elif mode == "ai":
            st.subheader("🤖 AI Insight")
            st.write(data)
