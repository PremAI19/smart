import openai
import pandas as pd
from dotenv import load_dotenv
import os

# Load variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Loaded from environment

def load_data(path="data/cleaned_statements.csv"):
    """Load processed transaction data"""
    try:
        df = pd.read_csv(path)
        return df
    except:
        return pd.DataFrame()

def generate_response(user_input, df):
    if df.empty or "amount" not in df.columns:
        summary = "No financial data available."
    else:
        # Aggregate only (VERY important)
        total_spent = df[df["amount"] < 0]["amount"].sum()
        total_income = df[df["amount"] > 0]["amount"].sum()
        txn_count = len(df)

        summary = (
            f"Total transactions: {txn_count}. "
            f"Total income: {total_income:.2f}. "
            f"Total spending: {abs(total_spent):.2f}."
        )

    prompt = f"""
    You are a smart personal finance assistant.

    Financial summary (aggregated, not raw data):
    {summary}

    User question:
    {user_input}

    Give a concise, practical financial insight (max 5 lines).
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200  # 🚨 LIMIT OUTPUT
    )

    return response.choices[0].message.content
