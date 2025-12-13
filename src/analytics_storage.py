"""
FinEdge Analytics Storage v1.0
JSON-based persistent storage for document analytics.
Stores analytics results so they can be retrieved without regeneration.
"""

import json
import os
from typing import Optional, Dict, List
from datetime import datetime

ANALYTICS_PATH = "vectorstore/analytics_cache.json"


def _ensure_dir():
    """Ensure the vectorstore directory exists."""
    os.makedirs(os.path.dirname(ANALYTICS_PATH), exist_ok=True)


def load_all_analytics() -> Dict:
    """Load all stored analytics."""
    if os.path.exists(ANALYTICS_PATH):
        try:
            with open(ANALYTICS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_analytics(doc_id: str, analytics: Dict) -> None:
    """
    Save analytics for a document.
    
    Args:
        doc_id: Unique document identifier
        analytics: Analytics result dictionary
    """
    _ensure_dir()
    data = load_all_analytics()
    
    # Add metadata
    analytics_entry = {
        "analytics": analytics,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    data[doc_id] = analytics_entry
    
    with open(ANALYTICS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_analytics(doc_id: str) -> Optional[Dict]:
    """
    Retrieve stored analytics for a document.
    
    Args:
        doc_id: Unique document identifier
        
    Returns:
        Analytics dictionary or None if not found
    """
    data = load_all_analytics()
    entry = data.get(doc_id)
    if entry:
        return entry.get("analytics")
    return None


def has_analytics(doc_id: str) -> bool:
    """Check if analytics exist for a document."""
    data = load_all_analytics()
    return doc_id in data


def delete_analytics(doc_id: str) -> bool:
    """
    Delete stored analytics for a document.
    
    Returns:
        True if deleted, False if not found
    """
    data = load_all_analytics()
    if doc_id in data:
        del data[doc_id]
        with open(ANALYTICS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    return False


def clear_all_analytics() -> None:
    """Delete all stored analytics."""
    if os.path.exists(ANALYTICS_PATH):
        os.remove(ANALYTICS_PATH)


def list_documents_with_analytics() -> List[str]:
    """Get list of document IDs that have stored analytics."""
    data = load_all_analytics()
    return list(data.keys())


def get_analytics_metadata(doc_id: str) -> Optional[Dict]:
    """Get metadata about stored analytics (creation time, etc.)."""
    data = load_all_analytics()
    entry = data.get(doc_id)
    if entry:
        return {
            "created_at": entry.get("created_at"),
            "updated_at": entry.get("updated_at")
        }
    return None
