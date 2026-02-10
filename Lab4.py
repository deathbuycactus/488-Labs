import streamlit as st
from openai import OpenAI
import sys
import chromadb
from pathlib import Path
from PyPDF2 import PdfReader
import google.generativeai as genai
from bs4 import BeautifulSoup
import requests

# ChomaDB fix
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_Lab')
collection = chroma_client.get_or_create_coillection('Lab4Collection')

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(api_key=st.secrets["lab_key"]["IST488"])

def add_to_collection(collection, text, file_name):

    # Create an embedding
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=text,
        model='text-embedding-3-small'
    )

    # Get the embedding
    embedding = response.data[0].embedding

    # Add embedding and document to ChromaDB
    collection.add(
        documents=[text],
        ids=file_name,
        embeddings=[embedding]
    )

def extract_text_from_pdf(pdf_path):
    
def load_pdfs_to_colletion(folder_path, collection):

if collection.count() == 0:
    loaded = load_pdfs_to_colletion('./Lab-04-Data/', collection)

### MAIN APP ###

st.title('Lab 4: Chatbot using RAG')


# Show title and descr
st.title("My HW 3 Question Answering Chatbot")
st.write("This is a question answering chatbot. It takes up to two URLs and will attempt to answer questions you ask about them. " \
"After your 4th prompt or after you respond that you do not want more information, it will summarize the interaction you had with it.")

LLM = st.sidebar.selectbox("Which Model?",
                            ("ChatGPT", "Gemini"))
def read_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    except requests.RequestException as e:
        print(f"Error reading {url}: {e}")
        return None 
    
URL1 = URL1 = st.text_input(
    "Enter a URL",
    placeholder="https://example1.com"
)

URL1_content = read_url_content(URL1)

URL2 = URL2 = st.text_input(
    "Enter a URL",
    placeholder="https://example2.com"
)

URL2_content = read_url_content(URL2)


if LLM == "ChatGPT":
    model_choice = "gpt-4o-mini"
else:
    model_choice = "gemini-2.5-pro"

# Create GPT Client
if LLM == "ChatGPT" and 'client' not in st.session_state:
    api_key = st.secrets["IST488"]
    st.session_state.client = OpenAI(api_key=api_key)
if LLM == "Gemini":
    genai.configure(api_key=st.secrets["IST488_G"])


if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": f"""
            You are a question-answering assistant.
            You will answer questions that pertain to {URL1_content} and/or {URL2_content}. Do not forget the contents of these websites.
            End first response: 'Do you want more information?' 
            If they want more information continue asking if they want more until they say no, then summarize the conversation. 
            Keep your answers simple enough such that a ten year old can understand them.
            If you reach 3 user-assistant exchanges, summarize the conversation so far, then replace the conversation history with that summary reponse.
            """
        },
        {
            "role": "assistant",
            "content": "How can I help you?"
        }
    ]


    
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    chat_msg = st.chat_message(msg["role"])
    chat_msg.write(msg["content"])

# Conversation buffer
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({
        "role": "user",
        "content": prompt})    
    with st.chat_message("user"):
        st.markdown(prompt)
    if LLM == "ChatGPT":
        client = st.session_state.client
        stream = client.chat.completions.create(
            model = model_choice,
            messages = st.session_state.messages, 
            stream = True)
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
    elif LLM == "Gemini":
        model = genai.GenerativeModel(model_choice)
        history = "\n".join(
            f"{m['role'].upper()}: {m['content']}"
            for m in st.session_state.messages
            if m["role"] != "system"
        )
        
        gemini_prompt = f"""
            You are a question-answering assistant.

            You will answer questions that pertain to {URL1_content} and/or {URL2_content}. Do not forget the contents of these websites.
            
            Conversation so far:
            {history}

            Rules:
            End first response: 'Do you want more information?' 
            If they want more information continue asking if they want more until they say no, then summarize the conversation. 
            Keep your answers simple enough such that a ten year old can understand them.
            If you reach 3 user-assistant exchanges, answer the user's question and provide a summary of the conversation as part of your response.
            
            User question:
            {prompt}
            """
        response = model.generate_content(gemini_prompt)
        assistant_text = response.text
        with st.chat_message("assistant"):
            st.write(assistant_text)

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_text
        })




#### QUERYING A COLLECTION -- ONLY USED FOR TESTING ####

topic = st.sidebar.text_input('Topic', placeholder='Type your topic (e.g., GenAI)...')

if topic:
    client = st.session_state.openai_client
    response = client.embeddings.create(
        input=topic,
        model='text-embedding-3-small'
    )
    
    # Get the embedding
    query_embedding = response.data[0].embedding

    # Get the text related to this question (this prompt)
    results = collection.query(
        query_embedding=[query_embedding],
        n_results=3 # Number of closest documents to return
    )

    # Display the results
    st.subheader(f"Results for: {topic}")

    for i in range(len(results['documents'][0])):
        doc = results['documents'][0][i]
        doc_id = results['ids'][0][i]
        st.write(f"**{i+1}, {doc_id}**")

else:
    st.info('Enter a topic in the sidebar to search the collection')