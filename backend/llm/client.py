"""
Deepseek LLM Client - OpenAI-compatible API integration
"""
import json
import time
from typing import List, Dict, Any, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging

from config import AgentConfig

logger = logging.getLogger(__name__)

class DeepseekClient:
    """OpenAI-compatible client for Deepseek API"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.api_key = api_key or AgentConfig.deepseek_api_key
        self.base_url = base_url or AgentConfig.deepseek_base_url
        self.model = model or AgentConfig.deepseek_model
        self.max_retries = AgentConfig.max_retries
        self.timeout = AgentConfig.request_timeout
        
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not set. LLM calls will fail.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        reraise=True
    )
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tools: Optional[List[Dict]] = None,
        tool_choice: str = "auto"
    ) -> Dict[str, Any]:
        """
        Make chat completion request to Deepseek API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            tools: List of tool definitions for function calling
            tool_choice: Tool choice strategy ('auto', 'none', or function name)
        
        Returns:
            Response dict with choices, usage, etc.
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice
            
            response = self.client.chat.completions.create(**kwargs)
            
            # Convert response to dict format
            result = {
                "id": response.id,
                "object": response.object,
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content,
                            "tool_calls": [
                                {
                                    "id": tc.id,
                                    "type": tc.type,
                                    "function": {
                                        "name": tc.function.name,
                                        "arguments": tc.function.arguments
                                    }
                                }
                                for tc in (choice.message.tool_calls or [])
                            ]
                        },
                        "finish_reason": choice.finish_reason
                    }
                    for choice in response.choices
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            logger.info(f"LLM API call successful. Tokens: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            raise
    
    def extract_tool_calls(self, response: Dict[str, Any]) -> List[Dict]:
        """Extract tool calls from LLM response"""
        tool_calls = []
        if response.get("choices"):
            message = response["choices"][0].get("message", {})
            tool_calls = message.get("tool_calls", [])
        return tool_calls
    
    def extract_content(self, response: Dict[str, Any]) -> str:
        """Extract text content from LLM response"""
        if response.get("choices"):
            message = response["choices"][0].get("message", {})
            return message.get("content", "")
        return ""

