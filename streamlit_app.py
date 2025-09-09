"""
Streamlit frontend for the Agentic Query System.
Provides an interactive chat-like UI for asking questions about camera feeds and encoder/decoder parameters.
"""
import streamlit as st
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime


# Page configuration
st.set_page_config(
    page_title="Agentic Query System",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# App title and description
st.title("🎥 Agentic Query System — Chat Interface")
st.markdown("Ask natural language questions about camera feeds, encoder settings, and decoder parameters. Follow up with additional questions for deeper insights!")


def create_new_session():
    """Create a new chat session."""
    try:
        response = requests.post(f"{st.session_state.api_base_url}/session/new", timeout=5)
        if response.status_code == 200:
            return response.json()["session_id"]
    except requests.RequestException:
        pass
    return None


def clear_chat_history():
    """Clear the current chat session."""
    st.session_state.messages = []
    if st.session_state.session_id:
        try:
            requests.delete(f"{st.session_state.api_base_url}/session/{st.session_state.session_id}/clear", timeout=5)
        except requests.RequestException:
            pass
    st.session_state.session_id = None


def process_user_message(user_input: str):
    """Process a user message and get AI response."""
    try:
        # Create session if needed
        if not st.session_state.session_id:
            st.session_state.session_id = create_new_session()
        
        # Make API request
        payload = {
            "question": user_input,
            "session_id": st.session_state.session_id
        }
        
        response = requests.post(
            f"{st.session_state.api_base_url}/ask",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Add assistant response to chat
            assistant_message = {
                "role": "assistant",
                "content": result["answer"],
                "tool_calls": result.get("tool_calls", [])
            }
            st.session_state.messages.append(assistant_message)
            
            # Update session ID if it changed
            st.session_state.session_id = result.get("session_id", st.session_state.session_id)
            
            return True
            
        else:
            error_detail = response.json().get("detail", "Unknown error") if response.headers.get("content-type") == "application/json" else response.text
            st.error(f"❌ API Error ({response.status_code}): {error_detail}")
            return False
            
    except requests.RequestException as e:
        st.error(f"❌ Connection Error: {str(e)}")
        st.info("Make sure the FastAPI backend is running on the configured URL.")
        return False
    except json.JSONDecodeError:
        st.error("❌ Invalid response format from API")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return False

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Settings")
    
    # API URL configuration
    if "api_base_url" not in st.session_state:
        st.session_state.api_base_url = "http://localhost:8000"
    
    api_base_url = st.text_input(
        "API Base URL",
        value=st.session_state.api_base_url,
        help="Base URL for the FastAPI backend"
    )
    st.session_state.api_base_url = api_base_url
    
    # Chat controls
    st.markdown("---")
    st.header("💬 Chat Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat", use_container_width=True):
            clear_chat_history()
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            clear_chat_history()
            st.rerun()
    
    # Session info
    if st.session_state.session_id:
        st.info(f"🔗 Session: {st.session_state.session_id[:8]}...")
    else:
        st.info("🔗 No active session")
    
    # Health check
    if st.button("🔍 Check API Health"):
        try:
            response = requests.get(f"{api_base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                st.success("✅ API is healthy!")
                st.json(health_data)
            else:
                st.error(f"❌ API health check failed: {response.status_code}")
        except requests.RequestException as e:
            st.error(f"❌ Cannot connect to API: {str(e)}")
    
    st.markdown("---")
    
    # Example queries
    st.header("💡 Example Queries")
    st.markdown("Click any example to use it:")
    
    example_queries = [
        "How many camera feeds are in the Pacific theater?",
        "Which cameras have the highest resolution?", 
        "What are the encoder parameters?",
        "Show me all H265 encoded feeds",
        "Which feeds have the lowest latency?",
        "What decoder settings are configured?",
        "List all feeds in Europe with encryption enabled",
        "Which camera models are used in CONUS?",
        "Show feeds sorted by frame rate",
        "What's the bitrate configuration for encoding?"
    ]
    
    for i, query in enumerate(example_queries):
        if st.button(f"📝 {query[:40]}...", key=f"example_{i}"):
            # Create session if needed
            if not st.session_state.session_id:
                st.session_state.session_id = create_new_session()
            
            # Add to chat and trigger processing
            st.session_state.messages.append({"role": "user", "content": query})
            with st.spinner("🤔 Processing your question..."):
                process_user_message(query)
            st.rerun()

# Display chat history
st.header("💬 Conversation")

# Chat container
chat_container = st.container()

with chat_container:
    # Display all messages
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(message["content"])
                
                # Show tool calls if available
                if "tool_calls" in message and message["tool_calls"]:
                    with st.expander("🔧 Tool Calls Used", expanded=False):
                        for j, tool_call in enumerate(message["tool_calls"], 1):
                            st.markdown(f"**Tool {j}: `{tool_call['name']}`**")
                            
                            if tool_call["arguments"]:
                                st.markdown("*Arguments:*")
                                st.json(tool_call["arguments"])
                            
                            if "result" in tool_call:
                                st.markdown("*Result:*")
                                if "error" in tool_call["result"]:
                                    st.error(f"Error: {tool_call['result']['error']}")
                                elif "data" in tool_call["result"]:
                                    st.markdown(f"Found {tool_call['result']['count']} results:")
                                    if tool_call["result"]["data"]:
                                        st.dataframe(tool_call["result"]["data"])
                                else:
                                    st.json(tool_call["result"])
                            
                            if j < len(message["tool_calls"]):
                                st.markdown("---")


# Chat input
user_input = st.chat_input("Ask a question about camera feeds, encoder, or decoder parameters...")

if user_input:
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Process the message
    with st.spinner("🤔 Processing your question..."):
        process_user_message(user_input)
    
    # Rerun to update the chat display
    st.rerun()

# Main interface (keep for backwards compatibility)
st.markdown("---")
st.header("📝 Direct Query")
st.markdown("*You can also use the form below instead of the chat interface above*")

col1, col2 = st.columns([3, 1])

with col1:
    # Query input
    user_question = st.text_area(
        "Ask your question:",
        height=100,
        placeholder="e.g., 'Which camera feeds are in the Pacific region with high resolution?'",
        key="direct_query_input"
    )

with col2:
    st.markdown("<br>", unsafe_allow_html=True)  # Add some spacing
    ask_button = st.button("🚀 Ask", type="primary", use_container_width=True, key="direct_ask")

# Handle direct query submission
if ask_button and user_question.strip():
    # Add to chat history and process
    st.session_state.messages.append({"role": "user", "content": user_question.strip()})
    
    with st.spinner("🤔 Processing your question..."):
        success = process_user_message(user_question.strip())
        if success:
            st.success("✅ Question answered successfully! Check the conversation above.")
            # Clear the direct input
            st.session_state.direct_query_input = ""
            st.rerun()

elif ask_button:
    st.warning("⚠️ Please enter a question before clicking Ask.")

# Footer
st.markdown("---")
st.markdown(
    "**💻 Technical Details:** This application uses OpenAI GPT with function calling to query camera feed data, "
    "encoder parameters, and decoder parameters. All responses are based solely on the loaded data."
)

# Instructions
with st.expander("📖 How to Use", expanded=False):
    st.markdown("""
    ### Getting Started
    1. **Start the Backend**: Make sure the FastAPI backend is running (`python main.py`)
    2. **Set API URL**: Configure the correct API URL in the sidebar (default: http://localhost:8000)
    3. **Check Health**: Use the health check button to verify the API is working
    4. **Ask Questions**: Type natural language questions about:
       - Camera feeds (locations, codecs, resolution, etc.)
       - Encoder parameters and settings
       - Decoder configuration
    
    ### Example Questions
    - "How many feeds are in each theater?"
    - "Which cameras have 4K resolution?"
    - "Show me the encoder bitrate settings"
    - "List all encrypted feeds in the Pacific region"
    - "What's the decoder buffer configuration?"
    
    ### Features
    - 🎯 **Smart Responses**: GPT only answers based on actual data, no hallucinations
    - 🔍 **Tool Tracing**: See exactly which data sources were queried
    - 📊 **Data Display**: Results shown in tables when appropriate
    - 💡 **Examples**: Quick-start with pre-made queries
    """)

# Clear the query input from session state after using it
if "query_input" in st.session_state and st.session_state.query_input:
    if user_question == st.session_state.query_input:
        del st.session_state.query_input
