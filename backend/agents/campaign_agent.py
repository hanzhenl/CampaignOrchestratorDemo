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

SYSTEM_PROMPT = """You are a Campaign Agent that generates structured campaign configurations with analysis.

Process:
1. Use research results (if provided) to inform campaign design
2. Extract campaign information from user prompt and research
3. Generate audience segment inline if missing (include in segmentIds and create segment object)
4. Generate journey/userFlowConfig inline if missing (include complete userFlowConfig with variants, steps, flowType)
5. Construct complete campaign structure with rationale

Return a JSON object with:
- "rationale": string - Human-readable analysis explaining the campaign design, recommendations, and key decisions. This will be displayed in the dialog panel.
- "campaign": object with:
  - "name": string
  - "description": string
  - "goals": array of goal strings
  - "startDate": string (ISO format)
  - "endDate": string (ISO format)
  - "segmentIds": array of segment IDs (generate inline if missing)
  - "channels": array of channel names
  - "estimatedAudienceSize": integer
  - "progress": float (0.0-1.0)
  - "userFlowConfig": object with flowType, steps, variants (generate inline if missing)
  - "variants": array of variant objects
  - "creatives": array of creative objects, each with:
    - "channel": string (e.g., "WhatsApp", "Google Ads", "Meta Ads")
    - "photos": array of photo URLs or placeholder image URLs
    - "copy": string (ad copy text)
  - "controlGroup": object
- "analysis": object (optional) with detailed analysis fields
- "missing_information": array of missing fields
- "recommendations": string with recommendations

IMPORTANT: Generate audience segments and journeys inline as part of the campaign structure. Only use separate agent calls if the inline generation fails or is too complex.

Output must be structured JSON ready for UI population. The rationale field is critical for user understanding."""

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
        
        Consolidated process:
        1. Use research results if provided (don't call research agent again - reuse from orchestrator)
        2. Generate complete campaign with rationale, audience, and journey in a single LLM call
        3. Fallback to sub-agents only if inline generation fails
        """
        # Build enhanced prompt with research context
        if research_results:
            # Format research results for prompt
            research_text = self._format_research_for_prompt(research_results)
            enhanced_prompt = f"""User Request: {prompt}

Research Analysis:
{research_text}

Based on the user request and research analysis above, generate a complete campaign configuration. Include:
1. A detailed rationale explaining your campaign design decisions and recommendations
2. A complete campaign structure with all fields populated
3. Audience segment information (generate inline if not specified)
4. User journey/flow configuration (generate inline if not specified)

Generate everything in a single response with both analysis text and structured data."""
        else:
            enhanced_prompt = f"""User Request: {prompt}

Generate a complete campaign configuration. Include:
1. A detailed rationale explaining your campaign design decisions and recommendations
2. A complete campaign structure with all fields populated
3. Audience segment information (generate inline if not specified)
4. User journey/flow configuration (generate inline if not specified)

Generate everything in a single response with both analysis text and structured data."""
        
        # Single LLM call to generate everything
        campaign_result = self.process(enhanced_prompt, context)
        
        # Ensure rationale exists for dialog panel
        if not campaign_result.get("rationale"):
            # Generate a default rationale if missing
            campaign = campaign_result.get("campaign", {})
            if campaign:
                goals = campaign.get("goals", [])
                name = campaign.get("name", "Campaign")
                rationale = f"Generated campaign '{name}'"
                if goals:
                    rationale += f" with goals: {', '.join(goals)}"
                campaign_result["rationale"] = rationale
        
        # Fallback: Only call sub-agents if critical fields are still missing after inline generation
        campaign = campaign_result.get("campaign", {})
        
        # Fallback for audience if still missing
        if not campaign.get("segmentIds") and not campaign_result.get("audience_segment"):
            goals = campaign.get("goals", [])
            goal_str = goals[0] if goals else prompt
            
            try:
                audience_result = self.audience_agent.process(
                    f"Create an audience segment for campaign goal: {goal_str}",
                    context
                )
                
                if not audience_result.get("error"):
                    if "campaign" not in campaign_result:
                        campaign_result["campaign"] = {}
                    campaign_result["campaign"]["segmentIds"] = ["generated_segment_1"]
                    campaign_result["audience_segment"] = audience_result.get("segment")
            except Exception as e:
                # If sub-agent fails, continue with what we have
                pass
        
        # Fallback for journey if still missing
        if not campaign.get("userFlowConfig"):
            goals = campaign.get("goals", [])
            goal_str = goals[0] if goals else "engagement"
            
            segment = {
                "name": "Target Audience",
                "id": campaign.get("segmentIds", [""])[0] if campaign.get("segmentIds") else ""
            }
            
            duration = 30  # default
            if campaign.get("startDate") and campaign.get("endDate"):
                from datetime import datetime
                try:
                    start = datetime.fromisoformat(campaign["startDate"].replace("Z", "+00:00"))
                    end = datetime.fromisoformat(campaign["endDate"].replace("Z", "+00:00"))
                    duration = (end - start).days
                except:
                    pass
            
            try:
                journey_result = self.journey_agent.process_specialized(
                    goal_str,
                    segment,
                    duration,
                    context
                )
                
                if journey_result.get("journey"):
                    if "campaign" not in campaign_result:
                        campaign_result["campaign"] = {}
                    campaign_result["campaign"]["userFlowConfig"] = journey_result["journey"]
            except Exception as e:
                # If sub-agent fails, continue with what we have
                pass
        
        return campaign_result
    
    def _format_research_for_prompt(self, research_results: Dict[str, Any]) -> str:
        """Format research results into a readable string for prompt"""
        if not isinstance(research_results, dict):
            return str(research_results)
        
        parts = []
        
        # Add rationale if available
        if research_results.get("rationale"):
            parts.append(f"Research Rationale: {research_results['rationale']}")
        
        # Add analysis summary
        analysis = research_results.get("analysis", {})
        if analysis:
            if analysis.get("optimal_goal"):
                parts.append(f"Optimal Goals: {analysis['optimal_goal']}")
            if analysis.get("recommended_channels"):
                parts.append(f"Recommended Channels: {', '.join(analysis['recommended_channels']) if isinstance(analysis['recommended_channels'], list) else analysis['recommended_channels']}")
            if analysis.get("recommended_schedule"):
                schedule = analysis["recommended_schedule"]
                if isinstance(schedule, dict):
                    schedule_parts = []
                    if schedule.get("startDate"):
                        schedule_parts.append(f"Start: {schedule['startDate']}")
                    if schedule.get("endDate"):
                        schedule_parts.append(f"End: {schedule['endDate']}")
                    if schedule_parts:
                        parts.append(f"Schedule: {', '.join(schedule_parts)}")
        
        # Add evidence summary
        evidence = research_results.get("evidence", {})
        if evidence:
            if evidence.get("historical_campaigns"):
                parts.append(f"Found {len(evidence['historical_campaigns'])} relevant historical campaigns")
        
        return "\n".join(parts) if parts else str(research_results)

