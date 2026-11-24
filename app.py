import os
import sys
import json
import mimetypes

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure python_backend is in path
backend_dir = os.path.join(BASE_DIR, "python_backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    from ha_controller import DeviceTracker, SensorDataProcessor, AutomationDecisionEngine
    tracker = DeviceTracker()
    engine = AutomationDecisionEngine()
    processor = SensorDataProcessor()
except Exception:
    tracker = None


def app(environ, start_response):
    """
    Universal WSGI Application for Vercel.
    Serves the HAVEN spatial dashboard at / and /haven,
    and provides JSON telemetry at /api.
    """
    path = environ.get("PATH_INFO", "/") or "/"
    method = environ.get("REQUEST_METHOD", "GET")

    # Normalize path
    clean_path = path.strip("/")

    # Handle CORS Preflight
    if method == "OPTIONS":
        status = "200 OK"
        headers = [
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
            ("Access-Control-Allow-Headers", "Content-Type"),
        ]
        start_response(status, headers)
        return [b""]

    # 1. API Endpoints
    if path.startswith("/api"):
        status = "200 OK"
        headers = [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Access-Control-Allow-Origin", "*"),
        ]
        start_response(status, headers)

        if tracker:
            data = tracker.get_summary()
        else:
            data = {
                "total_appliances": 3,
                "active_appliances": 0,
                "temperature": 24.5,
                "humidity": 52.0,
                "motion": "off",
                "mode": "Auto",
            }

        payload = {
            "status": "online",
            "message": "Home Automation Backend running on Vercel",
            "system_data": data,
        }
        return [json.dumps(payload, indent=2).encode("utf-8")]

    # 2. Main Dashboard (/)
    if path in ("/", "/index", "/index.html"):
        filepath = os.path.join(BASE_DIR, "index.html")
        if os.path.isfile(filepath):
            status = "200 OK"
            headers = [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Cache-Control", "public, max-age=3600"),
            ]
            start_response(status, headers)
            with open(filepath, "rb") as f:
                return [f.read()]

    # 3. Haven Dashboard (/haven)
    if path in ("/haven", "/haven.html"):
        filepath = os.path.join(BASE_DIR, "haven.html")
        if os.path.isfile(filepath):
            status = "200 OK"
            headers = [
                ("Content-Type", "text/html; charset=utf-8"),
                ("Cache-Control", "public, max-age=3600"),
            ]
            start_response(status, headers)
            with open(filepath, "rb") as f:
                return [f.read()]

    # 4. Fallback Static File Lookup
    possible_file = os.path.join(BASE_DIR, clean_path)
    if os.path.isfile(possible_file):
        mime, _ = mimetypes.guess_type(possible_file)
        mime = mime or "application/octet-stream"
        status = "200 OK"
        headers = [("Content-Type", mime)]
        start_response(status, headers)
        with open(possible_file, "rb") as f:
            return [f.read()]

    # 5. Fallback 404
    status = "404 Not Found"
    headers = [("Content-Type", "text/plain; charset=utf-8")]
    start_response(status, headers)
    return [b"404 Not Found"]


# Aliases for various WSGI/ASGI/Vercel serverless conventions
application = app
handler = app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting local server at http://localhost:{port}")
    server = make_server("0.0.0.0", port, app)
    server.serve_forever()
