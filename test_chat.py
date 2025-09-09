"""
Test script to demonstrate the new chat functionality.
Shows how the application maintains conversation history.
"""
import requests
import json


def test_chat_conversation():
    """Test a multi-turn conversation."""
    base_url = "http://localhost:8000"
    
    print("🎥 Testing Agentic Query System - Chat Functionality")
    print("=" * 60)
    
    # Create a new session
    print("1. Creating new chat session...")
    response = requests.post(f"{base_url}/session/new")
    session_id = response.json()["session_id"]
    print(f"   ✅ Session created: {session_id}")
    
    # First question
    print("\n2. First question: How many feeds are in the Pacific theater?")
    response = requests.post(f"{base_url}/ask", json={
        "question": "How many feeds are in the Pacific theater?",
        "session_id": session_id
    })
    result = response.json()
    print(f"   🤖 Answer: {result['answer']}")
    print(f"   🔧 Tools used: {[tc['name'] for tc in result['tool_calls']]}")
    
    # Follow-up question
    print("\n3. Follow-up question: What about their resolution?")
    response = requests.post(f"{base_url}/ask", json={
        "question": "What about their resolution?",
        "session_id": session_id
    })
    result = response.json()
    print(f"   🤖 Answer: {result['answer']}")
    print(f"   🔧 Tools used: {[tc['name'] for tc in result['tool_calls']]}")
    
    # Another follow-up
    print("\n4. Another follow-up: Which one has the highest resolution?")
    response = requests.post(f"{base_url}/ask", json={
        "question": "Which one has the highest resolution?",
        "session_id": session_id
    })
    result = response.json()
    print(f"   🤖 Answer: {result['answer']}")
    print(f"   🔧 Tools used: {[tc['name'] for tc in result['tool_calls']]}")
    
    # Get session history
    print(f"\n5. Getting conversation history...")
    response = requests.get(f"{base_url}/session/{session_id}/history")
    history = response.json()
    print(f"   📝 Total messages in conversation: {len(history['messages'])}")
    
    print("\n🎉 Chat functionality test completed successfully!")
    print(f"💡 Try the web interface at: http://localhost:8501")


if __name__ == "__main__":
    try:
        test_chat_conversation()
    except requests.RequestException as e:
        print(f"❌ Error: {e}")
        print("Make sure the FastAPI backend is running on http://localhost:8000")
