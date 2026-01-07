print("🚀 chatbot.py started")

import pandas as pd
from dotenv import load_dotenv
import os
from groq import Groq

# ==============================
# Load environment variables
# ==============================
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)

# ==============================
# Load financial data
# ==============================
def load_data(path="data/cleaned_statements.csv"):
    try:
        df = pd.read_csv(path)
        print(f"📊 Loaded {len(df)} rows from {path}")
        return df
    except Exception as e:
        print("⚠️ Failed to load data:", e)
        return pd.DataFrame()

# ==============================
# Generate AI response
# ==============================
def generate_response(user_input, df):
    if df.empty or "amount" not in df.columns:
        summary = "No financial data available."
    else:
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
        max_tokens=300
    )

    return response.choices[0].message.content

# ==============================
# Main chatbot loop
# ==============================
if __name__ == "__main__":
    print("✅ MAIN BLOCK RUNNING")
    print("💰 Personal Finance Chatbot")
    print("Type 'exit' to quit\n")

    df = load_data()

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        try:
            answer = generate_response(user_input, df)
            print("Bot:", answer)
        except Exception as e:
            print("❌ Error:", e)
