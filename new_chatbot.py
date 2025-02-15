import streamlit as st
from pymongo import MongoClient
import gridfs

import google.generativeai as genai
genai.configure(api_key="AIzaSyB0N5bUMNMzgy9Cah0Y7eNAz9BRawr7Xqw")
model = genai.GenerativeModel("gemini-1.5-flash")

client = MongoClient("mongodb://localhost:27017/")
db = client['calmconnect_db']
feelings_collection = db['feelings']
fs = gridfs.GridFS(db)

def generate_response(user_input):
    try:
        prompt = f"You are a supportive and empathetic chatbot. Provide thoughtful advice or suggestions based on the user's input: '{user_input}'"
        response = model.generate_content(prompt)
        return response.text.strip() if response.text else "No response available."
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return "I'm here for you! What else would you like to talk about?"

def chatbot_interface():
    st.subheader("Welcome to CalmConnect Chatbot!!")
    
    chat_history = st.session_state.get('chat_history', [])
    
    user_input = st.text_input("You:", "")
    
    if st.button("Send"):
        if user_input:
            chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history = chat_history

            chatbot_response = generate_response(user_input)
            chat_history.append({"role": "bot", "content": chatbot_response})
            st.session_state.chat_history = chat_history

    for message in chat_history:
        if message["role"] == "user":
            st.markdown(f"<span style='color: black; font-weight: bold;'>You: {message['content']}</span>", unsafe_allow_html=True)
        else:
            st.write(f"Bot: {message['content']}")

def main():
    st.title("CalmConnect")
    chatbot_interface()

if __name__ == "__main__":
    main()
