"""
Tools runtime module for the Agentic Query System.
Implements the three tools available to the GPT assistant.
"""
import pandas as pd
from typing import Dict, Any, List, Optional, Union
from data_loader import data_loader


def feeds_search(
    filters: Optional[Dict[str, Any]] = None,
    columns: Optional[List[str]] = None,
    top_k: Optional[int] = None,
    sort_by: Optional[str] = None,
    desc: bool = False
) -> Dict[str, Any]:
    """
    Search and filter camera feeds data.
    
    Args:
        filters: Dictionary of column->value filters to apply
        columns: List of columns to return (all if None)
        top_k: Maximum number of results to return
        sort_by: Column name to sort by
        desc: Whether to sort in descending order
        
    Returns:
        Dictionary with 'data' (list of records) and 'count' (total matches)
    """
    try:
        # Get the feeds dataframe
        df = data_loader.get_feeds_dataframe().copy()
        
        # Apply filters
        if filters:
            for column, value in filters.items():
                if column not in df.columns:
                    return {
                        "error": f"Unknown column: {column}",
                        "available_columns": list(df.columns)
                    }
                
                # Handle different filter types
                if isinstance(value, dict):
                    # Range or comparison filters
                    if "min" in value:
                        df = df[df[column] >= value["min"]]
                    if "max" in value:
                        df = df[df[column] <= value["max"]]
                    if "gt" in value:
                        df = df[df[column] > value["gt"]]
                    if "lt" in value:
                        df = df[df[column] < value["lt"]]
                elif isinstance(value, list):
                    # Multiple values (IN filter)
                    df = df[df[column].isin(value)]
                else:
                    # Exact match
                    if pd.api.types.is_string_dtype(df[column]):
                        # Case-insensitive string matching
                        df = df[df[column].str.contains(str(value), case=False, na=False)]
                    else:
                        df = df[df[column] == value]
        
        # Sort if requested
        if sort_by:
            if sort_by not in df.columns:
                return {
                    "error": f"Unknown sort column: {sort_by}",
                    "available_columns": list(df.columns)
                }
            df = df.sort_values(by=sort_by, ascending=not desc)
        
        # Apply top_k limit
        if top_k:
            df = df.head(top_k)
        
        # Select columns
        if columns:
            invalid_columns = [col for col in columns if col not in df.columns]
            if invalid_columns:
                return {
                    "error": f"Unknown columns: {invalid_columns}",
                    "available_columns": list(df.columns)
                }
            df = df[columns]
        
        # Convert to records
        records = df.to_dict('records')
        
        return {
            "data": records,
            "count": len(records),
            "total_feeds": len(data_loader.get_feeds_dataframe())
        }
        
    except Exception as e:
        return {"error": f"Error in feeds_search: {str(e)}"}


def encoder_get_params() -> Dict[str, Any]:
    """
    Get encoder parameters.
    
    Returns:
        Dictionary containing all encoder parameters
    """
    try:
        params = data_loader.get_encoder_params()
        return {
            "encoder_params": params,
            "description": "Video encoder configuration parameters"
        }
    except Exception as e:
        return {"error": f"Error getting encoder params: {str(e)}"}


def decoder_get_params() -> Dict[str, Any]:
    """
    Get decoder parameters.
    
    Returns:
        Dictionary containing all decoder parameters
    """
    try:
        params = data_loader.get_decoder_params()
        return {
            "decoder_params": params,
            "description": "Video decoder configuration parameters"
        }
    except Exception as e:
        return {"error": f"Error getting decoder params: {str(e)}"}


# Tool function registry for easy access
TOOL_FUNCTIONS = {
    "feeds_search": feeds_search,
    "encoder_get_params": encoder_get_params,
    "decoder_get_params": decoder_get_params
}


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Execute a tool by name with the given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        **kwargs: Arguments to pass to the tool
        
    Returns:
        Tool execution result
    """
    if tool_name not in TOOL_FUNCTIONS:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        return TOOL_FUNCTIONS[tool_name](**kwargs)
    except Exception as e:
        return {"error": f"Tool execution error: {str(e)}"}
