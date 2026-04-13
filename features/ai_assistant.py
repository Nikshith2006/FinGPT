def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # INIT STATE
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

        # 🔥 SHOW IMMEDIATELY (NO WAIT)
        fallback_advice(income, budget, total, question)

        # 🔥 SAVE STATE (for persistence)
        st.session_state.ai_output = ("fallback", question)

        # TRY AI (optional)
        try:
            import google.generativeai as genai
            from config import GOOGLE_API_KEYS

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

    # 🔥 ALSO SHOW PREVIOUS OUTPUT (important)
    elif st.session_state.ai_output:

        mode, data = st.session_state.ai_output

        if mode == "fallback":
            fallback_advice(income, budget, total, data)
