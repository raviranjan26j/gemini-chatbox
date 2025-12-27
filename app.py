import streamlit as st
import google.generativeai as genai
import os

# --- Configuration ---
# 1. Get the API Key from the environment variable (set in Step 1)
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("GEMINI_API_KEY environment variable not set. Please set it as described in Step 1.")
    # Exit or prevent further code execution if API Key is missing
    st.stop() 
else:
    # 2. Configure the Gemini client
    try:
        # The client automatically picks up the API key from the environment variable
        client = genai.Client()
        MODEL = 'gemini-2.5-flash' 
    except Exception as e:
        st.error(f"Error configuring Gemini client: {e}")
        st.stop()

# Streamlit Page Setup
st.set_page_config(page_title="Ravi Chatbox", layout="wide")
st.title("Welcome Ravi Chatbox 💬")

# =========================================================================
# 2. Managing Chat History (Streamlit st.session_state)
# =========================================================================

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am Ravi. How can I help you today!."}
    ]

# Display all existing messages from the history
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize the Gemini Chat Session
# We must prepare the history in the format required by the Gemini API:
# {"role": "user"/"model", "parts": [{"text": "..."}]}
gemini_history = []
for message in st.session_state["messages"]:
    role = "user" if message["role"] == "user" else "model"
    # Skip the initial assistant message in history sent to the API to avoid errors/redundancy
    if message["content"] != "Hello! I am Ravi. How can I help you today!.":
        gemini_history.append({"role": role, "parts": [{"text": message["content"]}]})

# Create the chat session with the accumulated history
chat = client.chats.create(model=MODEL, history=gemini_history)


# =========================================================================
# 3. Handling User Input and Getting Response
# =========================================================================

# Accept user input
# The := (walrus) operator assigns the input to 'prompt' and checks if it's non-empty
if prompt := st.chat_input("How can I help you today?"):
    
    # 1. Add user message to Streamlit session history
    st.session_state["messages"].append({"role": "user", "content": prompt})
    
    # 2. Display the new user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Get the response from the Gemini API
    try:
        # Use the chat session to send the message, which automatically includes history
        response = chat.send_message(prompt)
        
        # 4. Extract and display the assistant response
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # 5. Add the assistant response to Streamlit session history
        st.session_state["messages"].append({"role": "assistant", "content": response.text})
        
    except Exception as e:
        error_message = f"An error occurred while calling the Gemini API: {e}"
        st.error(error_message)
        st.session_state["messages"].append({"role": "assistant", "content": error_message})