"""
Base Agent class with LLM integration and common functionality
"""
import logging
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

import sys
import os
# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from llm.client import DeepseekClient
from llm.tools import get_tools_for_agent, execute_tool
from utils.response_parser import parse_json_response, extract_tool_calls
from config import AgentConfig

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Abstract base class for all agents"""
    
    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        use_tools: bool = False
    ):
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.temperature = temperature or AgentConfig.get_temperature(agent_name)
        self.max_tokens = max_tokens or AgentConfig.get_max_tokens(agent_name)
        self.use_tools = use_tools
        
        # Initialize LLM client
        self.llm_client = DeepseekClient()
        
        # Get tools if needed
        self.tools = get_tools_for_agent(agent_name) if use_tools else []
    
    def process(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process user prompt and return agent response
        
        Args:
            prompt: User prompt
            context: Optional context dict (conversation history, previous results, etc.)
        
        Returns:
            Agent response dict
        """
        try:
            # Build messages
            messages = self._build_messages(prompt, context)
            
            # Call LLM
            response = self._call_llm(messages)
            
            # Handle tool calls if present
            tool_calls = extract_tool_calls(response)
            if tool_calls and self.use_tools:
                return self._handle_tool_calls(response, tool_calls, messages, context)
            
            # Parse and return response
            return self._parse_response(response, context)
        
        except Exception as e:
            logger.error(f"Error in {self.agent_name} agent: {str(e)}")
            return self._handle_error(e, prompt, context)
    
    def _build_messages(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, str]]:
        """Build message list for LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add knowledge articles if available
        if context and context.get("knowledge_articles"):
            knowledge_text = self._format_knowledge_articles(context["knowledge_articles"])
            if knowledge_text:
                # Add knowledge articles as a system message or append to system prompt
                messages.append({
                    "role": "system",
                    "content": f"Relevant Knowledge Articles:\n\n{knowledge_text}\n\nUse this knowledge to inform your responses."
                })
        
        # Add context if available
        if context and context.get("conversation_history"):
            for msg in context["conversation_history"]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        return messages
    
    def _format_knowledge_articles(self, knowledge_articles: List[Dict[str, Any]]) -> str:
        """Format knowledge articles for inclusion in messages"""
        if not knowledge_articles:
            return ""
        
        formatted = []
        for article in knowledge_articles:
            title = article.get("title", "Untitled")
            content = article.get("content", "")
            formatted.append(f"Knowledge Article: {title}\n{content}")
        
        return "\n\n".join(formatted)
    
    def _call_llm(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None
    ) -> Dict[str, Any]:
        """Make LLM API call"""
        # Use provided tools/tool_choice, or fall back to defaults
        if tools is None:
            tools = self.tools if self.use_tools else None
        if tool_choice is None:
            tool_choice = "auto" if self.use_tools else "none"
        
        return self.llm_client.chat_completion(
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tools=tools,
            tool_choice=tool_choice
        )
    
    def _handle_tool_calls(
        self,
        response: Dict[str, Any],
        tool_calls: List[Dict],
        messages: List[Dict[str, str]],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle tool calls and continue conversation"""
        # Execute tool calls
        tool_results = []
        for tool_call in tool_calls:
            function_name = tool_call["function"]["name"]
            arguments = parse_json_response(tool_call["function"]["arguments"])
            
            logger.info(f"Executing tool: {function_name} with args: {arguments}")
            result = execute_tool(function_name, arguments)
            tool_results.append({
                "tool_call_id": tool_call["id"],
                "name": function_name,
                "result": result
            })
        
        # Add tool results to messages and continue
        messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": tc["type"],
                    "function": tc["function"]
                }
                for tc in tool_calls
            ]
        })
        
        # Add tool results
        for tr in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tr["tool_call_id"],
                "content": str(tr["result"])    
            })
        
        # Add explicit reminder to return JSON format after tool calls
        # This ensures the LLM returns structured JSON even after seeing tool results
        messages.append({
            "role": "user",
            "content": "Based on the tool results above, please provide your analysis in JSON format as specified in the system prompt. Return only valid JSON, no conversational text."
        })
        
        # Continue LLM call with tool results
        # Disable tool calling on final response to force JSON output
        final_response = self._call_llm(messages, tools=None, tool_choice="none")
        
        # Check if LLM made another tool call instead of returning content
        tool_calls_after = extract_tool_calls(final_response)
        if tool_calls_after and self.use_tools:
            # Recursively handle additional tool calls
            return self._handle_tool_calls(final_response, tool_calls_after, messages, context)
        
        return self._parse_response(final_response, context)
    
    def _parse_response(
        self,
        response: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse LLM response"""
        content = self.llm_client.extract_content(response)
        
        # Try to parse as JSON
        parsed = parse_json_response(content)
        
        # If parsing failed, return raw content
        if not parsed or "parse_error" in parsed:
            return {
                "content": content,
                "raw": True
            }
        
        return parsed
    
    def _handle_error(
        self,
        error: Exception,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle errors gracefully"""
        return {
            "error": True,
            "error_type": type(error).__name__,
            "message": str(error),
            "agent": self.agent_name
        }
    
    @abstractmethod
    def process_specialized(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Agent-specific processing logic
        Override in subclasses for specialized behavior
        """
        pass

