from datetime import datetime,timedelta
from dateutil import parser as date_parser

def detect_spoken_date(text):

    text=text.lower()
    today=datetime.today()

    if "yesterday" in text:
        return (today-timedelta(days=1)).strftime("%Y-%m-%d")

    if "today" in text:
        return today.strftime("%Y-%m-%d")

    try:
        parsed=date_parser.parse(text,fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except:
        return today.strftime("%Y-%m-%d")