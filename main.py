"""
FastAPI backend for the Agentic Query System.
Provides the /ask endpoint that processes natural language questions using OpenAI GPT with function calling.
"""
import json
import os
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai
from openai import OpenAI

# Load environment variables if .env file exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

from data_loader import data_loader
from tools_runtime import execute_tool
from openai_tools import create_messages, get_tool_schemas
from session_manager import session_manager, ChatSession


# Initialize FastAPI app
app = FastAPI(
    title="Agentic Query System API",
    description="Backend API for querying camera feeds and encoder/decoder parameters",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class NewSessionResponse(BaseModel):
    session_id: str

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]

class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]

class QueryResponse(BaseModel):
    answer: str
    tool_calls: List[ToolCall]
    session_id: str

# Initialize OpenAI client
client = None

def get_openai_client():
    """Get OpenAI client, initialized lazily."""
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="OPENAI_API_KEY environment variable not set"
            )
        # Initialize OpenAI client with just the API key
        client = OpenAI(api_key=api_key)
    return client


@app.on_event("startup")
async def startup_event():
    """Load all data on application startup."""
    try:
        data_loader.load_all_data()
        print("Data loaded successfully!")
        print(f"- Feeds: {len(data_loader.get_feeds_dataframe())} records")
        print(f"- Encoder params: {len(data_loader.get_encoder_params())} parameters")
        print(f"- Decoder params: {len(data_loader.get_decoder_params())} parameters")
    except Exception as e:
        print(f"Error loading data: {e}")
        raise


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Agentic Query System API is running",
        "endpoints": {
            "ask": "POST /ask - Submit a natural language question",
            "new_session": "POST /session/new - Create a new chat session",
            "get_history": "GET /session/{session_id}/history - Get chat history",
            "clear_session": "DELETE /session/{session_id}/clear - Clear session history",
            "health": "GET / - Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Detailed health check with data status."""
    try:
        feeds_count = len(data_loader.get_feeds_dataframe())
        encoder_loaded = data_loader.get_encoder_params() is not None
        decoder_loaded = data_loader.get_decoder_params() is not None
        
        return {
            "status": "healthy",
            "data": {
                "feeds_loaded": feeds_count,
                "encoder_loaded": encoder_loaded,
                "decoder_loaded": decoder_loaded
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/session/new", response_model=NewSessionResponse)
async def create_new_session():
    """Create a new chat session."""
    session_id = session_manager.create_session()
    return NewSessionResponse(session_id=session_id)


@app.get("/session/{session_id}/history", response_model=ChatHistoryResponse)
async def get_session_history(session_id: str):
    """Get the chat history for a session."""
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Convert messages to display format
    messages = []
    for msg in session.messages:
        message_dict = {
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat()
        }
        if msg.tool_calls:
            message_dict["tool_calls"] = msg.tool_calls
        messages.append(message_dict)
    
    return ChatHistoryResponse(session_id=session_id, messages=messages)


@app.delete("/session/{session_id}/clear")
async def clear_session_history(session_id: str):
    """Clear the chat history for a session."""
    success = session_manager.clear_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session history cleared successfully"}


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Process a natural language question using OpenAI GPT with function calling.
    Supports conversation history for follow-up questions.
    
    Args:
        request: QueryRequest containing the user's question and optional session_id
        
    Returns:
        QueryResponse with the assistant's answer, tool call traces, and session_id
    """
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session_id = session_manager.create_session()
        
        # Verify session exists
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Add user message to session
        session_manager.add_message(session_id, "user", request.question)
        
        # Get OpenAI client
        openai_client = get_openai_client()
        
        # Get conversation history including system prompt
        messages = session_manager.get_conversation_history(session_id, include_system=True)
        tools = get_tool_schemas()
        
        # Track tool calls for response
        tool_calls_made = []
        
        # Make the initial OpenAI API call
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Use GPT-4o-mini for better stability and cost efficiency
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1  # Low temperature for consistent, factual responses
        )
        
        # Check if the model wants to call functions
        assistant_message = response.choices[0].message
        
        # Handle function calls
        if assistant_message.tool_calls:
            # Convert tool calls for session storage
            tool_calls_for_session = [
                {
                    "id": tool_call.id,
                    "type": tool_call.type,
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                }
                for tool_call in assistant_message.tool_calls
            ]
            
            # Add assistant message to session
            session_manager.add_message(
                session_id, 
                "assistant", 
                assistant_message.content or "",
                tool_calls=tool_calls_for_session
            )
            
            # Add assistant message to conversation
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": tool_calls_for_session
            })
            
            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the tool
                tool_result = execute_tool(function_name, **function_args)
                
                # Record the tool call
                tool_calls_made.append(ToolCall(
                    name=function_name,
                    arguments=function_args,
                    result=tool_result
                ))
                
                # Add tool result to conversation
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_result)
                })
                
                # Add tool result to session
                session_manager.add_message(
                    session_id,
                    "tool",
                    json.dumps(tool_result),
                    tool_call_id=tool_call.id
                )
            
            # Get final response from assistant
            final_response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.1
            )
            
            final_answer = final_response.choices[0].message.content
        else:
            # No function calls made
            final_answer = assistant_message.content
        
        # Add final assistant response to session
        if assistant_message.tool_calls:
            # Final response after tool calls
            session_manager.add_message(session_id, "assistant", final_answer)
        # If no tool calls, the assistant message was already added above
        
        return QueryResponse(
            answer=final_answer,
            tool_calls=tool_calls_made,
            session_id=session_id
        )
        
    except openai.OpenAIError as e:
        raise HTTPException(
            status_code=500,
            detail=f"OpenAI API error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
