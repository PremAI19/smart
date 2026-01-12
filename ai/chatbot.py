print("🚀 chatbot.py started")

import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader

# ==============================
# Load environment variables
# ==============================
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found in .env")

client = Groq(api_key=API_KEY)

PDF_PATH = "data/sample_statements.pdf"
MAX_CHARS = 4000  # 🚨 prevent memory kill

# ==============================
# Read PDF safely
# ==============================
def read_pdf(path):
    try:
        reader = PdfReader(path)
        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

            if len(text) > MAX_CHARS:
                break  # 🚨 VERY IMPORTANT

        print(f"📄 PDF loaded ({len(text)} characters)")
        return text.strip()

    except Exception as e:
        print("❌ Failed to read PDF:", e)
        return ""

# ==============================
# Generate AI response
# ==============================
def generate_response(user_input, pdf_text):
    prompt = f"""
You are a smart personal finance assistant.

Below is a PARTIAL bank statement extracted from a PDF.
Summarize and infer insights — do NOT hallucinate numbers.

PDF CONTENT:
{pdf_text}

User question:
{user_input}

Give practical financial advice (max 5 lines).
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
    print("💰 Personal Finance Chatbot (PDF Based)")
    print("Type 'exit' to quit\n")

    pdf_text = read_pdf(PDF_PATH)

    if not pdf_text:
        print("❌ No PDF content loaded. Exiting.")
        exit(1)

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        try:
            answer = generate_response(user_input, pdf_text)
            print("Bot:", answer)
        except Exception as e:
            print("❌ Error:", e)
