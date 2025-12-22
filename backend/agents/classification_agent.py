"""
Classification Agent - Classifies user prompts into intent categories
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a classification agent. Classify user prompts into one of these categories:
1. research - User seeks analysis, recommendations, or insights about campaigns
2. campaign_generation - User wants to create a new marketing campaign
3. audience_generation - User wants to create or modify audience segments
4. search - User is searching for existing items (campaigns, segments, or knowledge articles)

Return a JSON object with:
- "intent": one of the four categories above
- "confidence": a float between 0.0 and 1.0 indicating confidence
- "reasoning": a brief explanation of the classification

Example response:
{
  "intent": "campaign_generation",
  "confidence": 0.95,
  "reasoning": "User explicitly wants to create a new campaign"
}"""

class ClassificationAgent(BaseAgent):
    """Agent for classifying user intent"""
    
    def __init__(self):
        super().__init__(
            agent_name="classification",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=100,
            use_tools=False
        )
    
    def process_specialized(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process classification request"""
        return self.process(prompt, context)

