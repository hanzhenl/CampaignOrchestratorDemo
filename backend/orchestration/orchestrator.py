"""
Main Agent Orchestrator - Coordinates the full agent workflow
"""
from typing import Dict, Any, Optional
import logging
import sys
import os
# Add backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from agents.classification_agent import ClassificationAgent
from agents.planning_agent import PlanningAgent
from agents.validation_agent import ValidationAgent
from orchestration.plan_executor import PlanExecutor

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Main orchestration engine for agent workflows"""
    
    def __init__(self):
        self.classification_agent = ClassificationAgent()
        self.planning_agent = PlanningAgent()
        self.validation_agent = ValidationAgent()
        self.plan_executor = PlanExecutor()
    
    def orchestrate(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main orchestration method
        
        Flow:
        1. Classify user intent
        2. Create execution plan
        3. Execute plan
        4. Optionally validate results
        5. Return structured result
        
        Args:
            prompt: User prompt
            context: Optional context (conversation history, etc.)
            session_id: Optional session ID for tracking
        
        Returns:
            Orchestration result dict
        """
        try:
            # Step 1: Classify intent
            logger.info("Step 1: Classifying user intent")
            classification = self._classify_intent(prompt, context)
            
            if classification.get("error"):
                return classification
            
            intent = classification.get("intent")
            logger.info(f"Intent classified as: {intent}")
            
            # Step 2: Create execution plan
            logger.info("Step 2: Creating execution plan")
            plan = self._create_plan(prompt, classification, context)
            
            if plan.get("error"):
                return plan
            
            # Step 3: Execute plan
            logger.info("Step 3: Executing plan")
            execution_result = self._execute_plan(plan, prompt, context)
            
            # Step 4: Extract final result
            final_result = execution_result.get("final_result", {})
            
            # Step 5: Format response for UI
            response = self._format_response(
                intent,
                classification,
                final_result,
                execution_result
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Orchestration error: {str(e)}")
            return {
                "error": True,
                "error_type": "orchestration_error",
                "message": str(e)
            }
    
    def _classify_intent(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Classify user intent"""
        result = self.classification_agent.process(prompt, context)
        
        # Ensure valid intent
        intent = result.get("intent", "")
        valid_intents = ["research", "campaign_generation", "audience_generation", "search"]
        
        if intent not in valid_intents:
            # Default to campaign_generation if unclear
            result["intent"] = "campaign_generation"
            result["confidence"] = 0.5
        
        return result
    
    def _create_plan(
        self,
        prompt: str,
        classification: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create execution plan based on classification"""
        result = self.planning_agent.process_specialized(prompt, classification, context)
        
        # Validate plan structure
        if not result.get("plan"):
            # Create default plan based on intent
            intent = classification.get("intent")
            if intent == "campaign_generation":
                result = {
                    "plan": [
                        {
                            "step": 1,
                            "agent": "research",
                            "action": "Analyze campaign requirements",
                            "input": {"prompt": prompt}
                        },
                        {
                            "step": 2,
                            "agent": "campaign",
                            "action": "Generate campaign configuration",
                            "input": {"prompt": prompt}
                        }
                    ],
                    "estimated_steps": 2
                }
            elif intent == "audience_generation":
                result = {
                    "plan": [
                        {
                            "step": 1,
                            "agent": "audience",
                            "action": "Generate audience segment",
                            "input": {"prompt": prompt}
                        }
                    ],
                    "estimated_steps": 1
                }
            elif intent == "research":
                result = {
                    "plan": [
                        {
                            "step": 1,
                            "agent": "research",
                            "action": "Perform research analysis",
                            "input": {"prompt": prompt}
                        }
                    ],
                    "estimated_steps": 1
                }
            elif intent == "search":
                result = {
                    "plan": [
                        {
                            "step": 1,
                            "agent": "search",
                            "action": "Search for items",
                            "input": {"query": prompt}
                        }
                    ],
                    "estimated_steps": 1
                }
        
        return result
    
    def _execute_plan(
        self,
        plan: Dict[str, Any],
        prompt: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the execution plan"""
        return self.plan_executor.execute(plan, context)
    
    def _format_response(
        self,
        intent: str,
        classification: Dict[str, Any],
        final_result: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format final response for UI"""
        
        # Determine experience panel type based on intent
        experience_panel_type = "default"
        if intent == "campaign_generation":
            experience_panel_type = "campaign_form"
        elif intent == "audience_generation":
            experience_panel_type = "segment_form"
        elif intent == "search":
            experience_panel_type = "search_results"
        elif intent == "research":
            experience_panel_type = "research_analysis"
        
        # Extract campaign config if available
        campaign_config = None
        if "campaign" in final_result:
            campaign_config = final_result["campaign"]
        elif isinstance(final_result, list) and final_result:
            # Search results
            campaign_config = {"type": "search_results", "items": final_result}
        
        response = {
            "intent": intent,
            "classification": classification,
            "campaignConfig": campaign_config or final_result,
            "experiencePanelType": experience_panel_type,
            "reasoningSteps": execution_result.get("step_results", []),
            "success": execution_result.get("success", True)
        }
        
        return response

