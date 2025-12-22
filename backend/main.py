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

# Import new orchestration system
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from orchestration.orchestrator import AgentOrchestrator
import logging

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
    
    try:
        # Use new orchestration system
        result = orchestrator.orchestrate(prompt, context, session_id)
        
        # Store in dialog session if sessionId provided
        if session_id:
            sessions = load_json(f"{DATA_DIR}/dialog_sessions.json")
            session = next((s for s in sessions if s["id"] == session_id), None)
            if session:
                # Add user message
                message = {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": prompt,
                    "timestamp": datetime.now().isoformat()
                }
                session["messages"].append(message)
                
                # Add assistant message
                proposal = result.get("campaignConfig", {}).get("name", "Response generated")
                if isinstance(result.get("campaignConfig"), dict):
                    proposal = f"Generated campaign: {result.get('campaignConfig', {}).get('name', 'Campaign')}"
                elif isinstance(result.get("campaignConfig"), list):
                    proposal = f"Found {len(result.get('campaignConfig', []))} results"
                else:
                    proposal = "Analysis completed"
                
                assistant_message = {
                    "id": str(uuid.uuid4()),
                    "role": "assistant",
                    "content": proposal,
                    "reasoningSteps": result.get("reasoningSteps", []),
                    "timestamp": datetime.now().isoformat()
                }
                session["messages"].append(assistant_message)
                session["updatedAt"] = datetime.now().isoformat()
                save_json(f"{DATA_DIR}/dialog_sessions.json", sessions)
        
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
    sessions = load_json(f"{DATA_DIR}/dialog_sessions.json")
    return sessions

@app.post("/api/v1/dialog/sessions")
async def create_session(session: DialogSession):
    sessions = load_json(f"{DATA_DIR}/dialog_sessions.json")
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
    save_json(f"{DATA_DIR}/dialog_sessions.json", sessions)
    return new_session

@app.get("/api/v1/dialog/sessions/{session_id}")
async def get_session(session_id: str):
    sessions = load_json(f"{DATA_DIR}/dialog_sessions.json")
    session = next((s for s in sessions if s["id"] == session_id), None)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@app.post("/api/v1/dialog/sessions/{session_id}/messages")
async def add_message(session_id: str, message: DialogMessage):
    sessions = load_json(f"{DATA_DIR}/dialog_sessions.json")
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
    save_json(f"{DATA_DIR}/dialog_sessions.json", sessions)
    return message_dict

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
