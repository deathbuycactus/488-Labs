import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("MY Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "The answer will be in 100 words, 2 connecting paragraphs, or in 5 bullet points."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
# Removed text input for LLM key: openai_api_key = st.text_input("OpenAI API Key", type="password")
#if not openai_api_key:
#    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
#else:

#st.write("lab_key", st.secrets["lab_key"]["IST488"])

lab_key = st.secrets["lab_key"]["IST488"]

# Create an OpenAI client.
client = OpenAI(api_key=lab_key)

if st.checkbox("Advanced Model"):
    st.write("Advanced Model: ON")
    checkbox = True
else:
    st.write("Advanced Model: OFF")
    checkbox = False
    
# Let the user upload a file via `st.file_uploader`.
uploaded_file = st.file_uploader(
    "Upload a document (.txt or .md)", type=("txt", "md")
)

add_selectbox = st.sidebar.selectbox(
    "How would you like the document summarized?:",
    ("In 100 words", "In 2 connecting paragraphs", "In 5 bullet points")
)

if uploaded_file and add_selectbox:

    # Process the uploaded file and question.
    document = uploaded_file.read().decode()
    messages = [
        {
            "role": "user",
            "content": f"Here's a document: {document} \n\n---\n\n {add_selectbox}",
        }
    ]
    if checkbox == True:
    # Generate an answer using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-5-nano",
            messages=messages,
            stream=True,
        )
    else:
        stream = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            stream=True,
        )

    # Stream the response to the app using `st.write_stream`.
    st.write_stream(stream)