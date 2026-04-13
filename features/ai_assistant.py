import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS
import concurrent.futures


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

def get_ai_response(context, question):
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

    # -------- SESSION STATE --------
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    if "clear_flag" not in st.session_state:
        st.session_state.clear_flag = False

    # -------- HANDLE CLEAR SAFELY --------
    if st.session_state.clear_flag:
        st.session_state.ai_input = ""
        st.session_state.clear_flag = False

    # -------- INPUT --------
    question = st.text_input(
        "Ask about your finances",
        key="ai_input"
    )

    # -------- BUTTONS (PROPER POSITION) --------
    col1, col2 = st.columns([1,1])

    with col1:
        ask_clicked = st.button("Ask AI")

    with col2:
        if st.button("❌ Clear"):
            st.session_state.clear_flag = True
            st.rerun()

    # ENTER KEY SUPPORT
    if question and not ask_clicked:
        ask_clicked = True

    # -------- EXECUTION --------
    if ask_clicked:

        if not question.strip():
            st.warning("Please enter a question")
            return

        context = f"""
Income: {income}
Budget: {budget}
Spending: {total}
"""

        result = None

        # 🔥 THREAD + TIMEOUT (KEY FIX)
        with st.spinner("Analyzing your finances... 🤔"):

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(get_ai_response, context, question)

                try:
                    # ⏱️ WAIT MAX 10 SECONDS
                    result = future.result(timeout=10)

                except concurrent.futures.TimeoutError:
                    result = None

        # -------- OUTPUT --------
        if result:
            st.subheader("🤖 AI Insight")
            st.write(result)
        else:
            fallback_advice(income, budget, total, question)
