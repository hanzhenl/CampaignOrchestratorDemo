"""
Audience Agent - Generates audience segmentation based on campaign goals
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are an Audience Agent that creates marketing audience segments.

Requirements:
1. Analyze the campaign goal to determine target audience
2. Create segment filters based on demographics, behaviors, and attributes
3. Provide estimated segment size
4. Explain your segmentation rationale

If the campaign goal is missing or unclear, return an error requesting clarification.

Return a JSON object with:
- "segment": object with:
  - "name": segment name
  - "description": segment description
  - "filters": object with demographics, behaviors, custom_attributes
  - "estimated_size": integer
  - "rationale": string explaining the segmentation
- "recommendations": object with alternative_segments and segmentation_strategy

If goal is missing, return:
{
  "error": true,
  "message": "Campaign goal is required to generate audience segment",
  "requested_info": ["campaign_goal", "target_demographics"]
}"""

class AudienceAgent(BaseAgent):
    """Agent for audience segment generation"""
    
    def __init__(self):
        super().__init__(
            agent_name="audience",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.6,
            max_tokens=1500,
            use_tools=False
        )
    
    def process_specialized(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process audience generation request"""
        return self.process(prompt, context)

