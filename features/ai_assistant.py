import streamlit as st
from google import genai
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def ask_ai(income,budget,expenses,question):

    context = f"""
    Income: {income}
    Budget: {budget}
    Total Spent: {expenses}
    """

    reply = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=context + question
    )

    return reply.text
