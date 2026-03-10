import json
import os
from app.config import settings

def load_schemes():
    filepath = settings.data_path
    if not os.path.exists(filepath):
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("schemes", [])
