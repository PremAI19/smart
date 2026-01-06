import pandas as pd
from dotenv import load_dotenv
import os
#from openai import OpenAI
from groq import Groq

# Load environment variables
#load_dotenv()
#OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#if not OPENAI_API_KEY:
#    raise ValueError("OpenAI API key not found! Please add it to .env")
# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found! Please add it to .env")

client = Groq(api_key=GROQ_API_KEY)

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def load_data(path="data/cleaned_statements.csv"):
    """Load processed transaction data"""
    try:
        df = pd.read_csv(path)
        return df
    except:
        return pd.DataFrame()

def generate_response(user_input, df):
    """Use GPT to answer user questions about expenses"""
    summary = ""
    if not df.empty:
        total_spent = df['amount'][df['amount'] < 0].sum()
        total_income = df['amount'][df['amount'] > 0].sum()
        summary = f"Your total income is {total_income:.2f} and total spending is {abs(total_spent):.2f}."

    prompt = f"""
    You are a smart personal finance assistant. 
    Use this data summary: {summary}
    User asked: {user_input}
    Provide a helpful, concise financial insight.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
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
