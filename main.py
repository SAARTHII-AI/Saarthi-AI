import sys
import os

WORKSPACE_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(WORKSPACE_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
os.chdir(BACKEND_DIR)

os.environ["SAARTHI_FRONTEND_DIR"] = os.path.join(WORKSPACE_ROOT, "frontend")

from app.main import app  # noqa: E402

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 80))
    print(f"Starting SaarthiAI on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
