import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS
import time


# ---------------- CONFIG ----------------
genai.configure(api_key=GOOGLE_API_KEYS[0])


# ---------------- MAIN FUNCTION ----------------
def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # ---------------- SESSION STATE ----------------
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    if "ai_response" not in st.session_state:
        st.session_state.ai_response = ""

    # ---------------- CLEAR FUNCTION ----------------
    def clear_all():
        st.session_state.ai_input = ""
        st.session_state.ai_response = ""

    # ---------------- INPUT ----------------
    question = st.text_input(
        "Ask about your finances",
        key="ai_input",
        placeholder="Ask something like: How can I save more money?"
    )

    # ---------------- BUTTONS (BOTTOM LEFT & RIGHT) ----------------
    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        ask_clicked = st.button("Ask AI")

    with col3:
        st.button("Clear", on_click=clear_all)

    # ---------------- TRIGGER ----------------
    trigger = question and (ask_clicked or question)

    if trigger:

        context = f"""
You are a smart Indian personal finance assistant.

STRICT RULES:
- Always use Indian Rupees (₹), NEVER use dollars ($)
- Give structured, clear, and practical advice

User Financial Data:
Monthly Income: ₹{income}
Monthly Budget: ₹{budget}
Current Spending: ₹{total}

RESPONSE FORMAT:

1. 📊 Current Situation
- Explain clearly

2. ⚠ Problems (if any)
- Identify risks

3. 💡 Suggestions
- Give 3–5 practical tips

4. 🎯 Action Plan
- Give steps to improve

5. 📈 Smart Tip
- One extra helpful tip
"""

        try:
            # 🔥 SPINNER (WAIT UNTIL RESPONSE)
            with st.spinner("🤖 Thinking..."):

                model = genai.GenerativeModel("gemini-2.5-flash")

                # 🔥 RETRY LOGIC
                for attempt in range(3):
                    try:
                        response = model.generate_content(
                            context + "\nUser Question: " + question,
                            generation_config={"temperature": 0.7}
                        )

                        if response and hasattr(response, "text"):
                            st.session_state.ai_response = response.text
                            break

                    except Exception:
                        if attempt < 2:
                            time.sleep(2)
                        else:
                            raise

        except Exception:
            st.error("⚠ AI is busy right now. Please try again.")

    # ---------------- OUTPUT ----------------
    if st.session_state.ai_response:
        st.success(st.session_state.ai_response)
