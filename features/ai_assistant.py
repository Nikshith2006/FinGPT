import streamlit as st
import google.generativeai as genai
from config import GOOGLE_API_KEYS


def generate_with_key(api_key, prompt):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response
    except Exception as e:
        return e


def fallback_advice(income, budget, total, question):
    """Smart fallback suggestions"""

    st.subheader("💡 Smart Financial Suggestions")

    # Simple conversational response
    if "hi" in question.lower() or "hello" in question.lower():
        st.write("👋 Hello! Here’s your financial overview:")

    # Financial logic
    if total > budget:
        st.error("🚨 You are overspending!")
        st.write("• Reduce unnecessary expenses")
        st.write("• Avoid shopping & entertainment for some time")

    elif total > 0.8 * budget:
        st.warning("⚠️ You are close to your budget limit")
        st.write("• Control your daily expenses")

    elif total > 0.5 * budget:
        st.info("👍 Your spending is moderate")
        st.write("• Try to save more this month")

    else:
        st.success("🎉 Excellent! You are saving well")
        st.write("• Consider investing your savings")

    # Savings insight
    savings = income - total
    st.write(f"💰 Estimated Savings: ₹{savings}")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    ask = st.button("Ask AI")

    if ask:

        if not question.strip():
            st.warning("Please enter a question")
            return

        context = f"""
You are a personal finance assistant.

User Financial Data:
Monthly Income: {income}
Monthly Budget: {budget}
Current Spending: {total}

Give helpful financial advice based on this data.
"""

        prompt = context + question

        response_text = None
        last_error = None

        with st.spinner("Thinking... 🤔"):

            # 🔥 TRY ALL KEYS
            for key in GOOGLE_API_KEYS:

                result = generate_with_key(key, prompt)

                if hasattr(result, "text") and result.text:
                    response_text = result.text
                    break
                else:
                    last_error = str(result)

        # ✅ SHOW AI RESPONSE
        if response_text:
            st.write(response_text)

        # 🔥 ALWAYS SHOW FALLBACK (NO BLANK SCREEN)
        else:
            fallback_advice(income, budget, total, question)
