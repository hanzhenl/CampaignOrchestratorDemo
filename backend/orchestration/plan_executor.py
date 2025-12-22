"""
Plan Executor - Executes multi-step plans created by Planning Agent
"""
from typing import Dict, Any, List, Optional
import logging

import sys
import os
# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from agents.research_agent import ResearchAgent
from agents.campaign_agent import CampaignAgent
from agents.audience_agent import AudienceAgent
from agents.journey_agent import JourneyAgent
from utils.data_access import search_campaigns, search_segments, search_knowledge

logger = logging.getLogger(__name__)

class PlanExecutor:
    """Executes execution plans step by step"""
    
    def __init__(self):
        # Initialize agents
        self.agents = {
            "research": ResearchAgent(),
            "campaign": CampaignAgent(),
            "audience": AudienceAgent(),
            "journey": JourneyAgent()
        }
    
    def execute(
        self,
        plan: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a multi-step plan
        
        Args:
            plan: Plan dict with "plan" array of steps
            context: Execution context (accumulates results)
        
        Returns:
            Final execution result
        """
        if context is None:
            context = {"results": {}, "step_results": []}
        
        steps = plan.get("plan", [])
        logger.info(f"Executing plan with {len(steps)} steps")
        
        for step in steps:
            step_num = step.get("step", 0)
            agent_name = step.get("agent")
            action = step.get("action", "")
            step_input = step.get("input", {})
            
            logger.info(f"Executing step {step_num}: {agent_name} - {action}")
            
            try:
                result = self._execute_step(step, context)
                context["step_results"].append({
                    "step": step_num,
                    "agent": agent_name,
                    "result": result,
                    "success": not result.get("error", False)
                })
                
                # Add result to context for next steps
                context["results"][agent_name] = result
                
            except Exception as e:
                logger.error(f"Error executing step {step_num}: {str(e)}")
                context["step_results"].append({
                    "step": step_num,
                    "agent": agent_name,
                    "error": str(e),
                    "success": False
                })
        
        # Return final result (usually from last step)
        if context["step_results"]:
            last_result = context["step_results"][-1]["result"]
            return {
                "success": True,
                "final_result": last_result,
                "all_results": context["results"],
                "step_results": context["step_results"]
            }
        
        return {"success": False, "error": "No steps executed"}
    
    def _execute_step(
        self,
        step: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a single plan step"""
        agent_name = step.get("agent")
        step_input = step.get("input", {})
        
        # Handle search separately (not an agent)
        if agent_name == "search":
            return self._handle_search(step_input.get("query", ""))
        
        # Get agent
        agent = self.agents.get(agent_name)
        if not agent:
            return {"error": True, "message": f"Unknown agent: {agent_name}"}
        
        # Prepare input
        prompt = step_input.get("prompt", "")
        
        # Special handling for campaign agent with research results
        if agent_name == "campaign":
            research_results = context.get("results", {}).get("research") if context else None
            if isinstance(agent, CampaignAgent):
                return agent.process_specialized(prompt, research_results, context)
        
        # Standard agent call
        return agent.process(prompt, context)
    
    def _handle_search(self, query: str) -> List[Dict]:
        """Handle search intent (not an agent)"""
        results = []
        
        # Search all categories
        campaigns = search_campaigns(query)
        segments = search_segments(query)
        knowledge = search_knowledge(query)
        
        for campaign in campaigns:
            results.append({
                "type": "campaign",
                "id": campaign.get("id"),
                "title": campaign.get("name"),
                "description": campaign.get("description", "")
            })
        
        for segment in segments:
            results.append({
                "type": "segment",
                "id": segment.get("id"),
                "title": segment.get("name"),
                "description": f"Segment with {segment.get('size', 0)} members"
            })
        
        for article in knowledge:
            results.append({
                "type": "knowledge",
                "id": article.get("id"),
                "title": article.get("title"),
                "description": article.get("content", "")[:100]
            })
        
        return results

