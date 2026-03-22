import sys
import os

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(WORKSPACE_ROOT, "backend"))

os.environ["SAARTHI_FRONTEND_DIR"] = os.path.join(WORKSPACE_ROOT, "frontend")

from app.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, host="0.0.0.0", port=port)
