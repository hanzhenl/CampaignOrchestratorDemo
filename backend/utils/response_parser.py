"""
Response parser utilities for JSON parsing and validation
"""
import json
import re
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

def parse_json_response(content: str) -> Dict[str, Any]:
    """
    Parse JSON response from LLM, handling markdown code blocks
    
    Args:
        content: LLM response content (may contain markdown)
    
    Returns:
        Parsed JSON dict
    """
    if not content:
        return {}
    
    # Remove markdown code blocks if present
    content = content.strip()
    
    # Try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
    if json_match:
        content = json_match.group(1)
    
    # Try to find JSON object in content
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        content = json_match.group(0)
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {e}. Content: {content[:200]}")
        # Try to return a basic structure
        return {"raw_content": content, "parse_error": str(e)}

def extract_tool_calls(response: Dict[str, Any]) -> List[Dict]:
    """
    Extract tool calls from LLM response
    
    Args:
        response: LLM API response dict
    
    Returns:
        List of tool call dicts
    """
    tool_calls = []
    if response.get("choices"):
        message = response["choices"][0].get("message", {})
        tool_calls = message.get("tool_calls", [])
    return tool_calls

def validate_agent_output(output: Dict[str, Any], schema: Optional[Dict] = None) -> bool:
    """
    Validate agent output against expected schema
    
    Args:
        output: Agent output dict
        schema: Expected schema (optional, basic validation if not provided)
    
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(output, dict):
        return False
    
    if schema:
        # Check required fields
        required = schema.get("required", [])
        for field in required:
            if field not in output:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Check field types
        properties = schema.get("properties", {})
        for field, value in output.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type == "array" and not isinstance(value, list):
                    return False
                elif expected_type == "object" and not isinstance(value, dict):
                    return False
                elif expected_type == "string" and not isinstance(value, str):
                    return False
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    return False
    
    return True

