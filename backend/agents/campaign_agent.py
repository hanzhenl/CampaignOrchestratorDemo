"""
Campaign Agent - Generates complete campaign configurations through multi-step orchestration
"""
from typing import Dict, Any, Optional
import sys
import os
# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from agents.base_agent import BaseAgent
from agents.research_agent import ResearchAgent
from agents.audience_agent import AudienceAgent
from agents.journey_agent import JourneyAgent

SYSTEM_PROMPT = """You are a Campaign Agent that generates structured campaign configurations.

Process:
1. Use research results (if provided) to inform campaign design
2. Extract campaign information from user prompt and research
3. If audience segment is missing, you will call Audience Agent
4. If journey is missing, you will call Journey Agent
5. Construct complete campaign structure

Return a JSON object with:
- "campaign": object with:
  - "name": string
  - "description": string
  - "goals": array of goal strings
  - "startDate": string (ISO format)
  - "endDate": string (ISO format)
  - "segmentIds": array of segment IDs
  - "channels": array of channel names
  - "estimatedAudienceSize": integer
  - "progress": float (0.0-1.0)
  - "userFlowConfig": object with flowType, steps, variants
  - "variants": array of variant objects
  - "creatives": array of creative objects
  - "controlGroup": object
- "missing_information": array of missing fields
- "recommendations": string with recommendations

Output must be structured JSON ready for UI population."""

class CampaignAgent(BaseAgent):
    """Agent for campaign generation with orchestration"""
    
    def __init__(self):
        super().__init__(
            agent_name="campaign",
            system_prompt=SYSTEM_PROMPT,
            temperature=0.7,
            max_tokens=3000,
            use_tools=False
        )
        # Initialize sub-agents for orchestration
        self.research_agent = ResearchAgent()
        self.audience_agent = AudienceAgent()
        self.journey_agent = JourneyAgent()
    
    def process_specialized(
        self,
        prompt: str,
        research_results: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process campaign generation with optional research results
        
        Multi-step process:
        1. Use research results if provided, otherwise call Research Agent
        2. Extract campaign information
        3. Call Audience Agent if needed
        4. Call Journey Agent if needed
        5. Construct final campaign
        """
        # Step 1: Get research if not provided
        if not research_results:
            research_results = self.research_agent.process(prompt, context)
        
        # Step 2: Extract campaign information with research context
        enhanced_prompt = f"""User Request: {prompt}

Research Analysis:
{str(research_results)}

Extract campaign information and generate complete campaign configuration."""
        
        # Get initial campaign structure
        campaign_result = self.process(enhanced_prompt, context)
        
        # Step 3: Generate audience if missing
        if not campaign_result.get("campaign", {}).get("segmentIds"):
            # Extract goal from campaign or prompt
            goals = campaign_result.get("campaign", {}).get("goals", [])
            goal_str = goals[0] if goals else prompt
            
            audience_result = self.audience_agent.process(
                f"Create an audience segment for campaign goal: {goal_str}",
                context
            )
            
            if not audience_result.get("error"):
                # Add segment to campaign (mock segment ID for now)
                if "campaign" not in campaign_result:
                    campaign_result["campaign"] = {}
                campaign_result["campaign"]["segmentIds"] = ["generated_segment_1"]
                campaign_result["audience_segment"] = audience_result.get("segment")
        
        # Step 4: Generate journey if missing
        if not campaign_result.get("campaign", {}).get("userFlowConfig"):
            campaign = campaign_result.get("campaign", {})
            goals = campaign.get("goals", [])
            goal_str = goals[0] if goals else "engagement"
            
            # Mock segment for journey generation
            segment = {
                "name": "Target Audience",
                "id": campaign.get("segmentIds", [""])[0] if campaign.get("segmentIds") else ""
            }
            
            # Calculate duration from dates or default
            duration = 30  # default
            if campaign.get("startDate") and campaign.get("endDate"):
                from datetime import datetime
                try:
                    start = datetime.fromisoformat(campaign["startDate"].replace("Z", "+00:00"))
                    end = datetime.fromisoformat(campaign["endDate"].replace("Z", "+00:00"))
                    duration = (end - start).days
                except:
                    pass
            
            journey_result = self.journey_agent.process_specialized(
                goal_str,
                segment,
                duration,
                context
            )
            
            if journey_result.get("journey"):
                campaign_result["campaign"]["userFlowConfig"] = journey_result["journey"]
        
        return campaign_result

