import os
import sys
import json
import mimetypes
import urllib.request
import urllib.parse

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure python_backend is in path
backend_dir = os.path.join(BASE_DIR, "python_backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

try:
    try:
        from python_backend.ha_controller import DeviceTracker, SensorDataProcessor, AutomationDecisionEngine
    except ImportError:
        from ha_controller import DeviceTracker, SensorDataProcessor, AutomationDecisionEngine
    tracker = DeviceTracker()
    engine = AutomationDecisionEngine()
    processor = SensorDataProcessor()
except Exception:
    tracker = None


def handle_blynk_api(environ, start_response, path, method):
    """
    Server-side proxy for Blynk IoT REST API to eliminate browser CORS limitations.
    Supports reading virtual pins (GET) and updating virtual pins (POST).
    """
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type"),
    ]

    query_str = environ.get("QUERY_STRING", "")
    params = urllib.parse.parse_qs(query_str)
    token = params.get("token", [""])[0]
    server = params.get("server", ["https://blynk.cloud"])[0].rstrip("/")

    if method == "GET":
        if not token:
            start_response("400 Bad Request", headers)
            return [json.dumps({"error": "Missing Blynk Auth Token (?token=...)"}).encode("utf-8")]

        try:
            # 1. Check if hardware is connected
            hw_url = f"{server}/external/api/isHardwareConnected?token={token}"
            req_hw = urllib.request.Request(hw_url, headers={"User-Agent": "Haven-Blynk-Proxy"})
            with urllib.request.urlopen(req_hw, timeout=4) as resp:
                hw_raw = resp.read().decode("utf-8").strip()
                is_connected = hw_raw.lower() in ("true", "1")

            # 2. Get Virtual Pin values V0 through V9
            get_url = f"{server}/external/api/get?token={token}&v0&v1&v2&v3&v4&v5&v6&v7&v8&v9"
            req_pins = urllib.request.Request(get_url, headers={"User-Agent": "Haven-Blynk-Proxy"})
            with urllib.request.urlopen(req_pins, timeout=4) as resp:
                pins_data = json.loads(resp.read().decode("utf-8"))

            start_response("200 OK", headers)
            return [json.dumps({
                "status": "online",
                "blynk_connected": True,
                "hardware_connected": is_connected,
                "pins": pins_data
            }, indent=2).encode("utf-8")]
        except Exception as e:
            start_response("200 OK", headers)
            return [json.dumps({
                "status": "error",
                "blynk_connected": False,
                "hardware_connected": False,
                "message": f"Could not reach Blynk Cloud: {str(e)}"
            }).encode("utf-8")]

    elif method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0) or 0)
            body = environ["wsgi.input"].read(content_length).decode("utf-8")
            payload = json.loads(body) if body else {}

            token = payload.get("token") or token
            pin = str(payload.get("pin", "v0")).lower().replace("pin", "v")
            if not pin.startswith("v"):
                pin = f"v{pin}"
            value = payload.get("value", 0)
            server = payload.get("server") or server

            if not token:
                start_response("400 Bad Request", headers)
                return [json.dumps({"error": "Missing Blynk Auth Token in payload"}).encode("utf-8")]

            # Call Blynk update API: https://blynk.cloud/external/api/update?token={token}&{pin}={value}
            update_url = f"{server}/external/api/update?token={token}&{pin}={urllib.parse.quote(str(value))}"
            req_update = urllib.request.Request(update_url, headers={"User-Agent": "Haven-Blynk-Proxy"})
            with urllib.request.urlopen(req_update, timeout=4) as resp:
                resp_data = resp.read().decode("utf-8")

            # Also update local tracker state if applicable
            if tracker:
                if pin == "v0":
                    tracker.update("switch.living_room_light", "on" if value in (1, "1", True) else "off")
                elif pin == "v1":
                    tracker.update("switch.bedroom_light", "on" if value in (1, "1", True) else "off")
                elif pin == "v2":
                    tracker.update("switch.living_room_fan", "on" if value in (1, "1", True) else "off")

            start_response("200 OK", headers)
            return [json.dumps({
                "status": "success",
                "pin": pin,
                "value": value,
                "blynk_response": resp_data
            }).encode("utf-8")]
        except Exception as e:
            start_response("500 Internal Server Error", headers)
            return [json.dumps({"error": f"Blynk update failed: {str(e)}"}).encode("utf-8")]

    start_response("405 Method Not Allowed", headers)
    return [b"405 Method Not Allowed"]


def app(environ, start_response):
    """
    Universal WSGI Application for Vercel.
    Serves the HAVEN spatial dashboard at / and /haven,
    provides JSON telemetry at /api, and proxies Blynk IoT at /api/blynk.
    """
    path = environ.get("PATH_INFO", "/") or "/"
    method = environ.get("REQUEST_METHOD", "GET")

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

    # 1. Blynk IoT Integration Proxy Endpoint
    if path.startswith("/api/blynk"):
        return handle_blynk_api(environ, start_response, path, method)

    # 2. General IoT Telemetry API Endpoints
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
            "blynk_support": True,
            "blynk_endpoint": "/api/blynk",
            "system_data": data,
        }
        return [json.dumps(payload, indent=2).encode("utf-8")]

    # 3. Main Dashboard (/)
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

    # 4. Haven Dashboard (/haven)
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

    # 5. Fallback Static File Lookup
    possible_file = os.path.join(BASE_DIR, clean_path)
    if os.path.isfile(possible_file):
        mime, _ = mimetypes.guess_type(possible_file)
        mime = mime or "application/octet-stream"
        status = "200 OK"
        headers = [("Content-Type", mime)]
        start_response(status, headers)
        with open(possible_file, "rb") as f:
            return [f.read()]

    # 6. Fallback 404
    status = "404 Not Found"
    headers = [("Content-Type", "text/plain; charset=utf-8")]
    start_response(status, headers)
    return [b"404 Not Found"]


application = app
handler = app

if __name__ == "__main__":
    from wsgiref.simple_server import make_server
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting local server at http://localhost:{port}")
    server = make_server("0.0.0.0", port, app)
    server.serve_forever()
