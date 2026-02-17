import requests
import tomllib
import streamlit as st
from openai import OpenAI
import json

weather_key = st.secrets["weather"]["weather_key"]

def get_current_weather(location, api_key, units='imperial'):
    url = (
        f'https://api.openweathermap.org/data/2.5/weather'
        f'?q={location}&appid={api_key}&units={units}'
    )
    response = requests.get(url)
    if response.status_code == 401:
        raise Exception('Authentication failed: Invalid API key (401 Unauthorized)')
    if response.status_code == 404:
        error_message = response.json().get('message')
        raise Exception(f'404 error: {error_message}')
    data = response.json()
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    temp_min = data['main']['temp_min']
    temp_max = data['main']['temp_max']
    humidity = data['main']['humidity']
    conditions = data["weather"][0]["description"]

    
    return {'location':location,
            'temperature': round(temp,2),
            'feels_like': round(feels_like, 2),
            'temp_min': round(temp_min, 2),
            'temp_max': round(temp_max, 2),
            'humidity': round(humidity, 2),
            'conditions': conditions
            }

# print(get_current_weather("Syracuse, NY, US", weather_key))
st.title("My Lab 5 What to Wear bot")

# Create GPT Client
if 'client' not in st.session_state:
    api_key = st.secrets["lab_key"]["IST488"]
    st.session_state.client = OpenAI(api_key=api_key)

# Memory
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "What city would you like weather information about?"
        }        
    ]

# Display History
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        chat_msg = st.chat_message(msg["role"])
        chat_msg.write(msg["content"])

# Tooling
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City and state, e.g. Syracuse, NY"
                    }
                },
                "required": []
            }
        }
    }
]

# User input
user_input = st.chat_input("Enter city, state, and country name here")

if user_input and user_input.strip():
    
    st.session_state.messages.append({"role":"user","content":user_input})
    with st.chat_message("user"):
        st.write(user_input)

    client = st.session_state.client

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=st.session_state.messages,
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    # get_current_weather call
    if msg.tool_calls:

        tool_call = msg.tool_calls[0]
        args = json.loads(tool_call.function.arguments or "{}")
        location = args.get("location", "Syracuse, NY, US")

        weather = get_current_weather(location, weather_key)

        weather_text = (
            f"Weather in {weather['location']}:\n"
            f"Temperature: {weather['temperature']}°F\n"
            f"Feels like: {weather['feels_like']}°F\n"
            f"Humidity: {weather['humidity']}%\n"
            f"Conditions: {weather['conditions']}"
        )

        # add tool call and result to messages
        st.session_state.messages.append(msg)
        st.session_state.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": weather_text
        })

        # final response
        final = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a helpful weather assistant. "
                "When given weather data, you must: provide suggestions on appropriate clothes to wear today and give suggestions for outdoor activities that are appropriate to the weather"
            )
        }
    ] + st.session_state.messages
)


        reply = final.choices[0].message.content

    else:
        reply = msg.content


    # reply
    st.session_state.messages.append({"role":"assistant","content":reply})

    with st.chat_message("assistant"):
        st.write(reply)
