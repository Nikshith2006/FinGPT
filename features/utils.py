from datetime import datetime, timedelta
import re
from dateutil import parser as date_parser

def detect_spoken_date(text):
    text = text.lower()
    today = datetime.today()

    if "day before yesterday" in text:
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")
    elif "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    elif "today" in text:
        return today.strftime("%Y-%m-%d")

    match = re.search(r"(\d+)\s+days?\s+ago", text)
    if match:
        return (today - timedelta(days=int(match.group(1)))).strftime("%Y-%m-%d")

    try:
        parsed = date_parser.parse(text, fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except:
        return today.strftime("%Y-%m-%d")
