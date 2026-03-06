from fastapi import FastAPI
import pandas as pd
from datetime import datetime

app = FastAPI()

@app.post("/add-expense/")
def add_expense(user: str, amount: float, category: str, description: str):
    df = pd.read_csv("expenses.csv")

    new_row = {
        "Date": datetime.today().strftime("%Y-%m-%d"),
        "Category": category,
        "Amount": amount,
        "Description": description,
        "User": user
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv("expenses.csv", index=False)

    return {"message": "Expense added successfully"}