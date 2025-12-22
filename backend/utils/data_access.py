"""
Data access layer for tool calling
Provides functions to query campaigns, segments, and metrics from JSON files
"""
import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

# Get the backend directory (parent of utils)
BACKEND_DIR = Path(__file__).parent.parent
DATA_DIR = BACKEND_DIR / "data"

def load_json(filepath: str) -> Any:
    """Load JSON data from file"""
    full_path = DATA_DIR / filepath
    if full_path.exists():
        with open(full_path, 'r') as f:
            return json.load(f)
    return []

def get_campaigns(filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """
    Retrieve historical campaigns with optional filters
    
    Args:
        filters: Dict with optional keys:
            - goal: Filter by campaign goal
            - status: Filter by status (active, completed, draft)
            - limit: Maximum number of campaigns to return
    
    Returns:
        List of campaign dictionaries
    """
    campaigns = load_json("campaigns.json")
    
    if not filters:
        return campaigns
    
    filtered = campaigns
    
    # Filter by goal
    if "goal" in filters and filters["goal"]:
        goal_filter = filters["goal"].lower()
        filtered = [
            c for c in filtered
            if goal_filter in str(c.get("goals", [])).lower()
        ]
    
    # Filter by status
    if "status" in filters and filters["status"]:
        status_filter = filters["status"].lower()
        filtered = [
            c for c in filtered
            if c.get("status", "").lower() == status_filter
        ]
    
    # Apply limit
    if "limit" in filters and filters["limit"]:
        filtered = filtered[:filters["limit"]]
    
    return filtered

def get_segments(filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """
    Retrieve audience segments with optional filters
    
    Args:
        filters: Dict with optional keys:
            - name: Filter by segment name (fuzzy match)
            - min_conversion_rate: Minimum conversion rate
            - limit: Maximum number of segments to return
    
    Returns:
        List of segment dictionaries
    """
    segments = load_json("segments.json")
    
    if not filters:
        return segments
    
    filtered = segments
    
    # Filter by name (fuzzy match)
    if "name" in filters and filters["name"]:
        name_filter = filters["name"].lower()
        filtered = [
            s for s in filtered
            if name_filter in s.get("name", "").lower()
        ]
    
    # Filter by conversion rate
    if "min_conversion_rate" in filters and filters["min_conversion_rate"] is not None:
        min_rate = float(filters["min_conversion_rate"])
        filtered = [
            s for s in filtered
            if s.get("pastConversionRate", 0) >= min_rate
        ]
    
    # Apply limit
    if "limit" in filters and filters["limit"]:
        filtered = filtered[:filters["limit"]]
    
    return filtered

def get_campaign_metrics(campaign_id: str) -> Dict[str, Any]:
    """
    Get performance metrics for a specific campaign
    
    Args:
        campaign_id: Campaign ID
    
    Returns:
        Dict with campaign metrics (mock data for POC)
    """
    campaigns = load_json("campaigns.json")
    campaign = next((c for c in campaigns if c.get("id") == campaign_id), None)
    
    if not campaign:
        return {"error": "Campaign not found"}
    
    # Return mock metrics for POC
    return {
        "campaign_id": campaign_id,
        "delivered": 10000,
        "opened": 3500,
        "clicked": 1200,
        "converted": 450,
        "open_rate": 0.35,
        "click_rate": 0.12,
        "conversion_rate": 0.045
    }

def search_campaigns(query: str) -> List[Dict]:
    """Search campaigns by query string"""
    campaigns = load_json("campaigns.json")
    query_lower = query.lower()
    
    results = [
        c for c in campaigns
        if query_lower in c.get("name", "").lower()
        or query_lower in c.get("description", "").lower()
    ]
    
    return results

def search_segments(query: str) -> List[Dict]:
    """Search segments by query string"""
    segments = load_json("segments.json")
    query_lower = query.lower()
    
    results = [
        s for s in segments
        if query_lower in s.get("name", "").lower()
        or query_lower in str(s.get("filters", {})).lower()
    ]
    
    return results

def search_knowledge(query: str) -> List[Dict]:
    """Search knowledge articles by query string"""
    knowledge = load_json("knowledge.json")
    query_lower = query.lower()
    
    results = [
        k for k in knowledge
        if query_lower in k.get("title", "").lower()
        or query_lower in k.get("content", "").lower()
    ]
    
    return results

