"""
OpenAI tools module for the Agentic Query System.
Contains system prompt and tool schemas for GPT function calling.
"""
from typing import List, Dict, Any

# System prompt for the GPT assistant
SYSTEM_PROMPT = """You are a cautious data assistant for a camera feed monitoring system. You MUST answer questions only using the provided tool results.

Your available tools are:
1. feeds_search - Query and filter camera feeds data
2. encoder_get_params - Get encoder configuration parameters  
3. decoder_get_params - Get decoder configuration parameters

Rules:
- If asked about camera feeds, feed data, or anything related to cameras/video streams, use feeds_search
- If asked about encoder settings, encoding parameters, or video encoding, use encoder_get_params
- If asked about decoder settings, decoding parameters, or video decoding, use decoder_get_params
- You MUST base your answers ONLY on tool results
- If a question is ambiguous or unclear, ask a clarifying question instead of making assumptions
- Do not hallucinate or provide information not returned by the tools
- When using feeds_search, you can filter by columns like THEATER, CODEC, ENCR, MODL_TAG, CIV_OK, etc.

Theater codes:
- CONUS: Continental United States
- EUR: Europe  
- ME: Middle East
- PAC: Pacific
- AFR: Africa

Example feed search filters:
- Theater: {"THEATER": "PAC"} for Pacific feeds
- High resolution: {"RES_W": {"min": 1920}} for 1920+ width
- Specific codec: {"CODEC": "H265"} for H265 encoded feeds
- Multiple theaters: {"THEATER": ["PAC", "EUR"]} for Pacific or Europe

Always provide clear, factual answers based on the data returned by your tools."""

# Tool schemas for OpenAI function calling
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "feeds_search",
            "description": "Search and filter camera feeds data with various criteria",
            "parameters": {
                "type": "object",
                "properties": {
                    "filters": {
                        "type": "object",
                        "description": "Dictionary of column->value filters. Supports exact match, list of values, or range/comparison filters",
                        "additionalProperties": True
                    },
                    "columns": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of columns to return. Available: FEED_ID, THEATER, FRRATE, RES_W, RES_H, CODEC, ENCR, LAT_MS, MODL_TAG, CIV_OK"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "minimum": 1
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Column name to sort results by"
                    },
                    "desc": {
                        "type": "boolean",
                        "description": "Whether to sort in descending order (default: false for ascending)"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function", 
        "function": {
            "name": "encoder_get_params",
            "description": "Get video encoder configuration parameters",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "decoder_get_params", 
            "description": "Get video decoder configuration parameters",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        }
    }
]


def create_messages(user_question: str) -> List[Dict[str, str]]:
    """
    Create the messages array for OpenAI API call.
    
    Args:
        user_question: The user's natural language question
        
    Returns:
        List of message dictionaries for OpenAI API
    """
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_question}
    ]


def get_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get the tool schemas for OpenAI function calling.
    
    Returns:
        List of tool schema dictionaries
    """
    return TOOL_SCHEMAS
