import asyncio
import json
import websockets
from datetime import datetime, timezone
import random
import urllib.request
import urllib.error
import time

def make_request(url, method="GET", data=None, headers=None):
    if headers is None:
        headers = {}
    
    req = urllib.request.Request(url, method=method, headers=headers)
    if data:
        req.data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
        
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Request to {url} failed: {e}")
        raise

async def main():
    # Wait for server to be ready
    print("Waiting for server...")
    await asyncio.sleep(2)

    # 1. Ensure user exists (login)
    try:
        print("Logging in (mock)...")
        make_request(
            "http://127.0.0.1:8000/api/v1/users/me",
            headers={"Authorization": "Bearer mock_dashboard_user"}
        )
        print("Login successful.")
    except Exception as e:
        print(f"Login failed (will try to proceed): {e}")

    # 2. Register device to user so dashboard receives data
    try:
        print("Registering device...")
        make_request(
            "http://127.0.0.1:8000/api/v1/devices",
            method="POST",
            data={"device_id": "helmet-pi-01", "model_name": "Mock Pi"},
            headers={"Authorization": "Bearer mock_dashboard_user"}
        )
        print("Device registered.")
    except Exception as e:
        print(f"Registration failed: {e}")

    # 3. Send trip_start
    uri = "ws://127.0.0.1:8000/ws/ingest"
    print(f"Connecting to {uri}...")
    async with websockets.connect(uri, max_size=64 * 1024) as ws:
        # Send trip_start
        start_msg = {
            "type": "trip_start",
            "device_id": "helmet-pi-01",
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        await ws.send(json.dumps(start_msg))
        print(f"Sent trip_start: {await ws.recv()}")

        # 4. Send telemetry
        while True:
            # "01/01/2025 12:30:55"
            ts_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S")
            
            msg = {
                "ts": ts_str,
                "type": "telemetry",
                "device_id": "helmet-pi-01",
                "helmet_on": True,
                "heart_rate": { 
                    "ok": True, 
                    "ir": 55321, 
                    "red": 24123, 
                    "finger": True, 
                    "hr": int(random.uniform(70, 120)), 
                    "spo2": 97 
                },
                "imu": { 
                    "ok": True, 
                    "sleep": False, 
                    "ax": random.uniform(-0.5, 0.5), 
                    "ay": random.uniform(-0.5, 0.5), 
                    "az": random.uniform(9.0, 10.0), 
                    "gx": 2.0, 
                    "gy": 3.0, 
                    "gz": 4.0 
                },
                "gps": { 
                    "ok": True, 
                    "lat": 33.8547 + random.uniform(-0.001, 0.001), 
                    "lng": 35.8623 + random.uniform(-0.001, 0.001), 
                    "alt": 12.3, 
                    "sats": 8, 
                    "lock": True 
                },
                "crash_flag": False
            }
            await ws.send(json.dumps(msg))
            resp = await ws.recv()
            print(f"Sent: {resp}")
            await asyncio.sleep(0.2) # 2 Hz

asyncio.run(main())
