"""
AI-native Campaign Orchestrator - FastAPI Backend
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
from pydantic import BaseModel
import uuid

app = FastAPI(title="Campaign Launchpad API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data storage (using JSON files for POC)
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Pydantic models
class DialogMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    reasoningSteps: Optional[List[Dict]] = None
    metadata: Optional[Dict] = None

class DialogSession(BaseModel):
    id: Optional[str] = None
    title: str
    state: Optional[Dict] = None
    agentContext: Optional[Dict] = None
    messages: Optional[List[DialogMessage]] = []
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    goals: Optional[List[str]] = []  # Changed to array
    segmentIds: Optional[List[str]] = []  # Changed to array for multiple segments
    estimatedAudienceSize: Optional[int] = None
    schedule: Optional[Dict] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    progress: Optional[float] = None
    userFlowConfig: Optional[Dict] = None
    channels: List[str] = []
    variants: Optional[List[Dict]] = None
    creatives: Optional[List[Dict]] = None
    sessionId: Optional[str] = None

class KnowledgeArticle(BaseModel):
    title: str
    content: str
    articleType: Optional[str] = "general"
    metadata: Optional[Dict] = None

class SegmentCreate(BaseModel):
    name: str
    filters: Dict
    demographics: Optional[Dict] = None
    behaviors: Optional[Dict] = None

# Helper functions for data persistence
def load_json(filepath: str) -> Any:
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []

def save_json(filepath: str, data: Any):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def format_research_content(research_data: Dict[str, Any]) -> str:
    """
    Extract readable content from research agent response.
    Prefers 'rationale' field, falls back to formatted 'analysis' summary.
    
    Args:
        research_data: Research agent response dict with 'rationale', 'analysis', 'evidence'
    
    Returns:
        Formatted string for dialog display
    """
    if not isinstance(research_data, dict):
        return "Analysis completed"
    
    # Prefer rationale if available
    if research_data.get("rationale"):
        return research_data["rationale"]
    
    # Fall back to formatting analysis fields
    analysis = research_data.get("analysis", {})
    if not analysis:
        return "Analysis completed"
    
    # Build summary from analysis fields
    parts = []
    
    # Optimal goal
    optimal_goal = analysis.get("optimal_goal")
    if optimal_goal:
        if isinstance(optimal_goal, list):
            parts.append(f"Optimal Goals: {', '.join(optimal_goal)}")
        else:
            parts.append(f"Optimal Goal: {optimal_goal}")
    
    # Recommended channels
    recommended_channels = analysis.get("recommended_channels")
    if recommended_channels:
        if isinstance(recommended_channels, list):
            parts.append(f"Recommended Channels: {', '.join(recommended_channels)}")
        else:
            parts.append(f"Recommended Channel: {recommended_channels}")
    
    # Recommended schedule
    recommended_schedule = analysis.get("recommended_schedule")
    if recommended_schedule and isinstance(recommended_schedule, dict):
        schedule_parts = []
        if recommended_schedule.get("startDate"):
            schedule_parts.append(f"Start: {recommended_schedule['startDate']}")
        if recommended_schedule.get("endDate"):
            schedule_parts.append(f"End: {recommended_schedule['endDate']}")
        if recommended_schedule.get("duration"):
            schedule_parts.append(f"Duration: {recommended_schedule['duration']}")
        if schedule_parts:
            parts.append(f"Schedule: {', '.join(schedule_parts)}")
    
    # Audience recommendations
    audience_recommendations = analysis.get("audience_recommendations")
    if audience_recommendations and isinstance(audience_recommendations, dict):
        existing_segments = audience_recommendations.get("existing_segments", [])
        if existing_segments:
            parts.append(f"Existing Segments: {len(existing_segments)} found")
    
    if parts:
        return "\n".join(parts)
    
    return "Analysis completed"

def format_intent_message(intent: str) -> str:
    """
    Format intent classification into a user-friendly message.
    
    Args:
        intent: Intent classification string
    
    Returns:
        Formatted message string
    """
    intent_messages = {
        "research": "Research analysis completed",
        "campaign_generation": "Campaign generation completed",
        "audience_generation": "Audience generation completed",
        "search": "Search completed"
    }
    
    return intent_messages.get(intent, "Request completed")

def format_reasoning_steps(step_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format reasoning steps for display in dialog panel.
    Converts complex result objects into readable strings.
    
    Args:
        step_results: List of step result dicts with 'step', 'agent', 'result', etc.
    
    Returns:
        List of formatted step dicts with readable 'result' strings
    """
    formatted_steps = []
    
    for step in step_results:
        step_num = step.get("step", "?")
        agent = step.get("agent", "unknown")
        result = step.get("result", {})
        success = step.get("success", True)
        error = step.get("error")
        
        # Format the result into a readable string
        if error:
            result_str = f"Error: {error}"
        elif isinstance(result, dict):
            # Extract key information from result dict
            if result.get("error"):
                result_str = f"Error: {result.get('error', 'Unknown error')}"
            elif "campaign" in result:
                campaign = result["campaign"]
                if isinstance(campaign, dict):
                    name = campaign.get("name", "Campaign")
                    result_str = f"Generated campaign: {name}"
                else:
                    result_str = "Campaign generated"
            elif "analysis" in result or "rationale" in result:
                # Research result
                rationale = result.get("rationale", "")
                if rationale:
                    result_str = rationale[:200] + "..." if len(rationale) > 200 else rationale
                else:
                    analysis = result.get("analysis", {})
                    if analysis:
                        goals = analysis.get("optimal_goal", [])
                        channels = analysis.get("recommended_channels", [])
                        if goals or channels:
                            parts = []
                            if goals:
                                parts.append(f"Goals: {', '.join(goals) if isinstance(goals, list) else goals}")
                            if channels:
                                parts.append(f"Channels: {', '.join(channels) if isinstance(channels, list) else channels}")
                            result_str = "; ".join(parts)
                        else:
                            result_str = "Research analysis completed"
                    else:
                        result_str = "Research analysis completed"
            elif "segment" in result:
                segment = result["segment"]
                if isinstance(segment, dict):
                    name = segment.get("name", "Segment")
                    result_str = f"Generated segment: {name}"
                else:
                    result_str = "Segment generated"
            elif "name" in result:
                result_str = f"Generated: {result.get('name')}"
            else:
                # Fallback: create a summary
                result_str = f"Step {step_num} completed by {agent}"
        elif isinstance(result, str):
            result_str = result
        elif isinstance(result, list):
            result_str = f"Found {len(result)} results"
        else:
            result_str = f"Step {step_num} completed by {agent}"
        
        formatted_steps.append({
            "step": step_num,
            "agent": agent,
            "result": result_str,
            "success": success
        })
    
    return formatted_steps

