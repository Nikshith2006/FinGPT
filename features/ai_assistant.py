import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS
import threading
import time

# CONFIG
genai.configure(api_key=GOOGLE_API_KEYS[0])


# ---------------- AI BACKGROUND ----------------
def run_ai(context, question, result_container):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content(
            context + "\nUser Question: " + question,
            generation_config={"temperature": 0.7}
        )

        if response and hasattr(response, "text"):
            result_container["result"] = response.text

    except:
        result_container["result"] = None


# ---------------- MAIN ----------------
def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    # SESSION STATE
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""

    if "ai_response" not in st.session_state:
        st.session_state.ai_response = None

    if "ai_done" not in st.session_state:
        st.session_state.ai_done = False

    # CLEAR FUNCTION
    def clear_all():
        st.session_state.ai_input = ""
        st.session_state.ai_response = None
        st.session_state.ai_done = False

    # INPUT
    question = st.text_input(
        "Ask about your finances",
        key="ai_input",
        placeholder="Ask something like: How can I save more money?"
    )

    # BUTTONS
    col1, col2, col3 = st.columns([1,6,1])

    with col1:
        ask_clicked = st.button("Ask AI")

    with col3:
        st.button("Clear", on_click=clear_all)

    # TRIGGER
    trigger = question and (ask_clicked or question)

    if trigger:

        # RESET
        st.session_state.ai_response = None
        st.session_state.ai_done = False

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
2. ⚠ Problems
3. 💡 Suggestions
4. 🎯 Action Plan
5. 📈 Smart Tip
"""

        result_container = {"result": None}

        # START AI THREAD
        thread = threading.Thread(
            target=run_ai,
            args=(context, question, result_container)
        )
        thread.start()

        # 🔥 SPINNER (MAX 15 SECONDS)
        with st.spinner("🤖 Thinking..."):
            for _ in range(15):
                time.sleep(1)
                if result_container["result"] is not None:
                    break

        # RESULT CHECK
        if result_container["result"]:
            st.session_state.ai_response = result_container["result"]
            st.session_state.ai_done = True
        else:
            st.session_state.ai_done = False

    # ---------------- OUTPUT ----------------
    if st.session_state.ai_response:
        st.success(st.session_state.ai_response)
