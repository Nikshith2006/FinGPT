import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Google API scopes
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials from Streamlit Secrets
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

# Authorize client
client = gspread.authorize(creds)

# Open your Google Sheet
spreadsheet = client.open("FinGPT Database")

# Access worksheets
expenses_sheet = spreadsheet.worksheet("expenses")
users_sheet = spreadsheet.worksheet("users")