# Import new orchestration system
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from orchestration.orchestrator import AgentOrchestrator
import logging
from utils.session_storage import load_sessions, atomic_session_operation
from utils.file_lock import FileLockError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize new orchestration system
orchestrator = AgentOrchestrator()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "Campaign Launchpad API", "version": "1.0.0"}

# Agent Orchestration
@app.post("/api/v1/agent/orchestrate")
async def orchestrate_agent(request: Dict[str, Any]):
    prompt = request.get("prompt", "")
    context = request.get("context", {})
    session_id = request.get("sessionId")
    knowledge_articles = request.get("knowledgeArticles", [])
    
    # If knowledge articles are provided, add them to context
    if knowledge_articles:
        if not isinstance(context, dict):
            context = {}
        context["knowledge_articles"] = knowledge_articles
    
    try:
        # Use new orchestration system
        result = orchestrator.orchestrate(prompt, context, session_id)
        
        # Store in dialog session if sessionId provided
        if session_id:
            try:
                with atomic_session_operation() as sessions:
                    session = next((s for s in sessions if s["id"] == session_id), None)
                    if session:
                        # Check if user message was already added (via API endpoint)
                        # Only add user message if the last message is not the same user message
                        last_message = session["messages"][-1] if session["messages"] else None
                        if not last_message or last_message.get("role") != "user" or last_message.get("content") != prompt:
                            # Add user message
                            message = {
                                "id": str(uuid.uuid4()),
                                "role": "user",
                                "content": prompt,
                                "timestamp": datetime.now().isoformat()
                            }
                            session["messages"].append(message)
                        
                        # Add assistant message
                        intent = result.get("intent", "")
                        campaign_config = result.get("campaignConfig", {})
                        raw_reasoning_steps = result.get("reasoningSteps", [])
                        
                        # Priority 1: Use rationale from campaign agent (if available)
                        rationale = result.get("rationale")
                        if not rationale and isinstance(campaign_config, dict):
                            rationale = campaign_config.get("rationale")
                        
                        # Priority 2: For campaign_generation, check if there's research analysis in step results
                        research_result = None
                        if intent == "campaign_generation" and raw_reasoning_steps:
                            # Find the research step result
                            for step in raw_reasoning_steps:
                                if step.get("agent") == "research":
                                    research_result = step.get("result", {})
                                    break
                        
                        # Check if this is a research result
                        is_research = (
                            intent == "research" or 
                            (isinstance(campaign_config, dict) and 
                             ("rationale" in campaign_config or "analysis" in campaign_config or "evidence" in campaign_config))
                        )
                        
                        # Determine proposal content with priority: rationale > research > intent message
                        if rationale:
                            # Use campaign agent's rationale for dialog panel
                            proposal = rationale
                        elif is_research and isinstance(campaign_config, dict):
                            # Use research content formatter
                            proposal = format_research_content(campaign_config)
                        elif intent == "campaign_generation" and research_result:
                            # For campaign_generation, show the research analysis
                            proposal = format_research_content(research_result)
                        elif isinstance(campaign_config, dict):
                            # Regular campaign config - show intent classification
                            proposal = format_intent_message(intent) if intent else "Request completed"
                        elif isinstance(campaign_config, list):
                            proposal = f"Found {len(campaign_config)} results"
                        else:
                            # Fallback to intent-based message
                            proposal = format_intent_message(intent) if intent else "Analysis completed"
                        
                        # Format reasoning steps for display
                        formatted_reasoning_steps = format_reasoning_steps(raw_reasoning_steps) if raw_reasoning_steps else []
                        
                        assistant_message = {
                            "id": str(uuid.uuid4()),
                            "role": "assistant",
                            "content": proposal,
                            "reasoningSteps": formatted_reasoning_steps,
                            "timestamp": datetime.now().isoformat()
                        }
                        session["messages"].append(assistant_message)
                        session["updatedAt"] = datetime.now().isoformat()
            except FileLockError as e:
                logger.warning(f"Lock error updating session {session_id}: {str(e)} - continuing without session update")
                # Don't fail the orchestration if session update fails
            except Exception as e:
                logger.warning(f"Error updating session {session_id}: {str(e)} - continuing without session update")
                # Don't fail the orchestration if session update fails
        
        return result
    
    except Exception as e:
        logger.error(f"Orchestration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

# Additional agent endpoints for testing
@app.post("/api/v1/agent/classify")
async def classify_intent(request: Dict[str, Any]):
    """Direct classification endpoint for testing"""
    try:
        from agents.classification_agent import ClassificationAgent
        agent = ClassificationAgent()
        prompt = request.get("prompt", "")
        result = agent.process(prompt)
        return result
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agent/research")
async def research_analysis(request: Dict[str, Any]):
    """Direct research agent endpoint for testing"""
    try:
        from agents.research_agent import ResearchAgent
        agent = ResearchAgent()
        prompt = request.get("prompt", "")
        context = request.get("context", {})
        result = agent.process(prompt, context)
        return result
    except Exception as e:
        logger.error(f"Research error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Dialog Sessions
@app.get("/api/v1/dialog/sessions")
async def list_sessions():
    try:
        sessions = load_sessions()
        return sessions
    except FileLockError as e:
        logger.error(f"Lock error listing sessions: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - unable to acquire lock")
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.post("/api/v1/dialog/sessions")
async def create_session(session: DialogSession):
    try:
        with atomic_session_operation() as sessions:
            new_session = {
                "id": str(uuid.uuid4()),
                "title": session.title,
                "state": session.state or {},
                "agentContext": session.agentContext or {},
                "messages": [],
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "lastAccessedAt": datetime.now().isoformat()
            }
            sessions.append(new_session)
        return new_session
    except FileLockError as e:
        logger.error(f"Lock error creating session: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - unable to acquire lock")
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/v1/dialog/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        sessions = load_sessions()
        session = next((s for s in sessions if s["id"] == session_id), None)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except FileLockError as e:
        logger.error(f"Lock error getting session: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - unable to acquire lock")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.post("/api/v1/dialog/sessions/{session_id}/messages")
async def add_message(session_id: str, message: DialogMessage):
    try:
        with atomic_session_operation() as sessions:
            session = next((s for s in sessions if s["id"] == session_id), None)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            
            message_dict = {
                "id": str(uuid.uuid4()),
                "role": message.role,
                "content": message.content,
                "reasoningSteps": message.reasoningSteps,
                "metadata": message.metadata,
                "timestamp": datetime.now().isoformat()
            }
            session["messages"].append(message_dict)
            session["updatedAt"] = datetime.now().isoformat()
        return message_dict
    except FileLockError as e:
        logger.error(f"Lock error adding message: {str(e)}")
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - unable to acquire lock")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")

# Campaigns
@app.get("/api/v1/campaigns")
async def list_campaigns():
    campaigns = load_json(f"{DATA_DIR}/campaigns.json")
    return campaigns

@app.post("/api/v1/campaigns")
async def create_campaign(campaign: CampaignCreate):
    campaigns = load_json(f"{DATA_DIR}/campaigns.json")
    new_campaign = {
        "id": str(uuid.uuid4()),
        "sessionId": campaign.sessionId,
        "name": campaign.name,
        "description": campaign.description,
        "goals": campaign.goals or [],
        "status": "draft",
        "schedule": campaign.schedule or {},
        "startDate": campaign.startDate,
        "endDate": campaign.endDate,
        "progress": campaign.progress or 0.0,
        "aiGeneratedConfig": {},
        "userFlowConfig": campaign.userFlowConfig or {},
        "estimatedAudienceSize": campaign.estimatedAudienceSize or 0,
        "segmentIds": campaign.segmentIds or [],
        "channels": campaign.channels,
        "variants": campaign.variants or [],
        "creatives": campaign.creatives or [],
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    campaigns.append(new_campaign)
    save_json(f"{DATA_DIR}/campaigns.json", campaigns)
    return new_campaign

@app.get("/api/v1/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str):
    campaigns = load_json(f"{DATA_DIR}/campaigns.json")
    campaign = next((c for c in campaigns if c["id"] == campaign_id), None)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign

@app.get("/api/v1/campaigns/{campaign_id}/metrics")
async def get_campaign_metrics(campaign_id: str):
    # Return mock metrics
    return {
        "campaignId": campaign_id,
        "delivered": 9500,
        "opened": 2850,
        "clicked": 1425,
        "converted": 285,
        "openRate": 30.0,
        "clickRate": 15.0,
        "conversionRate": 3.0,
        "variants": [
            {"variantId": "A", "conversionRate": 3.2},
            {"variantId": "B", "conversionRate": 2.8}
        ]
    }

# Search
@app.get("/api/v1/search")
async def search(q: str, type: str = "all"):
    results = []
    q_lower = q.lower()
    
    if type in ["all", "campaign"]:
        campaigns = load_json(f"{DATA_DIR}/campaigns.json")
        for campaign in campaigns:
            if q_lower in campaign.get("name", "").lower():
                results.append({
                    "id": campaign["id"],
                    "type": "campaign",
                    "title": campaign["name"],
                    "description": campaign.get("description", ""),
                    "relevance": 1.0
                })
    
    if type in ["all", "segment"]:
        segments = load_json(f"{DATA_DIR}/segments.json")
        for segment in segments:
            if q_lower in segment.get("name", "").lower():
                results.append({
                    "id": segment["id"],
                    "type": "segment",
                    "title": segment["name"],
                    "description": f"Size: {segment.get('size', 0)}",
                    "relevance": 1.0
                })
    
    if type in ["all", "knowledge"]:
        knowledge = load_json(f"{DATA_DIR}/knowledge.json")
        for article in knowledge:
            if q_lower in article.get("title", "").lower():
                results.append({
                    "id": article["id"],
                    "type": "knowledge",
                    "title": article["title"],
                    "description": article.get("content", "")[:100],
                    "relevance": 1.0
                })
    
    return results

# Segments
@app.get("/api/v1/segments")
async def list_segments():
    segments = load_json(f"{DATA_DIR}/segments.json")
    return segments

@app.post("/api/v1/segments")
async def create_segment(segment: SegmentCreate):
    segments = load_json(f"{DATA_DIR}/segments.json")
    new_segment = {
        "id": str(uuid.uuid4()),
        "name": segment.name,
        "filters": segment.filters,
        "size": 10000,  # mock
        "pastConversionRate": 0.03,
        "demographics": segment.demographics or {},
        "behaviors": segment.behaviors or {},
        "createdAt": datetime.now().isoformat()
    }
    segments.append(new_segment)
    save_json(f"{DATA_DIR}/segments.json", segments)
    return new_segment

# Knowledge
@app.get("/api/v1/knowledge")
async def list_knowledge():
    knowledge = load_json(f"{DATA_DIR}/knowledge.json")
    return knowledge

@app.post("/api/v1/knowledge")
async def create_knowledge(article: KnowledgeArticle):
    knowledge = load_json(f"{DATA_DIR}/knowledge.json")
    new_article = {
        "id": str(uuid.uuid4()),
        "title": article.title,
        "content": article.content,
        "articleType": article.articleType,
        "metadata": article.metadata or {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    knowledge.append(new_article)
    save_json(f"{DATA_DIR}/knowledge.json", knowledge)
    return new_article

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
