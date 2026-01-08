print("🚀 chatbot.py started")

import os
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from collections import deque

# ==============================
# Config
# ==============================
PDF_PATH = "data/sample_statements.pdf"
MAX_CHARS = 4500          # Prevent memory kill
MAX_MEMORY_TURNS = 5      # Chat memory size

# ==============================
# Load environment variables
# ==============================
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not API_KEY:
    raise ValueError("❌ GROQ_API_KEY not found")

client = Groq(api_key=API_KEY)

# ==============================
# Conversation Memory
# ==============================
chat_memory = deque(maxlen=MAX_MEMORY_TURNS)

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

            if len(text) > MAX_CHARS:
                break

        print(f"📄 PDF loaded ({len(text)} characters)")
        return text.strip()

    except Exception as e:
        print("❌ PDF read failed:", e)
        return ""

# ==============================
# Generate AI response
# ==============================
def generate_response(user_input, pdf_text):
    memory_context = ""
    for turn in chat_memory:
        memory_context += f"{turn}\n"

    prompt = f"""
You are a smart personal finance assistant.

You are analyzing BANK STATEMENT DATA extracted from a PDF.
- Infer trends, not exact amounts
- Identify monthly patterns
- Detect changes over time
- Be conservative (do NOT hallucinate numbers)

PDF CONTENT (partial):
{pdf_text}

Conversation memory:
{memory_context}

User question:
{user_input}

If asked about trends:
- Mention months
- Identify increase/decrease patterns
- Suggest actions

Answer in max 6 concise lines.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350
    )

    reply = response.choices[0].message.content

    # Save memory
    chat_memory.append(f"User: {user_input}")
    chat_memory.append(f"Assistant: {reply}")

    return reply

# ==============================
# Main Loop
# ==============================
if __name__ == "__main__":
    print("💰 Personal Finance Chatbot (PDF + Trends + Memory)")
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
