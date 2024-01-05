# -*- coding: utf-8 -*-
"""
Created on Thu Nov  2 16:00:05 2023

@author: Thuy-trang
"""
__import__('pysqlite3')
import sys

sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import streamlit as st
#import openai
import os
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.document_loaders import Docx2txtLoader
os.environ["OPENAI_API_KEY"] = "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"


st.header("Chat with me 💬 📚")
st.image("1.png")
if "messages" not in st.session_state.keys(): # Initialize the chat message history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading information – hang tight! This should take 1-2 minutes."):
        loader = DirectoryLoader("SOURCE_DOCUMENTS/")
        index = VectorstoreIndexCreator().from_loaders([loader])
        return index
    
uploaded_files = st.file_uploader("Upload files (pdf, docx , txt)", type=["pdf", "docx", "txt"], accept_multiple_files=True)

@st.cache_resource(show_spinner=False)
def process_files():
    text = []
    for file in uploaded_files:
        file_extension = os.path.splitext(file.name)[1]
        loader = None
        if file_extension == ".pdf":
            loader = PyPDFLoader(file.name)
        elif file_extension == ".docx" or file_extension == ".doc":
            loader = Docx2txtLoader(file.name)
        elif file_extension == ".txt":
            loader = TextLoader(file.name)

        if loader:
            text.extend(loader.load())
    combined_text_loader = TextLoader.from_text("\n".join(text))
    index = VectorstoreIndexCreator().from_loaders([combined_text_loader])
    return index


    

#index = load_data()
if uploaded_files:
    index = process_files()
else:
    index = load_data()
if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])
        
# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = index.query(prompt, llm = ChatOpenAI(model="gpt-4-1106-preview"))
            st.write(response)
            message = {"role": "assistant", "content": response}
            st.session_state.messages.append(message)
