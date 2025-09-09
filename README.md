# Agentic Query System - Baseline Implementation

This is the baseline implementation of the Agentic Query System for the CanyonCode AI Intern Technical Assessment.

## Architecture

The application consists of two main components:

### FastAPI Backend (`main.py`)
- Loads camera feeds data and encoder/decoder parameters
- Provides `/ask` endpoint for natural language queries
- Uses OpenAI GPT with function calling to process questions
- Returns structured responses with tool call traces

### Streamlit Frontend (`streamlit_app.py`)
- **Chat Interface**: ChatGPT-like conversation interface with message history
- **Session Management**: Maintains conversation context for follow-up questions
- **Interactive UI**: Both chat interface and direct query options
- **Tool Call Visualization**: Shows which data sources were queried
- **Chat Controls**: New chat, clear history, session management
- **Example Queries**: Quick-start with pre-made questions
- **Real-time Updates**: Live conversation with immediate responses

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key (get one at: https://platform.openai.com/api-keys)

### Quick Setup
1. **Verify Setup** (recommended first step)
   ```bash
   python check_setup.py
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **🔑 Set OpenAI API Key** (REQUIRED - SECURITY CRITICAL)
   
   **⚠️ SECURITY WARNING: Never commit your actual API key to version control!**
   
   **Option A: Environment Variable**
   ```bash
   # Windows
   set OPENAI_API_KEY=your_api_key_here
   
   # Linux/Mac
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   **Option B: .env File** (recommended for development)
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and replace 'your_openai_api_key_here' with your actual API key
   # The .env file is automatically ignored by git for security
   ```
   
   **🛡️ Security Best Practices:**
   - Never commit `.env` files to version control
   - Use environment variables in production
   - Rotate API keys regularly
   - Monitor API usage for suspicious activity

4. **Start the Application**
   
   **Easy way:**
   ```bash
   python start.py
   ```
   
   **Manual way:**
   ```bash
   # Terminal 1: Start Backend
   python main.py
   
   # Terminal 2: Start Frontend  
   streamlit run streamlit_app.py
   ```

### Access the Application
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:8501

## Usage

### Example Conversations
- **Initial**: "How many camera feeds are in the Pacific theater?"
- **Follow-up**: "What about their resolution?"
- **Follow-up**: "Which one has the highest resolution?"
- **Context Switch**: "Now tell me about the encoder parameters"
- **Clarification**: "What does the bitrate setting control?"

### Available Tools
The system provides three tools to the GPT assistant:

1. **feeds_search** - Query camera feeds data with filters, sorting, and column selection
2. **encoder_get_params** - Retrieve encoder configuration parameters
3. **decoder_get_params** - Retrieve decoder configuration parameters

## File Structure

```
├── main.py              # FastAPI backend
├── streamlit_app.py     # Streamlit frontend
├── data_loader.py       # Data loading and validation
├── tools_runtime.py     # Tool implementations
├── openai_tools.py      # OpenAI integration
├── requirements.txt     # Dependencies
├── Data/               # Data files
│   ├── Table_feeds_v2.csv
│   ├── encoder_params.json
│   ├── encoder_schema.json
│   ├── decoder_params.json
│   └── decoder_schema.json
└── README.md           # This file
```

## API Endpoints

### GET /
Health check endpoint

### GET /health
Detailed health check with data loading status

### POST /session/new
Create a new chat session
- **Output**: `{"session_id": "uuid"}`

### GET /session/{session_id}/history
Get conversation history for a session
- **Output**: `{"session_id": "uuid", "messages": [...]}`

### DELETE /session/{session_id}/clear
Clear conversation history for a session

### POST /ask
Submit a natural language question
- **Input**: `{"question": "your question here", "session_id": "optional_uuid"}`
- **Output**: `{"answer": "...", "tool_calls": [...], "session_id": "uuid"}`

## Key Features

- **💬 ChatGPT-like Interface**: Conversation history with follow-up questions
- **🧠 Session Memory**: Maintains context across multiple questions
- **🎯 Data-Only Responses**: GPT answers only based on tool results, no hallucinations
- **🔍 Tool Tracing**: Complete visibility into which tools were called and their results
- **🏗️ Modular Design**: Clean separation between data loading, tools, and API layers
- **📱 Dual Interface**: Both chat and direct query modes
- **✅ Validation**: JSON schema validation for encoder/decoder parameters

## Technical Details

- **Backend**: FastAPI with async endpoints and CORS support
- **Frontend**: Streamlit with real-time API integration
- **AI Model**: OpenAI GPT-4 Turbo with function calling
- **Data**: Pandas DataFrames for efficient querying
- **Validation**: JSON Schema for parameter validation

## Development Notes

- The system enforces that GPT only uses the provided tools
- All responses are stateless - no chat history is maintained
- Tool calls are logged for full traceability
- Error handling for API failures and data loading issues
