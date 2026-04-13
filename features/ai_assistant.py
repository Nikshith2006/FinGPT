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


def fallback_advice(income, budget, total):
    """Smart local financial suggestions (no AI needed)"""

    st.subheader("💡 Smart Financial Suggestions")

    if total > budget:
        st.error("🚨 You are overspending!")
        st.write("• Reduce unnecessary expenses")
        st.write("• Focus on essential spending only")
        st.write("• Avoid shopping & entertainment temporarily")

    elif total > 0.8 * budget:
        st.warning("⚠️ You are close to your budget limit")
        st.write("• Control spending for the rest of the month")
        st.write("• Track daily expenses carefully")

    elif total > 0.5 * budget:
        st.info("👍 You are managing your budget fairly well")
        st.write("• Try to save more")
        st.write("• Avoid impulse purchases")

    else:
        st.success("🎉 Excellent financial management!")
        st.write("• You are saving well")
        st.write("• Consider investing your savings")

    # Extra suggestions
    if income > 0:
        savings = income - total
        st.write(f"💰 Estimated Savings: ₹{savings}")

        if savings > 0:
            st.write("• You can allocate savings to investments or emergency funds")
        else:
            st.write("• Try to increase savings by reducing expenses")


def ai_financial_assistant(income, budget, total):

    st.subheader("🤖 AI Financial Assistant")

    question = st.text_input("Ask about your finances")

    ask = st.button("Ask AI")

    if ask and question and question.strip():

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

        # 🔥 TRY ALL API KEYS
        for key in GOOGLE_API_KEYS:

            result = generate_with_key(key, prompt)

            if hasattr(result, "text"):
                response_text = result.text
                break

        # ✅ IF AI WORKS
        if response_text:
            st.write(response_text)

        # 🔥 IF AI FAILS → NO ERROR SHOWN
        else:
            fallback_advice(income, budget, total)
