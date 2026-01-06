import pandas as pd
from dotenv import load_dotenv
import os
from groq import Groq

# ==============================
# Load environment variables
# ==============================
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found! Please add it to .env")

# ==============================
# Create Groq client
# ==============================
client = Groq(api_key=GROQ_API_KEY)

# ==============================
# Data loading
# ==============================
def load_data(path="data/cleaned_statements.csv"):
    """Load processed transaction data"""
    try:
        return pd.read_csv(path)
    except Exception as e:
        print("Failed to load data:", e)
        return pd.DataFrame()

# ==============================
# LLM response generation
# ==============================
def generate_response(user_input, df):
    """Use Groq LLM to answer user questions about expenses"""

    summary = ""
    if not df.empty and "amount" in df.columns:
        total_spent = df[df["amount"] < 0]["amount"].sum()
        total_income = df[df["amount"] > 0]["amount"].sum()
        summary = (
            f"Your total income is {total_income:.2f} "
            f"and total spending is {abs(total_spent):.2f}."
        )

    prompt = f"""
    You are a smart personal finance assistant.
    Use this data summary: {summary}
    User asked: {user_input}
    Provide a helpful, concise financial insight.
    """

    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ==============================
# Run chatbot in terminal
# ==============================
if __name__ == "__main__":
    df = load_data()
    print("Smart Personal Finance Chatbot is running! Type 'exit' to quit.")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        try:
            answer = generate_response(user_input, df)
            print("Bot:", answer)
        except Exception as e:
            print("Error:", e)
