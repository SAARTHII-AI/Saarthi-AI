import sys
import os

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "backend"))
os.chdir(os.path.join(WORKSPACE_ROOT, "backend"))

os.environ["SAARTHI_FRONTEND_DIR"] = os.path.join(WORKSPACE_ROOT, "frontend")

import uvicorn
from app.main import app

port = int(os.environ.get("PORT", 80))
print(f"Starting SaarthiAI on port {port}...")
uvicorn.run(app, host="0.0.0.0", port=port)
