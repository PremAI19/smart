print("🚀 chatbot.py started")

import os
import re
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from collections import defaultdict, deque

# ==============================
# Config
# ==============================
PDF_PATH = "data/sample_statements.pdf"
MAX_CHARS = 4500
MAX_MEMORY_TURNS = 6

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
# Chat memory
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
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

            if len(text) > MAX_CHARS:
                break

        print(f"📄 PDF loaded ({len(text)} characters)")
        return text.strip()

    except Exception as e:
        print("❌ Failed to read PDF:", e)
        return ""

# ==============================
# Extract monthly amounts (REAL)
# ==============================
def extract_monthly_amounts(pdf_text):
    """
    Extracts amounts per month using regex.
    This avoids hallucination.
    """
    month_totals = defaultdict(float)

    pattern = re.compile(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*.*?([0-9,]+\.\d{2})",
        re.IGNORECASE
    )

    for month, amount in pattern.findall(pdf_text):
        month = month.capitalize()
        value = float(amount.replace(",", ""))
        month_totals[month] += value

    return dict(month_totals)

# ==============================
# Generate AI response
# ==============================
def generate_response(user_input, pdf_text, monthly_amounts):
    memory_context = "\n".join(chat_memory)

    amount_summary = (
        "\n".join(f"{m}: {v:.2f}" for m, v in monthly_amounts.items())
        if monthly_amounts else
        "No numeric totals could be reliably extracted."
    )

    prompt = f"""
You are a smart personal finance assistant.

You are analyzing BANK STATEMENT DATA extracted from a PDF.

IMPORTANT RULES:
- Monthly totals below are REAL (Python-extracted)
- Do NOT invent numbers
- You may reason and compare using provided totals

Monthly spending totals:
{amount_summary}

Conversation memory:
{memory_context}

User question:
{user_input}

If asked:
- Say which month has highest spending
- Compare months numerically
- Give practical advice

Keep answer under 6 lines.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=350
    )

    reply = response.choices[0].message.content

    chat_memory.append(f"User: {user_input}")
    chat_memory.append(f"Assistant: {reply}")

    return reply

# ==============================
# Main loop
# ==============================
if __name__ == "__main__":
    print("💰 Personal Finance Chatbot (PDF + Amounts + Memory)")
    print("Type 'exit' to quit\n")

    pdf_text = read_pdf(PDF_PATH)

    if not pdf_text:
        print("❌ No PDF content loaded. Exiting.")
        exit(1)

    monthly_amounts = extract_monthly_amounts(pdf_text)

    if monthly_amounts:
        print("📊 Monthly totals extracted:")
        for m, v in monthly_amounts.items():
            print(f"   {m}: {v:.2f}")
    else:
        print("⚠️ No numeric totals detected")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        try:
            answer = generate_response(user_input, pdf_text, monthly_amounts)
            print("Bot:", answer)
        except Exception as e:
            print("❌ Error:", e)
