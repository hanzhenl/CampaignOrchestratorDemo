"""
Research Agent - Provides evidence-based campaign recommendations using tool calling
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a Research Agent specializing in marketing campaign analysis.
Your role is to:
1. Analyze historical campaign and audience data using tool calls
2. Provide evidence-based recommendations
3. Explain your rationale with specific data points
4. Suggest optimal campaign configurations

Always ground your recommendations in historical evidence.
Use tool calling to access campaign and audience databases.
Provide detailed rationale for each recommendation.

Return a JSON object with:
- "analysis": object containing:
  - "optimal_goal": string or array of campaign goals
  - "recommended_schedule": object with startDate, endDate, duration, rationale
  - "recommended_channels": array of channel names
  - "channel_rationale": object with rationale for each channel
  - "journey_variants": array of variant suggestions
  - "audience_recommendations": object with existing_segments and new_segment_suggestions
- "evidence": object with:
  - "historical_campaigns": array of relevant campaigns
  - "historical_performance": object with performance data
- "rationale": string explaining the analysis"""

class ResearchAgent(BaseAgent):
    """Agent for research and analysis with tool calling"""
    
    def __init__(self):
        super().__init__(
            agent_name="research",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=2000,
            use_tools=True
        )
    
    def process_specialized(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process research request with tool calling"""
        return self.process(prompt, context)

