"""
Deepseek LLM Client - OpenAI-compatible API integration
"""
import json
import time
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from openai import APIError, APITimeoutError
from httpx import TimeoutException as HTTPTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging
import os

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
        # #region agent log
        with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"llm.client.py:__init__:entry","message":"DeepseekClient __init__ called","data":{"env_request_timeout":os.getenv("REQUEST_TIMEOUT"),"agentconfig_request_timeout":AgentConfig.request_timeout},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"A"})+'\n')
        # #endregion
        self.api_key = api_key or AgentConfig.deepseek_api_key
        self.base_url = base_url or AgentConfig.deepseek_base_url
        self.model = model or AgentConfig.deepseek_model
        self.max_retries = AgentConfig.max_retries
        self.timeout = AgentConfig.request_timeout
        
        # #region agent log
        with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"llm.client.py:__init__:timeout_assigned","message":"Timeout value assigned to self.timeout","data":{"self_timeout":self.timeout,"timeout_type":type(self.timeout).__name__},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"B"})+'\n')
        # #endregion
        
        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY not set. LLM calls will fail.")
        
        # OpenAI client expects timeout as tuple (connect_timeout, read_timeout) or float
        # Use tuple format: (connect_timeout, read_timeout) for better control
        # Set read timeout higher for LLM requests that may take longer
        timeout_config: Tuple[float, float] = (10.0, float(self.timeout))
        
        # #region agent log
        with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"llm.client.py:__init__:timeout_config","message":"Timeout config tuple created","data":{"timeout_config":timeout_config,"connect_timeout":timeout_config[0],"read_timeout":timeout_config[1]},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"C"})+'\n')
        # #endregion
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=timeout_config,
            max_retries=0  # Disable OpenAI's built-in retries, we handle retries ourselves
        )
        
        # #region agent log
        try:
            client_timeout = getattr(self.client._client, 'timeout', None)
            timeout_str = str(client_timeout) if client_timeout else 'not_found'
        except:
            timeout_str = 'error_accessing'
        with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"llm.client.py:__init__:client_created","message":"OpenAI client created with timeout config","data":{"client_timeout_str":timeout_str,"client_has_timeout":hasattr(self.client._client, 'timeout')},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"D"})+'\n')
        # #endregion
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # Only retry on API errors, not on timeouts (timeouts suggest the request is too complex or server is overloaded)
        retry=retry_if_exception_type((APIError,)),
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
            start_time = time.time()
            
            # #region agent log
            with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"location":"llm.client.py:chat_completion:before_request","message":"About to make LLM API call","data":{"self_timeout":self.timeout,"model":self.model,"max_tokens":max_tokens,"has_tools":tools is not None,"tools_count":len(tools) if tools else 0},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"E"})+'\n')
            # #endregion
            
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = tool_choice
                # Log tool schemas for debugging
                for tool in tools:
                    if tool.get("function", {}).get("name") == "get_campaign_metrics":
                        logger.debug(f"get_campaign_metrics schema: {json.dumps(tool.get('function', {}).get('parameters', {}), indent=2)}")
            
            response = self.client.chat.completions.create(**kwargs)
            
            elapsed_time = time.time() - start_time
            
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
            
            logger.info(f"LLM API call successful. Tokens: {result['usage']['total_tokens']}, Time: {elapsed_time:.2f}s")
            return result
            
        except (APITimeoutError, HTTPTimeout, TimeoutError) as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            
            # #region agent log
            with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
                f.write(json.dumps({"location":"llm.client.py:chat_completion:timeout_error","message":"LLM API call timed out","data":{"elapsed_time":elapsed_time,"self_timeout":self.timeout,"error_type":type(e).__name__,"error_message":str(e)},"timestamp":int(time.time()*1000),"sessionId":"debug-session","runId":"run1","hypothesisId":"F"})+'\n')
            # #endregion
            
            logger.error(f"LLM API call timed out after {elapsed_time:.2f}s (timeout: {self.timeout}s). "
                        f"This may indicate the request is too complex or the API is overloaded. Error: {str(e)}")
            raise
        except Exception as e:
            elapsed_time = time.time() - start_time if 'start_time' in locals() else 0
            logger.error(f"LLM API call failed after {elapsed_time:.2f}s: {str(e)}")
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

