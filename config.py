import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from streamlit_oauth import OAuth2Component

load_dotenv()

GOOGLE_API_KEY=os.getenv("GOOGLE_API_KEY")
GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET")

AUTHORIZE_URL="https://accounts.google.com/o/oauth2/auth"
TOKEN_URL="https://oauth2.googleapis.com/token"

genai.configure(api_key=GOOGLE_API_KEY)
client = genai

oauth2=OAuth2Component(
GOOGLE_CLIENT_ID,
GOOGLE_CLIENT_SECRET,
AUTHORIZE_URL,
TOKEN_URL,
TOKEN_URL

)

