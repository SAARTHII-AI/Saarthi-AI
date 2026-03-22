import subprocess
import sys
import os
import signal
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import urllib.error

BACKEND_URL = "http://localhost:8000"
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")


class ProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/query") or self.path.startswith("/health") or self.path.startswith("/schemes") or self.path.startswith("/help-centers") or self.path.startswith("/api/"):
            self._proxy_request("GET")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/query") or self.path.startswith("/health") or self.path.startswith("/schemes") or self.path.startswith("/help-centers") or self.path.startswith("/api/"):
            self._proxy_request("POST")
        else:
            self.send_error(405, "Method Not Allowed")

    def _proxy_request(self, method):
        path = self.path
        # Ensure API paths have trailing slash so FastAPI doesn't 307-redirect
        for prefix in ("/query", "/health", "/schemes", "/help-centers"):
            if path == prefix or path.startswith(prefix + "?"):
                path = prefix + "/" + path[len(prefix):]
                break
        target_url = BACKEND_URL + path
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(
            target_url,
            data=body,
            method=method,
            headers={
                "Content-Type": self.headers.get("Content-Type", "application/json"),
                "Accept-Encoding": self.headers.get("Accept-Encoding", "gzip, deflate"),
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=55) as response:
                self.send_response(response.status)
                for header, value in response.headers.items():
                    if header.lower() not in ("transfer-encoding", "connection"):
                        self.send_header(header, value)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, f"Backend unavailable: {e}")

    def log_message(self, format, *args):
        pass


def start_backend():
    backend_dir = os.path.join(os.path.dirname(__file__), "backend")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "localhost", "--port", "8000"],
        cwd=backend_dir
    )
    return proc


def main():
    print("Starting SaarthiAI backend on port 8000...")
    backend_proc = start_backend()

    print("Waiting for backend to start...")
    time.sleep(3)

    port = int(os.environ.get("PORT", 5000))
    print(f"Starting frontend proxy server on port {port}...")
    server = HTTPServer(("0.0.0.0", port), ProxyHandler)

    def shutdown(signum, frame):
        print("Shutting down...")
        backend_proc.terminate()
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    print(f"SaarthiAI is running at http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
