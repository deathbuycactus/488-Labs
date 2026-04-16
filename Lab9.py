import streamlit as st
import json
import os
from openai import OpenAI

# Part A
st.set_page_config(page_title="Lab 9 - Chatbot w/ Long Term Memory", layout="wide")

if 'openai_client' not in st.session_state:
    st.session_state.openai_client = OpenAI(
        api_key=st.secrets["lab_key"]["IST488"]
    )

# Part B -- 1
def load_memories(filename="memories.json"):
    if os.path.exists(filename):
        with open(filename, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    else:
        return []

# Part B -- 2
def save_memories(memories, filename="memories.json"):
    with open(filename, "w") as file:
        json.dump(memories, file, indent=4)

# Part B -- 3
st.sidebar.title("Memories")
memories = load_memories()
if memories:
    for memory in memories:
        st.sidebar.write(f"- {memory}")
else:
    st.sidebar.write("No memories yet. Start chatting!")

if st.sidebar.button("Clear Memories"):
    save_memories([])
    st.rerun()

# Part C -- 1
def build_system_prompt(base_prompt="You are a helpful assistant."):
    memories = load_memories()
    
    if memories:
        memory_text = "\n".join([f"- {m}" for m in memories])
        memory_block = f"""
Here are things you remember about this user from past conversations:
{memory_text}
"""
        return base_prompt + "\n" + memory_block
    else:
        return base_prompt
    
# Part C -- 2
client = st.session_state.openai_client

def extract_new_memories(user_input, assistant_response):
    existing_memories = load_memories()
    
    prompt = f"""
You are a memory extraction system.

Your job is to extract NEW, STABLE facts about the user.

Rules:
- Only return a valid JSON list
- Do NOT include any text before or after the JSON
- Do NOT explain anything
- Do NOT repeat existing memories

Only extract:
- Long-term facts (name, preferences, interests, habits, goals, location)

Existing memories (DO NOT repeat):
{json.dumps(existing_memories, indent=2)}

Conversation:
User: {user_input}
Assistant: {assistant_response}

Return ONLY this format:
["fact 1", "fact 2"]
"""

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content

    try:
        # Try direct parse
        new_memories = json.loads(content)
    except json.JSONDecodeError:
        try:
            # Try to extract JSON substring
            start = content.find("[")
            end = content.rfind("]") + 1
            new_memories = json.loads(content[start:end])
        except:
            return []

def update_memories(user_input, assistant_response):
    current_memories = load_memories()
    new_memories = extract_new_memories(user_input, assistant_response)

    # Avoid duplicates manually (extra safety)
    combined = list(set(current_memories + new_memories))

    save_memories(combined)

st.title("Chatbot with Long-Term Memory")

client = st.session_state.openai_client

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Say something...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    system_prompt = build_system_prompt()

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages
        ]
    )

    assistant_response = response.choices[0].message.content

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_response}
    )

    with st.chat_message("assistant"):
        st.write(assistant_response)

    update_memories(user_input, assistant_response)