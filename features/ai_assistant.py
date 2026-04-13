import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS
import time


# ---------------- FALLBACK ----------------

def fallback_advice(income, budget, total, question):

    st.subheader("💡 Smart Financial Suggestions")

    savings = income - total

    if "hi" in question.lower():
        st.write("👋 Hello! Here's your financial summary:")

    if total > budget:
        suggestions = [
            "🚨 You are overspending. Cut unnecessary expenses",
            "🛑 Avoid shopping & entertainment",
            "📊 Track daily expenses",
            "🍔 Reduce outside food",
            "💡 Focus on essentials",
            "📉 Bring spending under budget"
        ]

    elif total > 0.8 * budget:
        suggestions = [
            "⚠️ Close to budget limit",
            "📊 Monitor spending",
            "🛍 Avoid impulse buying",
            "🍽 Reduce eating out",
            "📅 Plan remaining days",
            "💡 Save small amount"
        ]

    elif total > 0.5 * budget:
        suggestions = [
            "👍 Moderate spending",
            "💰 Increase savings",
            "📊 Optimize expenses",
            "🛍 Avoid luxury",
            "📈 Start investing",
            "💡 Plan ahead"
        ]

    else:
        suggestions = [
            "🎉 Excellent management!",
            "💰 Saving well",
            "📈 Invest savings",
            "🛡 Build emergency fund",
            "📊 Track consistency",
            "🚀 Explore passive income"
        ]

    for s in suggestions:
        st.write("•", s)

    st.success(f"💰 Savings: ₹{savings}")


# ---------------- AI CALL ----------------

def try_ai(context, question):
    try:
        genai.configure(api_key=GOOGLE_API_KEYS[0])
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(context + question)

        if response and hasattr(response, "text"):
            return response.text
    except:
        return None

    return None


# ---------------- MAIN ----------------

def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # SAFE SESSION STATE INIT
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    if "ask_clicked" not in st.session_state:
        st.session_state.ask_clicked = False

    if "clear_clicked" not in st.session_state:
        st.session_state.clear_clicked = False

    # 🔥 HANDLE CLEAR SAFELY BEFORE INPUT
    if st.session_state.clear_clicked:
        st.session_state.ai_input = ""
        st.session_state.clear_clicked = False

    # ---------------- INPUT ----------------

    question = st.text_input(
        "Ask about your finances",
        key="ai_input"
    )

    # ---------------- BUTTONS ----------------

    col1, col2 = st.columns([1,1])

    with col1:
        if st.button("Ask AI"):
            st.session_state.ask_clicked = True

    with col2:
        if st.button("❌ Clear"):
            st.session_state.clear_clicked = True
            st.rerun()

    # ENTER KEY SUPPORT
    if question and not st.session_state.ask_clicked:
        st.session_state.ask_clicked = True

    # ---------------- EXECUTION ----------------

    if st.session_state.ask_clicked:

        st.session_state.ask_clicked = False  # 🔥 prevent loop

        if not question.strip():
            st.warning("Please enter a question")
            return

        context = f"""
Income: {income}
Budget: {budget}
Spending: {total}
"""

        result = None

        # 🔥 SAFE TIME LIMIT
        with st.spinner("Analyzing your finances... 🤔"):

            start = time.time()

            try:
                result = try_ai(context, question)
            except:
                result = None

            # ⏱️ If takes too long → fallback
            if time.time() - start > 10:
                result = None

        # ---------------- OUTPUT ----------------

        if result:
            st.subheader("🤖 AI Insight")
            st.write(result)
        else:
            fallback_advice(income, budget, total, question)
