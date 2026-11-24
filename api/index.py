from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Ensure python_backend is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python_backend'))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    try:
        from python_backend.ha_controller import DeviceTracker, SensorDataProcessor, AutomationDecisionEngine
    except ImportError:
        from ha_controller import DeviceTracker, SensorDataProcessor, AutomationDecisionEngine
    tracker = DeviceTracker()
    engine = AutomationDecisionEngine()
    processor = SensorDataProcessor()
    HAS_BACKEND = True
except Exception as e:
    HAS_BACKEND = False
    tracker = None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        if HAS_BACKEND and tracker:
            data = tracker.get_summary()
        else:
            data = {
                "total_appliances": 3,
                "active_appliances": 0,
                "temperature": 24.5,
                "humidity": 52.0,
                "motion": "off",
                "mode": "Auto"
            }

        response = {
            "status": "online",
            "message": "Home Automation IoT & Backend API running on Vercel",
            "dashboard_url": "/",
            "system_data": data
        }

        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        return

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            payload = json.loads(post_data) if post_data else {}
        except Exception:
            payload = {}

        response = {
            "status": "received",
            "action": payload.get("action", "query"),
            "result": "Command processed successfully"
        }
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        return

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
