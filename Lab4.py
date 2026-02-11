import streamlit as st
from openai import OpenAI
import sys
import chromadb
from pathlib import Path
from PyPDF2 import PdfReader
from bs4 import BeautifulSoup
import requests

# ChomaDB fix
__import__('pysqlite3')
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

# Create ChromaDB client
chroma_client = chromadb.PersistentClient(path='./ChromaDB_for_Lab')
collection = chroma_client.get_or_create_collection('Lab4Collection')

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
        ids=[file_name],
        embeddings=[embedding],
        metadatas=[{"source": file_name}]
    )

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text != None:
            text += page_text

    return text

def load_pdfs_to_collection(folder_path, collection):
    folder = Path(folder_path)

    for pdf_path in folder.glob("*.pdf"):
        try:
            # Extract text from PDF
            text = extract_text_from_pdf(pdf_path)

            # Use filename as ID
            file_name = pdf_path.name

            # Add to ChromaDB
            add_to_collection(collection, text, file_name)

        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}") 

# Check if collection is empty and load PDFs
if collection.count() == 0:
    loaded = load_pdfs_to_collection('./Lab-04-Data/', collection)

### MAIN APP ###

# Show title and descr
st.title('Lab 4: Chatbot using RAG')
st.write("This is a question answering chatbot. -- Add more to descr later")

LLM = st.sidebar.selectbox("Which Model?",
                            ("ChatGPT"))

if LLM == "ChatGPT":
    model_choice = "gpt-4o-mini"

# VECTOR DATABASE COLLECTION VARIABLE
if "Lab4_VectorDB" not in st.session_state:
    st.session_state.Lab4_VectorDB = collection

# Create GPT Client
if 'client' not in st.session_state:
    api_key = st.secrets["IST488"]
    st.session_state.client = OpenAI(api_key=api_key)

if "messages" not in st.session_state: 
    st.session_state["messages"] = [
        {
            "role": "system",
            "content": f"""
            You are a question-answering assistant.
            [CHANGE LINES BELOW] 
            You will answer questions that pertain to {URL1_content} and/or {URL2_content}. Do not forget the contents of these websites.
            End first response: 'Do you want more information?' 
            If they want more information continue asking if they want more until they say no, then summarize the conversation. 
            Keep your answers simple enough such that a ten year old can understand them.
            If you reach 3 user-assistant exchanges, summarize the conversation so far, then replace the conversation history with that summary reponse.
            [CHANGE LIVES ABOVE]
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