import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

scope = [
"https://www.googleapis.com/auth/spreadsheets",
"https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("FinGPT Database")

expenses_sheet = sheet.worksheet("expenses")
users_sheet = sheet.worksheet("users")
