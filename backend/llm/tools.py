"""
Tool definitions and execution for agent tool calling
"""
from typing import Dict, Any, List
import logging
import sys
import os
# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from utils.data_access import (
    get_campaigns,
    get_segments,
    get_campaign_metrics
)

logger = logging.getLogger(__name__)

# Tool definitions for LLM function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_campaigns",
            "description": "Retrieve historical campaigns with optional filters. Use this to analyze past campaign performance and configurations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "Filter campaigns by goal (e.g., 'purchase', 'activation', 'engagement')"
                    },
                    "status": {
                        "type": "string",
                        "description": "Filter by status: 'active', 'completed', or 'draft'",
                        "enum": ["active", "completed", "draft"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of campaigns to return (default: 10)",
                        "default": 10
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_segments",
            "description": "Retrieve audience segments with optional filters. Use this to find suitable audience segments for campaigns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Filter segments by name (fuzzy match)"
                    },
                    "min_conversion_rate": {
                        "type": "number",
                        "description": "Minimum conversion rate threshold"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of segments to return (default: 10)",
                        "default": 10
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_campaign_metrics",
            "description": "Get performance metrics for a specific campaign. Use this to analyze campaign effectiveness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_id": {
                        "type": "string",
                        "description": "The ID of the campaign to get metrics for",
                        "required": True
                    }
                },
                "required": ["campaign_id"]
            }
        }
    }
]

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool call
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments dict
    
    Returns:
        Tool execution result
    """
    try:
        if tool_name == "get_campaigns":
            result = get_campaigns(arguments)
            return {
                "success": True,
                "data": result,
                "count": len(result)
            }
        
        elif tool_name == "get_segments":
            result = get_segments(arguments)
            return {
                "success": True,
                "data": result,
                "count": len(result)
            }
        
        elif tool_name == "get_campaign_metrics":
            campaign_id = arguments.get("campaign_id")
            if not campaign_id:
                return {
                    "success": False,
                    "error": "campaign_id is required"
                }
            result = get_campaign_metrics(campaign_id)
            return {
                "success": True,
                "data": result
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }
    
    except Exception as e:
        logger.error(f"Tool execution error for {tool_name}: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_tools_for_agent(agent_name: str) -> List[Dict]:
    """
    Get tool definitions for a specific agent
    
    Args:
        agent_name: Name of the agent
    
    Returns:
        List of tool definitions
    """
    # Research agent needs all tools
    if agent_name == "research":
        return TOOLS
    
    # Other agents don't need tools by default
    return []

