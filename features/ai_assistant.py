import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # ✅ SESSION STATE INIT
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    # -------- INPUT --------
    question = st.text_input(
        "Ask about your finances",
        key="ai_input"
    )

    # -------- BUTTONS (PROPER ALIGNMENT) --------
    col1, col2, col3 = st.columns([1,1,6])

    with col1:
        ask_clicked = st.button("Ask AI")

    with col2:
        clear_clicked = st.button("❌ Clear")

    # -------- CLEAR BUTTON FIX --------
    if clear_clicked:
        st.session_state.ai_input = ""
        st.rerun()

    # -------- ASK BUTTON --------
    if ask_clicked:

        if not question.strip():
            st.warning("Please enter a question")
            return

        # ✅ SPINNER ONLY FOR SHORT TIME
        with st.spinner("Analyzing your finances... 🤔"):

            # 👉 SHOW FALLBACK IMMEDIATELY
            fallback_advice(income, budget, total, question)

        # 🔥 AFTER SPINNER ENDS → TRY AI (NO SPINNER = NO HANG)
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
