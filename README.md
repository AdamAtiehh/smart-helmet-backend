smart_helmet_backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entrypoint (starts WS + background workers)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py        # SQLAlchemy database tables
│   │   └── schemas.py          # Pydantic models for validation (TelemetryIn, AlertOut)
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py       # Database engine + session setup
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── persist_worker.py   # Saves telemetry data to DB
│   │   └── inference_worker.py # Runs ML model → generates alerts → saves + broadcasts
│   │
│   ├── ml/
│   │   ├── __init__.py
│   │   ├── model.onnx          # (later) your trained crash-detection model
│   │   └── predictor.py        # Helper to load model + run predictions
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   └── broadcaster.py      # Handles sending messages to /ws/stream clients
│   │
│   ├── static/
│   │   └── listener.html       # Simple front-end dashboard for testing
│   │
│   ├── mock_sender.py          # Simulates Raspberry Pi or Flutter app sending data
│   └── requirements.txt
│
├── helmet.db                   # Local SQLite database (created automatically)
│
├── .env                        # (optional) for DB_URL, model paths, etc.
└── README.md
