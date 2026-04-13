def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # 🔥 SESSION STATE FOR OUTPUT (IMPORTANT)
    if "ai_output" not in st.session_state:
        st.session_state.ai_output = None

    if "input_key" not in st.session_state:
        st.session_state.input_key = "input_1"

    # INPUT
    question = st.text_input(
        "Ask about your finances",
        key=st.session_state.input_key
    )

    # BUTTONS (ASK LEFT, CLEAR RIGHT)
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
        st.session_state.ai_output = None   # 🔥 clear output also
        st.rerun()

    # ASK BUTTON
    if ask_clicked:

        if not question.strip():
            st.warning("Please enter a question")
            return

        with st.spinner("Analyzing your finances... 🤔"):

            # 🔥 SAVE OUTPUT IN STATE (KEY FIX)
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
                st.session_state.ai_output = ("ai", response.text)

        except:
            pass

    # 🔥 DISPLAY OUTPUT (AFTER BUTTONS → FIXES GRAPH ISSUE)
    if st.session_state.ai_output:

        mode, data = st.session_state.ai_output

        if mode == "fallback":
            fallback_advice(income, budget, total, data)

        elif mode == "ai":
            st.subheader("🤖 AI Insight")
            st.write(data)
