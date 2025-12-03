🪖 Smart Helmet Backend

Backend system for a real-time motorcycle safety helmet using FastAPI, WebSockets, ML inference, and SQLite/MySQL.

This service receives telemetry from the helmet (via Raspberry Pi → mobile app → backend), stores trip data, and streams live updates to the user dashboard. It also includes background workers for data persistence and (later) machine-learning-based crash detection.

📁 Project Structure
smart_helmet_backend/
│
├── app/
│   ├── main.py                 # FastAPI app entrypoint (REST + WebSockets + workers)
│   │
│   ├── models/
│   │   ├── db_models.py        # SQLAlchemy ORM models (Device, Telemetry, Trip, etc.)
│   │   └── schemas.py          # Pydantic request/response models
│   │
│   ├── database/
│   │   └── connection.py       # Async SQLAlchemy engine + session management
│   │
│   ├── workers/
│   │   ├── persist_worker.py   # Background queue → writes telemetry & trips to DB
│   │   └── inference_worker.py # (Later) ML inference worker for crash detection
│   │
│   ├── ml/
│   │   ├── model.onnx          # Placeholder for trained crash-detection model
│   │   └── predictor.py        # Loads/executes ONNX model
│   │
│   ├── services/
│   │   ├── connection_manager.py # Manages connected WebSocket clients
│   │   └── broadcaster.py        # Sends real-time data to subscribed users
│   │
│   ├── api/
│   │   └── api_router.py       # Organized API endpoints (/api/v1)
│   │
│   ├── static/
│   │   └── dashboard.html      # Simple WebSocket-powered debug dashboard
│   │
│   └── mock_sender.py          # Script that simulates telemetry packets
│
├── helmet.db                   # Local SQLite database (auto-created)
├── .env                        # Optional: DATABASE_URL, Firebase keys, model paths
└── README.md

🚀 Features
Real-time ingest pipeline

/ws/ingest receives live telemetry:

GPS location

Speed

Acceleration / gyroscope data

Heart rate (planned)

Stress levels (planned)

Crash detection signals (via ML, planned)

Telemetry is validated using Pydantic models, queued, stored, and broadcast to the user.

Real-time dashboard updates

/ws/stream pushes live updates to the authenticated user.

Useful for:

Live map tracking

Live speed & sensor data

Crash alerts

Trip progress

Works with the included static/dashboard.html test page.

Background workers

Two async workers run alongside FastAPI:

Persist Worker

Writes telemetry & trip events to the database.

Prevents slowing down WebSocket handling.

Inference Worker (future)

Loads ONNX ML model.

Detects crash probability based on incoming telemetry.

Sends live alerts through the broadcast manager.

Database flexibility

Supports both:

SQLite (default for local development)

MySQL / Postgres (production-ready via DATABASE_URL)

🧪 Local Development
1. Install dependencies
pip install -r requirements.txt

2. Start the server
uvicorn app.main:app --reload

3. Open API docs

http://127.0.0.1:8000/docs

4. View the live dashboard

http://127.0.0.1:8000/static/dashboard.html

📡 WebSocket Endpoints
ws://host/ws/ingest

Used by the mobile app / Raspberry Pi to stream telemetry.

ws://host/ws/stream?token=USER_TOKEN

Used by the dashboard to receive data in real time.

📦 Simulating Data (optional)

You can simulate telemetry without a helmet or mobile app:

python app/mock_sender.py


This connects to /ws/ingest and streams random sensor events.

🔒 Authentication

Firebase token verification is supported.

When Firebase credentials are missing, the backend automatically switches to mocked auth mode (useful for dev & Burp Suite testing).

🛠️ Roadmap / Next Steps

Crash detection ML model (ONNX)

Trip summary analytics

Stress & health signals

Admin dashboard with charts

Push notifications on crash events
