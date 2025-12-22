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

app = FastAPI(title="AI-native Campaign Orchestrator API", version="1.0.0")

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
    goal: str
    segmentId: Optional[str] = None
    estimatedAudienceSize: Optional[int] = None
    schedule: Optional[Dict] = None
    userFlowConfig: Optional[Dict] = None
    channels: List[str] = []
    variants: Optional[List[Dict]] = None
    sessionId: Optional[str] = None

class CompendiumArticle(BaseModel):
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

# Agent Orchestration Engine
class AgentOrchestrator:
    def __init__(self):
        self.agents = {
            "campaign_generation": CampaignGenerationAgent(),
            "campaign_analysis": CampaignAnalysisAgent(),
        }
    
    def route_intent(self, prompt: str) -> str:
        """Classify user intent and route to appropriate agent"""
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["create", "generate", "new campaign", "campaign"]):
            return "campaign_generation"
        elif any(word in prompt_lower for word in ["analyze", "review", "performance"]):
            return "campaign_analysis"
        return "campaign_generation"  # default
    
    def process(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        intent = self.route_intent(prompt)
        agent = self.agents[intent]
        return agent.process(prompt, context)

class CampaignGenerationAgent:
    def process(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        """Generate campaign configuration based on prompt"""
        # Load historical data for analysis
        campaigns = load_json(f"{DATA_DIR}/campaigns.json")
        segments = load_json(f"{DATA_DIR}/segments.json")
        
        # Simulate AI analysis
        reasoning_steps = [
            {"step": "Intent Classification", "result": "Campaign creation request identified"},
            {"step": "Historical Analysis", "result": f"Analyzed {len(campaigns)} historical campaigns"},
            {"step": "Audience Research", "result": f"Evaluated {len(segments)} available segments"},
            {"step": "Optimal Configuration", "result": "Generated campaign configuration based on best practices"}
        ]
        
        # Generate campaign configuration
        campaign_config = {
            "name": self._extract_campaign_name(prompt),
            "description": "AI-generated campaign based on your requirements",
            "goal": self._infer_goal(prompt),
            "channels": self._infer_channels(prompt),
            "estimatedAudienceSize": 10000,
            "schedule": {"type": "immediate"},
            "userFlowConfig": {
                "flowType": "sequential",
                "steps": self._generate_user_flow(prompt)
            },
            "variants": [
                {"name": "Variant A", "splitPercentage": 50.0, "content": {}},
                {"name": "Variant B", "splitPercentage": 50.0, "content": {}}
            ]
        }
        
        proposal = f"""
Based on your request: "{prompt}"

I've analyzed historical campaign data and audience segments to recommend the following optimal configuration:

**Campaign Strategy:**
- Goal: {campaign_config['goal']}
- Channels: {', '.join(campaign_config['channels'])}
- Estimated Reach: {campaign_config['estimatedAudienceSize']:,} users
- Flow Type: {campaign_config['userFlowConfig']['flowType']}

**Why this configuration:**
- Historical campaigns with similar goals showed 15-20% higher conversion with multi-channel approach
- Sequential flow allows for progressive engagement
- A/B testing with 50/50 split provides statistical significance

You can review and edit the configuration in the Experience Panel.
        """.strip()
        
        return {
            "agent": "CampaignGenerationAgent",
            "reasoningSteps": reasoning_steps,
            "proposal": proposal,
            "campaignConfig": campaign_config,
            "experiencePanelType": "campaign_form"
        }
    
    def _extract_campaign_name(self, prompt: str) -> str:
        # Simple extraction - in production would use NLP
        if "campaign" in prompt.lower():
            return prompt[:50] + " Campaign"
        return "New Campaign"
    
    def _infer_goal(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "purchase" in prompt_lower or "buy" in prompt_lower:
            return "purchase"
        elif "session" in prompt_lower or "visit" in prompt_lower:
            return "start_session"
        elif "open" in prompt_lower:
            return "open_message"
        return "custom_event"
    
    def _infer_channels(self, prompt: str) -> List[str]:
        channels = []
        prompt_lower = prompt.lower()
        if "email" in prompt_lower:
            channels.append("email")
        if "sms" in prompt_lower or "text" in prompt_lower:
            channels.append("sms")
        if "push" in prompt_lower or "notification" in prompt_lower:
            channels.append("push")
        return channels if channels else ["email", "sms"]  # default
    
    def _generate_user_flow(self, prompt: str) -> List[Dict]:
        return [
            {"stepType": "email", "channel": "email", "order": 1},
            {"stepType": "sms", "channel": "sms", "order": 2, "condition": "if_email_opened"}
        ]

class CampaignAnalysisAgent:
    def process(self, prompt: str, context: Optional[Dict] = None) -> Dict:
        return {
            "agent": "CampaignAnalysisAgent",
            "reasoningSteps": [{"step": "Analysis", "result": "Campaign performance analyzed"}],
            "proposal": "Analysis results would be displayed here",
            "experiencePanelType": "analysis_view"
        }

orchestrator = AgentOrchestrator()

# API Endpoints

@app.get("/")
async def root():
    return {"message": "AI-native Campaign Orchestrator API", "version": "1.0.0"}

# Agent Orchestration
@app.post("/api/v1/agent/orchestrate")
async def orchestrate_agent(request: Dict[str, Any]):
    prompt = request.get("prompt", "")
    context = request.get("context", {})
    session_id = request.get("sessionId")
    
    result = orchestrator.process(prompt, context)
    
    # Store in dialog session if sessionId provided
    if session_id:
        sessions = load_json(f"{DATA_DIR}/dialog_sessions.json")
        session = next((s for s in sessions if s["id"] == session_id), None)
        if session:
            message = {
                "id": str(uuid.uuid4()),
                "role": "user",
                "content": prompt,
                "timestamp": datetime.now().isoformat()
            }
            session["messages"].append(message)
            
            assistant_message = {
                "id": str(uuid.uuid4()),
                "role": "assistant",
                "content": result["proposal"],
                "reasoningSteps": result["reasoningSteps"],
                "timestamp": datetime.now().isoformat()
            }
            session["messages"].append(assistant_message)
            session["updatedAt"] = datetime.now().isoformat()
            save_json(f"{DATA_DIR}/dialog_sessions.json", sessions)
    
    return result

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
        "goal": campaign.goal,
        "status": "draft",
        "schedule": campaign.schedule or {},
        "aiGeneratedConfig": {},
        "userFlowConfig": campaign.userFlowConfig or {},
        "estimatedAudienceSize": campaign.estimatedAudienceSize or 0,
        "segmentId": campaign.segmentId,
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
    
    if type in ["all", "compendium"]:
        compendium = load_json(f"{DATA_DIR}/compendium.json")
        for article in compendium:
            if q_lower in article.get("title", "").lower():
                results.append({
                    "id": article["id"],
                    "type": "compendium",
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

# Compendium
@app.get("/api/v1/compendium")
async def list_compendium():
    compendium = load_json(f"{DATA_DIR}/compendium.json")
    return compendium

@app.post("/api/v1/compendium")
async def create_compendium(article: CompendiumArticle):
    compendium = load_json(f"{DATA_DIR}/compendium.json")
    new_article = {
        "id": str(uuid.uuid4()),
        "title": article.title,
        "content": article.content,
        "articleType": article.articleType,
        "metadata": article.metadata or {},
        "createdAt": datetime.now().isoformat(),
        "updatedAt": datetime.now().isoformat()
    }
    compendium.append(new_article)
    save_json(f"{DATA_DIR}/compendium.json", compendium)
    return new_article

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
