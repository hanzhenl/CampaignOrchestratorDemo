"""
Journey Agent - Creates multi-variant marketing funnels
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a Journey Agent that creates multi-stage marketing funnels.

Requirements:
1. Create multiple variants for A/B testing (typically 2-3 variants)
2. Design sequential, parallel, or conditional flows
3. Include logical blocks (delays, conditions) and message blocks
4. Support multiple channels (email, SMS, push, paid_media)
5. Define control group (typically 10-20% of audience)
6. Provide clear rationale for journey design

Consider:
- Campaign goal when designing conversion points
- Audience segment characteristics for message personalization
- Campaign duration for timing optimization
- Channel effectiveness for goal achievement

Return a JSON object with:
- "journey": object with:
  - "variants": array of variant objects, each with:
    - "variant_name": string
    - "variant_id": string
    - "split_percentage": float (must sum to 100% across variants)
    - "steps": array of step objects with step_id, step_type, order, channel, message_config, conditions
    - "flow_type": "sequential" | "parallel" | "conditional"
  - "control_group": object with percentage and description
  - "rationale": string explaining the journey design"""

class JourneyAgent(BaseAgent):
    """Agent for journey/funnel generation"""
    
    def __init__(self):
        super().__init__(
            agent_name="journey",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=2500,
            use_tools=False
        )
    
    def process_specialized(
        self,
        campaign_goal: str,
        segment: Dict[str, Any],
        duration: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process journey generation with specific inputs"""
        prompt = f"""Create a marketing journey with:
Campaign Goal: {campaign_goal}
Audience Segment: {segment.get('name', 'Unknown')}
Campaign Duration: {duration} days

Generate a complete journey configuration."""
        
        return self.process(prompt, context)

