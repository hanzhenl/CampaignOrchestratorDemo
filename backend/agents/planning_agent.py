"""
Planning Agent - Creates multi-step execution plans based on classification
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a planning agent that orchestrates marketing campaign workflows.
Create concise, multi-step plans that route user requests to specialist agents.

For campaign_generation intent:
1. Step 1: Route to Research Agent for campaign analysis
2. Step 2: Route to Campaign Agent with research results

For audience_generation intent:
- Route directly to Audience Agent

For research intent:
- Route directly to Research Agent

For search intent:
- Call search function directly (not an agent)

Return a JSON object with:
- "plan": array of step objects, each with:
  - "step": step number (integer)
  - "agent": agent name ("research", "campaign", "audience", "journey", or "search")
  - "action": description of what this step does
  - "input": object with input data for this step
- "estimated_steps": total number of steps

Example response:
{
  "plan": [
    {
      "step": 1,
      "agent": "research",
      "action": "Analyze campaign requirements and historical data",
      "input": {"prompt": "user prompt here"}
    },
    {
      "step": 2,
      "agent": "campaign",
      "action": "Generate campaign configuration",
      "input": {"prompt": "user prompt", "research_results": "from step 1"}
    }
  ],
  "estimated_steps": 2
}"""

class PlanningAgent(BaseAgent):
    """Agent for creating execution plans"""
    
    def __init__(self):
        super().__init__(
            agent_name="planning",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.5,
            max_tokens=500,
            use_tools=False
        )
    
    def process_specialized(
        self,
        prompt: str,
        classification: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create execution plan based on classification"""
        # Include classification in the prompt
        enhanced_prompt = f"""User intent: {classification.get('intent')}
Confidence: {classification.get('confidence')}
Reasoning: {classification.get('reasoning')}

User prompt: {prompt}

Create an execution plan for this request."""
        
        return self.process(enhanced_prompt, context)

