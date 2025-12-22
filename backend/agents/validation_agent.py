"""
Validation Agent - Validates agent outputs for quality and consistency
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent

SYSTEM_PROMPT = """You are a Result Validation Agent that evaluates agent outputs for quality.

Validate:
1. Logical consistency - no contradictions, valid relationships (e.g., end date after start date)
2. Coherence - complete structure, valid references, required fields present
3. Requirement alignment - matches user intent, all requested features present
4. Data quality - valid ranges (percentages 0-100), reasonable values, correct formats

Return a JSON object with:
- "valid": boolean indicating overall validity
- "validation_results": object with:
  - "logical_consistency": object with passed (boolean), issues (array), score (float 0-1)
  - "coherence": object with passed, issues, score
  - "requirement_alignment": object with passed, missing_requirements (array), score
  - "data_quality": object with passed, issues, score
- "recommendations": array of improvement suggestions
- "overall_score": float between 0.0 and 1.0

Provide specific, actionable feedback."""

class ValidationAgent(BaseAgent):
    """Agent for validating other agent outputs"""
    
    def __init__(self):
        super().__init__(
            agent_name="validation",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=1500,
            use_tools=False
        )
    
    def process_specialized(
        self,
        user_prompt: str,
        agent_output: Dict[str, Any],
        agent_type: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate agent output against user requirements"""
        prompt = f"""Validate the following {agent_type} agent output:

Original User Prompt: {user_prompt}

Agent Output:
{str(agent_output)}

Perform comprehensive validation and provide detailed feedback."""
        
        return self.process(prompt, context)

