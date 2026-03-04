from datetime import datetime, timedelta
import re
from dateutil import parser as date_parser

# ---------------- DATE DETECTION ----------------
def detect_spoken_date(text):
    text = text.lower()
    today = datetime.today()

    if "day before yesterday" in text:
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")

    if "yesterday" in text:
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")

    if "today" in text:
        return today.strftime("%Y-%m-%d")

    match = re.search(r"(\d+)\s+days?\s+ago", text)
    if match:
        return (today - timedelta(days=int(match.group(1)))).strftime("%Y-%m-%d")

    try:
        parsed = date_parser.parse(text, fuzzy=True)
        return parsed.strftime("%Y-%m-%d")
    except:
        return today.strftime("%Y-%m-%d")


# ---------------- HEALTH SCORE ----------------
def calculate_health_score(income, spent):

    if income == 0:
        return 300, "Poor"

    ratio = spent / income
    score = 900 - int(ratio * 600)

    score = max(300, min(score, 900))

    if score >= 750:
        rating = "Excellent"
    elif score >= 650:
        rating = "Good"
    elif score >= 550:
        rating = "Average"
    else:
        rating = "Poor"

    return score, rating