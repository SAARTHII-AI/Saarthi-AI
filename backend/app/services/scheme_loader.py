import json
import os
from typing import List, Dict, Any, Optional
from app.config import settings


def _normalize_scheme(s: Dict[str, Any]) -> Dict[str, Any]:
    if "scope" in s and "type" not in s:
        s["type"] = s["scope"]
    if "states" in s and "state" not in s:
        states = s.get("states") or []
        s["state"] = states[0] if states else None
    if "application_url" in s:
        links = list(s.get("documents_links") or [])
        url = s["application_url"]
        if url and url.startswith("http") and url not in links:
            links.insert(0, url)
        s["documents_links"] = links
    return s


def load_schemes(scheme_type: Optional[str] = None, state: Optional[str] = None) -> List[Dict[str, Any]]:
    filepath = settings.data_path
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        schemes = [_normalize_scheme(s) for s in data.get("schemes", [])]

    if scheme_type:
        schemes = [s for s in schemes if s.get("type", "").lower() == scheme_type.lower()]

    if state:
        state_lower = state.lower()
        schemes = [
            s for s in schemes
            if s.get("type") == "central" or (s.get("state") and s["state"].lower() == state_lower)
        ]

    return schemes
