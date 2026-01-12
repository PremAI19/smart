print("🚀 chatbot.py started")

import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from collections import deque

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
# Config
# ==============================
PDF_PATH = "data/sample_statements.pdf"
MAX_PDF_CHARS = 4000        # Prevent OOM
MAX_RESPONSE_TOKENS = 300   # Safe limit

# ==============================
# Conversation memory (SHORT TERM)
# ==============================
chat_memory = deque(maxlen=6)  # stores last 3 user-bot turns

# ==============================
# Read PDF safely
# ==============================
def read_pdf(path):
    try:
        reader = PdfReader(path)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

            if len(text) >= MAX_PDF_CHARS:
                break  # 🚨 critical safety

        print(f"📄 PDF loaded ({len(text)} characters)")
        return text.strip()

    except Exception as e:
        print("❌ Failed to read PDF:", e)
        return ""

# ==============================
# Generate AI response
# ==============================
def generate_response(user_input, pdf_text):
    memory_context = "\n".join(chat_memory)

    prompt = f"""
You are a smart personal finance assistant.

Conversation memory:
{memory_context}

Below is a PARTIAL bank statement extracted from a PDF.
Do NOT hallucinate numbers. Use trends, categories, and logic.

PDF CONTENT:
{pdf_text}

User question:
{user_input}

Rules:
- Use numbers ONLY if clearly visible in PDF
- Prefer trends, patterns, categories
- Max 5 concise lines
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=MAX_RESPONSE_TOKENS
    )

    return response.choices[0].message.content.strip()

# ==============================
# Main chatbot loop
# ==============================
if __name__ == "__main__":
    print("✅ MAIN BLOCK RUNNING")
    print("💰 Smart Personal Finance Chatbot (PDF + Memory)")
    print("Type 'exit' to quit\n")

    pdf_text = read_pdf(PDF_PATH)

    if not pdf_text:
        print("❌ No PDF content loaded. Exiting.")
        exit(1)

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        try:
            answer = generate_response(user_input, pdf_text)

            # 🧠 update memory
            chat_memory.append(f"User: {user_input}")
            chat_memory.append(f"Assistant: {answer}")

            print("Bot:", answer)

        except Exception as e:
            print("❌ Error:", e)
