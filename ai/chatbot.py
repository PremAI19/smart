import os
import pandas as pd
import pdfplumber
from dotenv import load_dotenv
from groq import Groq

# ==============================
# Load environment variables
# ==============================
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)

# ==============================
# Load data directly from PDF
# ==============================
def load_data(path="data/sample_statements.pdf"):
    if not os.path.exists(path):
        print(f"⚠️ PDF not found: {path}")
        return pd.DataFrame()

    rows = []

    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table and len(table) > 1:
                rows.extend(table[1:])  # skip header row

    if not rows:
        print("⚠️ No tables found in PDF")
        return pd.DataFrame()

    # Adjust columns if your PDF differs
    df = pd.DataFrame(rows, columns=["date", "description", "amount"])

    # Clean amount column
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("$", "", regex=False)
    )
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

    return df

# ==============================
# Generate LLM response
# ==============================
def generate_response(user_input, df):
    summary = "No financial data available."

    if not df.empty and "amount" in df.columns:
        total_spent = df[df["amount"] < 0]["amount"].sum()
        total_income = df[df["amount"] > 0]["amount"].sum()

        summary = (
            f"Total income: {total_income:.2f}. "
            f"Total spending: {abs(total_spent):.2f}."
        )

    prompt = f"""
    You are a smart personal finance assistant.

    Financial summary:
    {summary}

    User question:
    {user_input}

    Give a clear, practical financial insight.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ==============================
# Run chatbot in terminal
# ==============================
if __name__ == "__main__":
    df = load_data()

    print("💰 Personal Finance Chatbot (PDF-based)")
    print("Type 'exit' to quit\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye 👋")
            break

        try:
            answer = generate_response(user_input, df)
            print("Bot:", answer)
        except Exception as e:
            print("Error:", e)
