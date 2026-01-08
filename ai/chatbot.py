print("🚀 chatbot.py started")

import os
import re
from dotenv import load_dotenv
from groq import Groq
from pypdf import PdfReader
from collections import defaultdict, deque

import speech_recognition as sr
import pyttsx3

# ==============================
# Config
# ==============================
PDF_PATH = "data/sample_statements.pdf"
MAX_CHARS = 4500
MAX_MEMORY_TURNS = 6
USE_VOICE = False  # Codespaces safe   # 🔊 Toggle voice on/off

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
# Voice setup
# ==============================
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 175)

def listen():
    """Capture voice input"""
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio)
        print(f"🗣️ You said: {text}")
        return text
    except sr.UnknownValueError:
        print("❌ Could not understand audio")
        return ""
    except sr.RequestError:
        print("❌ Speech service unavailable")
        return ""

def speak(text):
    """Convert text to speech"""
    tts_engine.say(text)
    tts_engine.runAndWait()

# ==============================
# Chat memory
# ==============================
chat_memory = deque(maxlen=MAX_MEMORY_TURNS)

# ==============================
# Read PDF safely
# ==============================
def read_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
        if len(text) > MAX_CHARS:
            break

    print(f"📄 PDF loaded ({len(text)} chars)")
    return text.strip()

# ==============================
# Extract monthly amounts
# ==============================
def extract_monthly_amounts(pdf_text):
    month_totals = defaultdict(float)

    pattern = re.compile(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*.*?([0-9,]+\.\d{2})",
        re.IGNORECASE
    )

    for month, amount in pattern.findall(pdf_text):
        month_totals[month.capitalize()] += float(amount.replace(",", ""))

    return dict(month_totals)

# ==============================
# Generate AI response
# ==============================
def generate_response(user_input, pdf_text, monthly_amounts):
    memory = "\n".join(chat_memory)

    totals = "\n".join(f"{m}: {v:.2f}" for m, v in monthly_amounts.items())

    prompt = f"""
You are a smart personal finance assistant.

Monthly totals (REAL, extracted):
{totals}

Conversation memory:
{memory}

User question:
{user_input}

Give concise, practical advice (max 5 lines).
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )

    reply = response.choices[0].message.content

    chat_memory.append(f"User: {user_input}")
    chat_memory.append(f"Assistant: {reply}")

    return reply

# ==============================
# Main loop
# ==============================
if __name__ == "__main__":
    print("💰 Voice-enabled Finance Chatbot")
    print("Say 'exit' or type 'exit' to quit\n")

    pdf_text = read_pdf(PDF_PATH)
    monthly_amounts = extract_monthly_amounts(pdf_text)

    while True:
        if USE_VOICE:
            user_input = listen()
            if not user_input:
                continue
        else:
            user_input = input("You: ")

        if user_input.lower() in ("exit", "quit"):
            speak("Goodbye!")
            break

        try:
            answer = generate_response(user_input, pdf_text, monthly_amounts)
            print("Bot:", answer)
            if USE_VOICE:
                speak(answer)
        except Exception as e:
            print("❌ Error:", e)
            speak("Sorry, something went wrong.")
