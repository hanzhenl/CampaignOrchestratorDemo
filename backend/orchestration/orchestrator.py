"""
Main Agent Orchestrator - Coordinates the full agent workflow
"""
from typing import Dict, Any, Optional
import logging
import sys
import os
import copy
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
            # Ensure context is initialized
            if context is None:
                context = {}
            
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
    
    def _detect_chart_data(self, data: Any, path: str = "") -> Optional[Dict[str, Any]]:
        """
        Recursively detect chartable data in research results
        
        Args:
            data: Data structure to analyze
            path: Current path in the data structure (for debugging)
        
        Returns:
            Chart configuration dict if chartable data found, None otherwise
        """
        if isinstance(data, dict):
            # Check if chart data already exists (from create_chart tool)
            if "chart" in data and isinstance(data["chart"], dict):
                return data["chart"]
            
            # Check for chartData field
            if "chartData" in data and isinstance(data["chartData"], dict):
                return data["chartData"]
            
            # Look for evidence.historical_performance or similar structures
            if "evidence" in data and isinstance(data["evidence"], dict):
                evidence = data["evidence"]
                # Check for historical_performance with time-series data
                if "historical_performance" in evidence:
                    perf = evidence["historical_performance"]
                    if isinstance(perf, dict):
                        # Look for arrays of numeric data
                        for key, value in perf.items():
                            if isinstance(value, list) and len(value) > 1:
                                # Check if it's numeric data
                                if all(isinstance(x, (int, float)) for x in value):
                                    labels = [f"Point {i+1}" for i in range(len(value))]
                                    return {
                                        "title": f"{key.replace('_', ' ').title()} Over Time",
                                        "xLabel": "Time Period",
                                        "yLabel": key.replace('_', ' ').title(),
                                        "type": "line",
                                        "data": {
                                            "labels": labels,
                                            "datasets": [{
                                                "label": key.replace('_', ' ').title(),
                                                "data": value,
                                                "borderColor": "rgb(59, 130, 246)",
                                                "backgroundColor": "rgba(59, 130, 246, 0.1)"
                                            }]
                                        }
                                    }
            
            # Recursively check nested structures
            for key, value in data.items():
                chart_data = self._detect_chart_data(value, f"{path}.{key}")
                if chart_data:
                    return chart_data
        
        elif isinstance(data, list) and len(data) > 1:
            # Check if it's an array of numeric values
            if all(isinstance(x, (int, float)) for x in data):
                labels = [f"Point {i+1}" for i in range(len(data))]
                return {
                    "title": "Data Visualization",
                    "xLabel": "Index",
                    "yLabel": "Value",
                    "type": "line",
                    "data": {
                        "labels": labels,
                        "datasets": [{
                            "label": "Data",
                            "data": data,
                            "borderColor": "rgb(59, 130, 246)",
                            "backgroundColor": "rgba(59, 130, 246, 0.1)"
                        }]
                    }
                }
            # Check if it's an array of objects with x/y properties
            elif all(isinstance(x, dict) and "x" in x and "y" in x for x in data):
                labels = [str(point.get("x", "")) for point in data]
                values = [float(point.get("y", 0)) for point in data]
                return {
                    "title": "Data Visualization",
                    "xLabel": "X Axis",
                    "yLabel": "Y Axis",
                    "type": "line",
                    "data": {
                        "labels": labels,
                        "datasets": [{
                            "label": "Data",
                            "data": values,
                            "borderColor": "rgb(59, 130, 246)",
                            "backgroundColor": "rgba(59, 130, 246, 0.1)"
                        }]
                    }
                }
        
        return None
    
    def _detect_recommendations(self, data: Any, path: str = "") -> Optional[Dict[str, Any]]:
        """
        Recursively detect recommendations (campaigns or segments) in agent responses
        
        Args:
            data: Data structure to analyze
            path: Current path in the data structure (for debugging)
        
        Returns:
            Recommendations configuration dict if found, None otherwise
        """
        # Handle list of items (e.g., search results)
        if isinstance(data, list) and len(data) > 0:
            # Check if it's a list of search results with type field
            if all(isinstance(item, dict) and "type" in item for item in data):
                # Group by type
                campaigns = [item for item in data if item.get("type") == "campaign"]
                segments = [item for item in data if item.get("type") == "segment"]
                knowledge = [item for item in data if item.get("type") == "knowledge"]
                
                all_items = []
                rec_type = "mixed"
                
                if campaigns:
                    all_items.extend(campaigns)
                    if rec_type == "mixed":
                        rec_type = "campaign" if not segments else "mixed"
                
                if segments:
                    all_items.extend(segments)
                    if rec_type == "mixed":
                        rec_type = "segment" if not campaigns else "mixed"
                
                if knowledge:
                    all_items.extend(knowledge)
                    if rec_type == "mixed" and not campaigns and not segments:
                        rec_type = "mixed"  # Knowledge items are treated as mixed
                
                if all_items:
                    return {
                        "uiComponent": "recommendations",
                        "type": rec_type if rec_type != "mixed" or (campaigns and segments) else ("campaign" if campaigns else "segment"),
                        "items": all_items,
                        "title": "Search Results" if path == "" else "Recommended Items"
                    }
            # If it's a plain list of items (campaigns or segments)
            elif all(isinstance(item, dict) for item in data):
                # Check if items have campaign-like or segment-like structure
                has_campaign_fields = any("goals" in item or "segmentIds" in item for item in data)
                has_segment_fields = any("size" in item or "criteria" in item for item in data)
                
                if has_campaign_fields or has_segment_fields:
                    rec_type = "campaign" if has_campaign_fields and not has_segment_fields else ("segment" if has_segment_fields and not has_campaign_fields else "mixed")
                    return {
                        "uiComponent": "recommendations",
                        "type": rec_type,
                        "items": data,
                        "title": "Recommended Items"
                    }
        
        if isinstance(data, dict):
            # Check if recommendations already exist (from show_recommendations tool)
            if "recommendations" in data and isinstance(data["recommendations"], dict):
                return data["recommendations"]
            
            # Check for explicit recommendation fields
            if "recommended_campaigns" in data and isinstance(data["recommended_campaigns"], list):
                return {
                    "uiComponent": "recommendations",
                    "type": "campaign",
                    "items": data["recommended_campaigns"],
                    "title": "Recommended Campaigns"
                }
            
            if "recommended_segments" in data and isinstance(data["recommended_segments"], list):
                return {
                    "uiComponent": "recommendations",
                    "type": "segment",
                    "items": data["recommended_segments"],
                    "title": "Recommended Segments"
                }
            
            # Check for audience_recommendations in analysis
            if "analysis" in data and isinstance(data["analysis"], dict):
                analysis = data["analysis"]
                if "audience_recommendations" in analysis:
                    audience_recs = analysis["audience_recommendations"]
                    recommendations = []
                    rec_type = "mixed"
                    
                    # Check for existing segments
                    if "existing_segments" in audience_recs and isinstance(audience_recs["existing_segments"], list):
                        segment_ids = audience_recs["existing_segments"]
                        # Fetch full segment data
                        from utils.data_access import get_segments
                        all_segments = get_segments()
                        for seg_id in segment_ids:
                            segment = next((s for s in all_segments if s.get("id") == seg_id), None)
                            if segment:
                                recommendations.append(segment)
                                if rec_type == "mixed":
                                    rec_type = "segment"
                    
                    # Check for new segment suggestions
                    if "new_segment_suggestions" in audience_recs and isinstance(audience_recs["new_segment_suggestions"], list):
                        new_segments = audience_recs["new_segment_suggestions"]
                        for seg in new_segments:
                            if isinstance(seg, dict):
                                # Format as segment-like object
                                recommendations.append({
                                    "id": seg.get("name", "").lower().replace(" ", "-"),
                                    "name": seg.get("name", "New Segment"),
                                    "description": seg.get("criteria", seg.get("description", "")),
                                    "isSuggested": True
                                })
                                if rec_type == "mixed":
                                    rec_type = "segment"
                    
                    if recommendations:
                        return {
                            "uiComponent": "recommendations",
                            "type": rec_type,
                            "items": recommendations,
                            "title": "Recommended Segments"
                        }
            
            # Check for historical_campaigns that might be recommendations
            if "evidence" in data and isinstance(data["evidence"], dict):
                evidence = data["evidence"]
                if "historical_campaigns" in evidence and isinstance(evidence["historical_campaigns"], list):
                    campaigns = evidence["historical_campaigns"]
                    # If campaigns are explicitly marked as recommended or if context suggests it
                    recommended_campaigns = []
                    for campaign in campaigns:
                        if isinstance(campaign, dict):
                            # Check if marked as recommended
                            if campaign.get("recommended") or campaign.get("isRecommended"):
                                recommended_campaigns.append(campaign)
                            # If it's in evidence and has performance data, it might be a recommendation
                            elif "performance" in campaign or campaign.get("status") == "completed":
                                recommended_campaigns.append(campaign)
                            # For research results, if campaigns are in evidence, they're likely recommendations
                            # (research agent found them as relevant examples)
                            elif path == "" or "research" in path.lower():
                                recommended_campaigns.append(campaign)
                    
                    if recommended_campaigns:
                        return {
                            "uiComponent": "recommendations",
                            "type": "campaign",
                            "items": recommended_campaigns,
                            "title": "Recommended Campaigns"
                        }
            
            # Recursively check nested structures
            for key, value in data.items():
                rec_data = self._detect_recommendations(value, f"{path}.{key}")
                if rec_data:
                    return rec_data
        
        return None
    
    def _format_source_references(
        self,
        execution_result: Dict[str, Any],
        final_result: Dict[str, Any]
    ) -> str:
        """
        Extract source references from research evidence and format as markdown.
        
        Args:
            execution_result: Execution result with step_results
            final_result: Final result from agents
        
        Returns:
            Formatted markdown string with source references, or empty string
        """
        sources_text = ""
        source_campaigns = []
        source_segments = []
        
        # Check step results for research evidence
        step_results = execution_result.get("step_results", [])
        for step in step_results:
            if step.get("agent") == "research":
                result = step.get("result", {})
                if isinstance(result, dict):
                    evidence = result.get("evidence", {})
                    if evidence:
                        # Extract campaign sources
                        historical_campaigns = evidence.get("historical_campaigns", [])
                        if historical_campaigns:
                            for campaign in historical_campaigns[:5]:  # Limit to 5
                                if isinstance(campaign, dict):
                                    campaign_id = campaign.get("id")
                                    campaign_name = campaign.get("name", campaign_id)
                                    if campaign_id:
                                        # Avoid duplicates
                                        if not any(c["id"] == campaign_id for c in source_campaigns):
                                            source_campaigns.append({
                                                "id": campaign_id,
                                                "name": campaign_name
                                            })
                        
                        # Extract segment sources from evidence if available
                        # (segments might be in analysis.audience_recommendations)
                        analysis = result.get("analysis", {})
                        if analysis:
                            audience_recs = analysis.get("audience_recommendations", {})
                            if audience_recs:
                                existing_segments = audience_recs.get("existing_segments", [])
                                if existing_segments:
                                    # Fetch segment names
                                    from utils.data_access import get_segments
                                    all_segments = get_segments()
                                    for seg_id in existing_segments[:5]:  # Limit to 5
                                        segment = next((s for s in all_segments if s.get("id") == seg_id), None)
                                        if segment:
                                            # Avoid duplicates
                                            if not any(s["id"] == seg_id for s in source_segments):
                                                source_segments.append({
                                                    "id": seg_id,
                                                    "name": segment.get("name", seg_id)
                                                })
        
        # Also check final_result for evidence
        if isinstance(final_result, dict):
            evidence = final_result.get("evidence", {})
            if evidence:
                historical_campaigns = evidence.get("historical_campaigns", [])
                if historical_campaigns:
                    for campaign in historical_campaigns[:5]:
                        if isinstance(campaign, dict):
                            campaign_id = campaign.get("id")
                            campaign_name = campaign.get("name", campaign_id)
                            if campaign_id and not any(c["id"] == campaign_id for c in source_campaigns):
                                source_campaigns.append({
                                    "id": campaign_id,
                                    "name": campaign_name
                                })
        
        # Format sources as markdown links
        if source_campaigns or source_segments:
            sources_text = "\n\n---\n\n**Based on:**\n\n"
            
            if source_campaigns:
                sources_text += "**Campaigns:** "
                campaign_refs = [f"[{c['name']}](grounding://campaign/{c['id']})" for c in source_campaigns]
                sources_text += ", ".join(campaign_refs)
                sources_text += "\n\n"
            
            if source_segments:
                sources_text += "**Segments:** "
                segment_refs = [f"[{s['name']}](grounding://segment/{s['id']})" for s in source_segments]
                sources_text += ", ".join(segment_refs)
                sources_text += "\n\n"
        
        return sources_text
    
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
        rationale = None
        
        # Extract rationale from final_result (for dialog panel)
        if isinstance(final_result, dict):
            rationale = final_result.get("rationale")
            # Also check in analysis field
            if not rationale and final_result.get("analysis"):
                analysis = final_result.get("analysis")
                if isinstance(analysis, dict):
                    rationale = analysis.get("rationale")
        
        # Extract and format source references
        source_references = self._format_source_references(execution_result, final_result)
        
        # Append source references to rationale if available
        if source_references and rationale:
            rationale = rationale + source_references
        elif source_references:
            # If no rationale but we have sources, create a minimal message with sources
            rationale = "Analysis completed." + source_references
        
        if "campaign" in final_result:
            campaign_config = final_result["campaign"]
            # Ensure it's a dict
            if not isinstance(campaign_config, dict):
                campaign_config = {}
            # Preserve other useful fields from final_result
            if isinstance(final_result, dict):
                for key in ["rationale", "analysis", "evidence"]:
                    if key in final_result and key not in campaign_config:
                        campaign_config[key] = final_result[key]
        elif isinstance(final_result, list) and final_result:
            # Search results
            campaign_config = {"type": "search_results", "items": final_result}
        else:
            # For research and other intents, use full result
            campaign_config = final_result if isinstance(final_result, dict) else {}
        
        # CRITICAL: Ensure campaign_config is always a dict
        if not isinstance(campaign_config, dict):
            campaign_config = {}
        
        # Include rationale in campaign_config for UI access
        if rationale and isinstance(campaign_config, dict):
            campaign_config["rationale"] = rationale
        
        # Initialize UI components list
        ui_components = []
        
        # Add UI component for campaign generation
        if intent == "campaign_generation":
            # Ensure campaign_config is a dict
            if not isinstance(campaign_config, dict):
                campaign_config = {}
            
            # Create a deep copy of campaign_config for the data field to avoid circular reference
            # We'll exclude uiComponents from the copy since we'll add it later
            campaign_data = copy.deepcopy(campaign_config)
            # Remove uiComponents if it exists in the copy (it shouldn't at this point, but be safe)
            campaign_data.pop("uiComponents", None)
            campaign_data.pop("primaryComponent", None)
            
            # For campaign_generation, always use campaign_form (not campaign detail)
            # This allows users to edit and refine the generated campaign
            ui_components.append({"type": "campaign_form", "data": campaign_data})
            experience_panel_type = "campaign_form"
        
        # Add UI component for audience generation
        if intent == "audience_generation" and campaign_config and isinstance(campaign_config, dict):
            # Create a deep copy of campaign_config for the data field to avoid circular reference
            segment_data = copy.deepcopy(campaign_config)
            # Remove uiComponents if it exists in the copy
            segment_data.pop("uiComponents", None)
            segment_data.pop("primaryComponent", None)
            
            if campaign_config.get("name"):
                # Add segment detail component
                ui_components.append({"type": "segment", "data": segment_data})
                experience_panel_type = "segment"
            else:
                # Add segment form component
                ui_components.append({"type": "segment_form", "data": segment_data})
                experience_panel_type = "segment_form"
        
        # Add UI component for research intent
        if intent == "research":
            # Research results should have analysis, evidence, or rationale
            research_data = copy.deepcopy(campaign_config)
            research_data.pop("uiComponents", None)
            research_data.pop("primaryComponent", None)
            
            # If no chart or recommendations detected yet, show research analysis
            # (chart and recommendations will be added later if found)
            if not any(c.get("type") in ["chart", "recommendations"] for c in ui_components):
                # Add a research analysis component (or use chart/recommendations if found)
                ui_components.append({"type": "research_analysis", "data": research_data})
                experience_panel_type = "research_analysis"
        
        # Add UI component for knowledge generation (if intent exists)
        if intent == "knowledge_generation" and campaign_config and isinstance(campaign_config, dict):
            knowledge_data = copy.deepcopy(campaign_config)
            knowledge_data.pop("uiComponents", None)
            knowledge_data.pop("primaryComponent", None)
            
            if campaign_config.get("title") or campaign_config.get("id"):
                # Knowledge article detail
                ui_components.append({"type": "knowledge", "data": knowledge_data})
                experience_panel_type = "knowledge"
            else:
                # Knowledge list or form
                ui_components.append({"type": "knowledge_list", "data": knowledge_data})
                experience_panel_type = "knowledge_list"
        
        # Handle search intent - format search results as recommendations
        if intent == "search" and isinstance(final_result, list) and len(final_result) > 0:
            # Format search results as recommendations
            recommendations_data = {
                "uiComponent": "recommendations",
                "type": "mixed",
                "items": final_result,
                "title": "Search Results",
                "description": f"Found {len(final_result)} result(s)"
            }
            ui_components.append({"type": "recommendations", "data": recommendations_data})
        
        # Auto-detect chart data for research results (and other intents that might have charts)
        chart_data = None
        # Check for charts in all intents, not just research
        chart_data = self._detect_chart_data(final_result)
        
        # Also check reasoning steps for chart tool calls
        if not chart_data:
            step_results = execution_result.get("step_results", [])
            for step in step_results:
                result = step.get("result", {})
                if isinstance(result, dict) and "chart" in result:
                    chart_data = result["chart"]
                    break
        
        if chart_data:
            ui_components.append({"type": "chart", "data": chart_data})
        
        # Auto-detect recommendations for ALL intents
        recommendations_data = None
        
        # For campaign_generation, check research step results first (they often contain recommendations)
        if intent == "campaign_generation":
            step_results = execution_result.get("step_results", [])
            # Check research step (usually first step) for recommendations
            for step in step_results:
                if step.get("agent") == "research":
                    result = step.get("result", {})
                    if isinstance(result, dict):
                        detected = self._detect_recommendations(result)
                        if detected:
                            recommendations_data = detected
                            break
        
        # Check final_result for recommendations (if not already found)
        if not recommendations_data:
            # Only detect from final_result if we haven't already set it for search
            if intent != "search" or not isinstance(final_result, list):
                recommendations_data = self._detect_recommendations(final_result)
        
        # Also check reasoning steps for explicit show_recommendations tool calls
        if not recommendations_data:
            step_results = execution_result.get("step_results", [])
            for step in step_results:
                result = step.get("result", {})
                if isinstance(result, dict) and "recommendations" in result:
                    recommendations_data = result["recommendations"]
                    break
        
        # Also check all step results for recommendations in nested structures (if not already found)
        if not recommendations_data:
            step_results = execution_result.get("step_results", [])
            for step in step_results:
                result = step.get("result", {})
                if isinstance(result, dict):
                    detected = self._detect_recommendations(result)
                    if detected:
                        recommendations_data = detected
                        break
        
        recommendations_data_copy = None
        if recommendations_data:
            # Create a deep copy of recommendations_data to avoid any circular references
            recommendations_data_copy = copy.deepcopy(recommendations_data)
            # Only add if not already added (e.g., for search intent)
            if not any(c.get("type") == "recommendations" for c in ui_components):
                ui_components.append({"type": "recommendations", "data": recommendations_data_copy})
        
        # Determine primary component
        # For campaign/audience generation: prioritize form/detail > recommendations > chart
        # For other intents: prioritize recommendations > chart > others
        primary_component = None
        if ui_components:
            if intent == "campaign_generation":
                # For campaign generation, always prioritize campaign_form (never campaign detail)
                campaign_form_comp = next((c for c in ui_components if c["type"] == "campaign_form"), None)
                recommendations_comp = next((c for c in ui_components if c["type"] == "recommendations"), None)
                chart_comp = next((c for c in ui_components if c["type"] == "chart"), None)
                
                if campaign_form_comp:
                    primary_component = "campaign_form"
                    experience_panel_type = "campaign_form"
                elif recommendations_comp:
                    primary_component = "recommendations"
                    experience_panel_type = "recommendations"
                elif chart_comp:
                    primary_component = "chart"
                    experience_panel_type = "chart"
                else:
                    primary_component = ui_components[0]["type"]
                    experience_panel_type = primary_component
            elif intent == "audience_generation":
                # For audience generation, prioritize segment/segment_form over recommendations
                segment_comp = next((c for c in ui_components if c["type"] in ["segment", "segment_form"]), None)
                recommendations_comp = next((c for c in ui_components if c["type"] == "recommendations"), None)
                chart_comp = next((c for c in ui_components if c["type"] == "chart"), None)
                
                if segment_comp:
                    primary_component = segment_comp["type"]
                    experience_panel_type = primary_component
                elif recommendations_comp:
                    primary_component = "recommendations"
                    experience_panel_type = "recommendations"
                elif chart_comp:
                    primary_component = "chart"
                    experience_panel_type = "chart"
                else:
                    primary_component = ui_components[0]["type"]
                    experience_panel_type = primary_component
            else:
                # For other intents (research, search, etc.), prioritize chart > recommendations > others
                chart_comp = next((c for c in ui_components if c["type"] == "chart"), None)
                recommendations_comp = next((c for c in ui_components if c["type"] == "recommendations"), None)
                campaign_comp = next((c for c in ui_components if c["type"] in ["campaign", "campaign_form", "segment", "segment_form"]), None)
                
                if chart_comp:
                    primary_component = "chart"
                    experience_panel_type = "chart"
                elif recommendations_comp:
                    primary_component = "recommendations"
                    experience_panel_type = "recommendations"
                elif campaign_comp:
                    primary_component = campaign_comp["type"]
                    experience_panel_type = primary_component
                else:
                    primary_component = ui_components[0]["type"]
                    experience_panel_type = primary_component
        elif intent in ["campaign_generation", "audience_generation"]:
            # Fallback: if no components were added (shouldn't happen), set default
            if intent == "campaign_generation":
                primary_component = "campaign_form"
                experience_panel_type = "campaign_form"
            elif intent == "audience_generation":
                primary_component = "segment_form"
                experience_panel_type = "segment_form"
        
        # Always merge UI components into campaign_config
        if not campaign_config:
            campaign_config = {}
        
        # Ensure campaign_config is always a dict
        if not isinstance(campaign_config, dict):
            campaign_config = {}
        
        # Always set uiComponents if we have any, or if this is campaign/segment generation (should always have at least one)
        if ui_components:
            campaign_config["uiComponents"] = ui_components
            # Ensure primaryComponent is set (should always be set if ui_components exists)
            if primary_component:
                campaign_config["primaryComponent"] = primary_component
            else:
                # Fallback: use first component type
                campaign_config["primaryComponent"] = ui_components[0]["type"]
        elif intent in ["campaign_generation", "audience_generation"]:
            # Fallback: ensure at least one component exists for campaign/segment generation
            # This should rarely happen, but ensures UI always has something to display
            if intent == "campaign_generation":
                campaign_data = copy.deepcopy(campaign_config)
                campaign_data.pop("uiComponents", None)
                campaign_config["uiComponents"] = [{"type": "campaign_form", "data": campaign_data}]
                campaign_config["primaryComponent"] = "campaign_form"
                experience_panel_type = "campaign_form"
                primary_component = "campaign_form"
            elif intent == "audience_generation":
                segment_data = copy.deepcopy(campaign_config)
                segment_data.pop("uiComponents", None)
                campaign_config["uiComponents"] = [{"type": "segment_form", "data": segment_data}]
                campaign_config["primaryComponent"] = "segment_form"
                experience_panel_type = "segment_form"
                primary_component = "segment_form"
            
            # Also add individual components for backward compatibility
            if chart_data:
                campaign_config["chart"] = copy.deepcopy(chart_data)
            if recommendations_data_copy:
                # Use the copy we already created
                campaign_config["recommendations"] = recommendations_data_copy
        
        # Ensure uiComponents is always set for campaign/audience generation (even if empty list was created)
        if intent in ["campaign_generation", "audience_generation"] and "uiComponents" not in campaign_config:
            # This should never happen, but as a safety net, ensure we have at least one component
            if intent == "campaign_generation":
                campaign_data = copy.deepcopy(campaign_config)
                campaign_data.pop("uiComponents", None)
                campaign_config["uiComponents"] = [{"type": "campaign_form", "data": campaign_data}]
                campaign_config["primaryComponent"] = "campaign_form"
                experience_panel_type = "campaign_form"
            elif intent == "audience_generation":
                segment_data = copy.deepcopy(campaign_config)
                segment_data.pop("uiComponents", None)
                campaign_config["uiComponents"] = [{"type": "segment_form", "data": segment_data}]
                campaign_config["primaryComponent"] = "segment_form"
                experience_panel_type = "segment_form"
        
        # FINAL VALIDATION: Ensure uiComponents is always set
        if "uiComponents" not in campaign_config or not campaign_config.get("uiComponents"):
            logger.warning(f"uiComponents not set for intent {intent}, creating fallback")
            
            # Create appropriate fallback based on intent
            fallback_data = copy.deepcopy(campaign_config)
            fallback_data.pop("uiComponents", None)
            fallback_data.pop("primaryComponent", None)
            
            if intent == "campaign_generation":
                campaign_config["uiComponents"] = [{"type": "campaign_form", "data": fallback_data}]
                campaign_config["primaryComponent"] = "campaign_form"
            elif intent == "audience_generation":
                campaign_config["uiComponents"] = [{"type": "segment_form", "data": fallback_data}]
                campaign_config["primaryComponent"] = "segment_form"
            elif intent == "research":
                campaign_config["uiComponents"] = [{"type": "research_analysis", "data": fallback_data}]
                campaign_config["primaryComponent"] = "research_analysis"
            elif intent == "search":
                # Search should have been handled earlier, but fallback to recommendations
                if isinstance(final_result, list) and final_result:
                    campaign_config["uiComponents"] = [{"type": "recommendations", "data": {
                        "type": "mixed",
                        "items": final_result,
                        "title": "Search Results"
                    }}]
                    campaign_config["primaryComponent"] = "recommendations"
                else:
                    campaign_config["uiComponents"] = [{"type": "research_analysis", "data": fallback_data}]
                    campaign_config["primaryComponent"] = "research_analysis"
            elif intent == "knowledge_generation":
                campaign_config["uiComponents"] = [{"type": "knowledge_list", "data": fallback_data}]
                campaign_config["primaryComponent"] = "knowledge_list"
            else:
                # Generic fallback
                campaign_config["uiComponents"] = [{"type": "research_analysis", "data": fallback_data}]
                campaign_config["primaryComponent"] = "research_analysis"
        
        # Log final structure for debugging
        logger.info(f"Final campaign_config has uiComponents: {'uiComponents' in campaign_config}")
        logger.info(f"uiComponents count: {len(campaign_config.get('uiComponents', []))}")
        logger.info(f"primaryComponent: {campaign_config.get('primaryComponent')}")
        
        # #region agent log
        import json
        import time
        with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"orchestrator.py:_format_response:before_response", "message":"About to create response", "data":{"campaign_config_has_uiComponents":"uiComponents" in campaign_config, "uiComponents_count":len(campaign_config.get("uiComponents", [])), "primaryComponent":campaign_config.get("primaryComponent"), "campaign_config_keys":list(campaign_config.keys()) if isinstance(campaign_config, dict) else None, "uiComponents_structure":[{"type":c.get("type"), "has_data":c.get("data") is not None} for c in campaign_config.get("uiComponents", [])]}, "timestamp":int(time.time()*1000), "sessionId":"debug-session", "runId":"run1", "hypothesisId":"A"})+'\n')
        # #endregion
        
        response = {
            "intent": intent,
            "classification": classification,
            "campaignConfig": campaign_config or final_result,
            "experiencePanelType": experience_panel_type,
            "reasoningSteps": execution_result.get("step_results", []),
            "success": execution_result.get("success", True)
        }
        
        # #region agent log
        with open('/Users/hanzhenliu/Desktop/Oneiros/CampaignOrchestratorDemo/.cursor/debug.log', 'a') as f:
            f.write(json.dumps({"location":"orchestrator.py:_format_response:response_created", "message":"Response created", "data":{"response_has_campaignConfig":"campaignConfig" in response, "campaignConfig_has_uiComponents":"uiComponents" in (response.get("campaignConfig", {}) if isinstance(response.get("campaignConfig"), dict) else {}), "experiencePanelType":response.get("experiencePanelType")}, "timestamp":int(time.time()*1000), "sessionId":"debug-session", "runId":"run1", "hypothesisId":"A"})+'\n')
        # #endregion
        
        # Add rationale to response for dialog panel (if available)
        if rationale:
            response["rationale"] = rationale
        
        return response

