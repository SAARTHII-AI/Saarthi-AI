import json
import os
from typing import List, Dict, Any, Optional
from app.config import settings

def load_schemes(scheme_type: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
    filepath = settings.data_path
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        schemes = data.get("schemes", [])

    if scheme_type:
        schemes = [s for s in schemes if s.get("type", "").lower() == scheme_type.lower()]

    if state:
        state_lower = state.lower()
        schemes = [
            s for s in schemes
            if s.get("type") == "central" or (s.get("state") and s["state"].lower() == state_lower)
        ]

    return schemes
