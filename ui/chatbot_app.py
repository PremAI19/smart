import streamlit as st
from ai.chatbot import load_data, generate_response
from ai.voice_utils import listen, speak

st.title("💬 Smart Personal Finance Chatbot")

df = load_data()

mode = st.radio("Select Mode:", ["Text Chat", "Voice Chat"])

if mode == "Text Chat":
    user_input = st.text_input("Type your question:")
    if st.button("Ask"):
        if user_input:
            answer = generate_response(user_input, df)
            st.write("**Chatbot:**", answer)
else:
    if st.button("🎤 Speak Now"):
        query = listen()
        if query:
            answer = generate_response(query, df)
            st.write("**Chatbot:**", answer)
            speak(answer)
