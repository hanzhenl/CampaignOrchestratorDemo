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
                        "description": "The ID of the campaign to get metrics for"
                    }
                },
                "required": ["campaign_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": "Create a chart visualization for data extracted during research. Use this to visualize time-series data, performance metrics, or any numeric data arrays.",
            "parameters": {
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "description": "Array of data points. Each point should have 'x' (label) and 'y' (value) properties, or be a number array with corresponding labels array.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "x": {"type": ["string", "number"]},
                                "y": {"type": "number"}
                            }
                        }
                    },
                    "title": {
                        "type": "string",
                        "description": "Chart title"
                    },
                    "xLabel": {
                        "type": "string",
                        "description": "X-axis label"
                    },
                    "yLabel": {
                        "type": "string",
                        "description": "Y-axis label"
                    },
                    "chartType": {
                        "type": "string",
                        "description": "Chart type (default: 'line')",
                        "enum": ["line"],
                        "default": "line"
                    },
                    "labels": {
                        "type": "array",
                        "description": "Optional array of labels for X-axis (if data is just numbers)",
                        "items": {"type": "string"}
                    },
                    "datasetLabel": {
                        "type": "string",
                        "description": "Label for the dataset (default: 'Data')",
                        "default": "Data"
                    }
                },
                "required": ["data", "title", "xLabel", "yLabel"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "show_recommendations",
            "description": "Display recommended campaigns or audience segments as cards in the experience panel. Use this when you identify campaigns or segments that should be recommended to the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "items": {
                        "type": "array",
                        "description": "Array of recommendation objects. Each item should be a campaign or segment object with at least 'id' and 'name' fields.",
                        "items": {
                            "type": "object"
                        }
                    },
                    "type": {
                        "type": "string",
                        "description": "Type of recommendations",
                        "enum": ["campaign", "segment", "mixed"],
                        "default": "mixed"
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional title for the recommendations section (e.g., 'Recommended Campaigns', 'Suggested Segments')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional description explaining why these items are recommended"
                    }
                },
                "required": ["items"]
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
        
        elif tool_name == "create_chart":
            data = arguments.get("data", [])
            title = arguments.get("title", "Chart")
            x_label = arguments.get("xLabel", "X Axis")
            y_label = arguments.get("yLabel", "Y Axis")
            chart_type = arguments.get("chartType", "line")
            labels = arguments.get("labels")
            dataset_label = arguments.get("datasetLabel", "Data")
            
            # Process data into chart format
            chart_labels = []
            chart_data = []
            
            if labels:
                # If labels provided separately, use them
                chart_labels = labels
                # Extract y values from data
                if data and isinstance(data[0], dict):
                    chart_data = [point.get("y", 0) for point in data]
                elif data and isinstance(data[0], (int, float)):
                    chart_data = data
            else:
                # Extract from data points
                for point in data:
                    if isinstance(point, dict):
                        chart_labels.append(str(point.get("x", "")))
                        chart_data.append(float(point.get("y", 0)))
                    elif isinstance(point, (int, float)):
                        chart_labels.append(str(len(chart_labels) + 1))
                        chart_data.append(float(point))
            
            if not chart_data:
                return {
                    "success": False,
                    "error": "No valid data points found"
                }
            
            # Format for frontend Chart.js
            chart_config = {
                "title": title,
                "xLabel": x_label,
                "yLabel": y_label,
                "type": chart_type,
                "data": {
                    "labels": chart_labels,
                    "datasets": [{
                        "label": dataset_label,
                        "data": chart_data,
                        "borderColor": "rgb(59, 130, 246)",
                        "backgroundColor": "rgba(59, 130, 246, 0.1)"
                    }]
                }
            }
            
            return {
                "success": True,
                "chart": chart_config
            }
        
        elif tool_name == "show_recommendations":
            items = arguments.get("items", [])
            rec_type = arguments.get("type", "mixed")
            title = arguments.get("title")
            description = arguments.get("description")
            
            if not items or not isinstance(items, list):
                return {
                    "success": False,
                    "error": "items array is required and must be a list"
                }
            
            # Format recommendations for frontend
            recommendations_config = {
                "uiComponent": "recommendations",
                "type": rec_type,
                "items": items,
                "title": title or f"Recommended {rec_type.title()}s" if rec_type != "mixed" else "Recommendations",
                "description": description
            }
            
            return {
                "success": True,
                "recommendations": recommendations_config
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

