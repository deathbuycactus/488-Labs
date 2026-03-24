import streamlit as st
from openai import OpenAI
from pydantic import BaseModel

# ---------------------------
# Setup
# ---------------------------
st.set_page_config(page_title="Lab 6 - OpenAI Agent", layout="wide")

# Initialize OpenAI client
api_key = st.secrets['lab_key']['IST488']
client = OpenAI(api_key=api_key)

# Session state for conversation chaining
if "last_response_id" not in st.session_state:
    st.session_state.last_response_id = None

# ---------------------------
# Sidebar خيارات
# ---------------------------
st.sidebar.title("Settings")

use_structured = st.sidebar.checkbox("Return structured summary")
use_streaming = st.sidebar.checkbox("Stream response")
st.sidebar.caption("⚡ Web search is enabled for up-to-date answers.")

# ---------------------------
# Structured Output Model
# ---------------------------
class ResearchSummary(BaseModel):
    main_answer: str
    key_facts: list[str]
    source_hint: str

# ---------------------------
# UI
# ---------------------------
st.title("🔎 OpenAI Research Agent")

user_question = st.text_input("Ask a question:")

# ---------------------------
# Function: Make API Call
# ---------------------------
def get_response(prompt, previous_id=None):
    if use_structured:
        response = client.responses.parse(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=prompt,
            tools=[{"type": "web_search_preview"}],
            previous_response_id=previous_id,
            text_format=ResearchSummary,
        )
        return response

    elif use_streaming:
        stream = client.responses.stream(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=prompt,
            tools=[{"type": "web_search_preview"}],
            previous_response_id=previous_id,
        )
        full_text = ""
        placeholder = st.empty()

        for event in stream:
            if event.type == "response.output_text.delta":
                full_text += event.delta
                placeholder.markdown(full_text)

        final_response = stream.get_final_response()
        return final_response

    else:
        response = client.responses.create(
            model="gpt-4o",
            instructions="You are a helpful research assistant. Cite your sources.",
            input=prompt,
            tools=[{"type": "web_search_preview"}],
            previous_response_id=previous_id,
        )
        return response

# ---------------------------
# First Question (Part A + C)
# ---------------------------
if user_question:
    response = get_response(user_question)

    if use_structured:
        data = response.output_parsed
        st.subheader("Answer")
        st.write(data.main_answer)

        st.subheader("Key Facts")
        for fact in data.key_facts:
            st.write(f"- {fact}")

        st.caption(data.source_hint)

    else:
        st.subheader("Answer")
        st.write(response.output_text)

    # Save response ID for chaining
    st.session_state.last_response_id = response.id

# ---------------------------
# Follow-up (Part B)
# ---------------------------
if st.session_state.last_response_id:
    follow_up = st.text_input("Ask a follow-up question:")

    if follow_up:
        response = get_response(
            follow_up,
            previous_id=st.session_state.last_response_id
        )

        if use_structured:
            data = response.output_parsed
            st.subheader("Follow-up Answer")
            st.write(data.main_answer)

            st.subheader("Key Facts")
            for fact in data.key_facts:
                st.write(f"- {fact}")

            st.caption(data.source_hint)

        else:
            st.subheader("Follow-up Answer")
            st.write(response.output_text)

        # Update chain
        st.session_state.last_response_id = response.id