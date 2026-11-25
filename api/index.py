from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import urllib.request
import urllib.parse

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
except Exception:
    HAS_BACKEND = False
    tracker = None


class handler(BaseHTTPRequestHandler):
    def send_cors_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', f'{content_type}; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self.send_cors_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        # 1. Blynk Proxy GET Endpoint: /api/blynk?token=...
        if 'blynk' in path:
            token = query.get('token', [''])[0]
            server = query.get('server', ['https://blynk.cloud'])[0].rstrip('/')

            if not token:
                self.send_cors_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing Blynk Auth Token (?token=...)'}).encode('utf-8'))
                return

            try:
                # 1. Check if hardware is connected
                hw_url = f"{server}/external/api/isHardwareConnected?token={token}"
                req_hw = urllib.request.Request(hw_url, headers={'User-Agent': 'Haven-Blynk-Proxy'})
                with urllib.request.urlopen(req_hw, timeout=4) as resp:
                    hw_raw = resp.read().decode('utf-8').strip()
                    is_connected = hw_raw.lower() in ('true', '1')

                # 2. Get Virtual Pin values V0 through V9
                get_url = f"{server}/external/api/get?token={token}&v0&v1&v2&v3&v4&v5&v6&v7&v8&v9"
                req_pins = urllib.request.Request(get_url, headers={'User-Agent': 'Haven-Blynk-Proxy'})
                with urllib.request.urlopen(req_pins, timeout=4) as resp:
                    pins_data = json.loads(resp.read().decode('utf-8'))

                self.send_cors_headers(200)
                result = {
                    'status': 'online',
                    'blynk_connected': True,
                    'hardware_connected': is_connected,
                    'pins': pins_data
                }
                self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
                return
            except Exception as e:
                self.send_cors_headers(200)
                result = {
                    'status': 'error',
                    'blynk_connected': False,
                    'hardware_connected': False,
                    'message': f"Could not reach Blynk Cloud: {str(e)}"
                }
                self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
                return

        # 2. General System Telemetry Endpoint
        self.send_cors_headers(200)

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
            "blynk_support": True,
            "blynk_endpoint": "/api/blynk",
            "dashboard_url": "/",
            "system_data": data
        }

        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        return

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else ''
        
        try:
            payload = json.loads(post_data) if post_data else {}
        except Exception:
            payload = {}

        # 1. Blynk Proxy POST Endpoint: /api/blynk (to update virtual pins)
        if 'blynk' in path:
            token = payload.get('token')
            pin = str(payload.get('pin', 'v0')).lower().replace('pin', 'v')
            if not pin.startswith('v'):
                pin = f"v{pin}"
            value = payload.get('value', 0)
            server = (payload.get('server') or 'https://blynk.cloud').rstrip('/')

            if not token:
                self.send_cors_headers(400)
                self.wfile.write(json.dumps({'error': 'Missing Blynk Auth Token in payload'}).encode('utf-8'))
                return

            try:
                update_url = f"{server}/external/api/update?token={token}&{pin}={urllib.parse.quote(str(value))}"
                req_update = urllib.request.Request(update_url, headers={'User-Agent': 'Haven-Blynk-Proxy'})
                with urllib.request.urlopen(req_update, timeout=4) as resp:
                    resp_data = resp.read().decode('utf-8')

                if HAS_BACKEND and tracker:
                    if pin == 'v0':
                        tracker.update('switch.living_room_light', 'on' if value in (1, '1', True) else 'off')
                    elif pin == 'v1':
                        tracker.update('switch.bedroom_light', 'on' if value in (1, '1', True) else 'off')
                    elif pin == 'v2':
                        tracker.update('switch.living_room_fan', 'on' if value in (1, '1', True) else 'off')

                self.send_cors_headers(200)
                result = {
                    'status': 'success',
                    'pin': pin,
                    'value': value,
                    'blynk_response': resp_data
                }
                self.wfile.write(json.dumps(result, indent=2).encode('utf-8'))
                return
            except Exception as e:
                self.send_cors_headers(500)
                self.wfile.write(json.dumps({'error': f'Blynk update failed: {str(e)}'}).encode('utf-8'))
                return

        # 2. General Command Handler
        self.send_cors_headers(200)
        response = {
            "status": "received",
            "action": payload.get("action", "query"),
            "result": "Command processed successfully"
        }
        self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))
        return
