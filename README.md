# SENTINEL — Real-Time Object Detection System

A full-stack real-time object detection and tracking system built with **YOLOv11**, **ByteTrack**, **FastAPI**, and **React**.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)
![React](https://img.shields.io/badge/React-18-61dafb)
![YOLOv11](https://img.shields.io/badge/YOLO-v11n-red)

---

## Features

- **Real-time detection** via webcam or video file
- **5 detection modes**: Traffic, Security, Wildlife, Retail, Airport/Railway
- **ByteTrack** object tracking (built into Ultralytics)
- **Speed estimation** (km/h) per tracked object
- **Detection log** saved to CSV automatically
- **Sound alert** on new object detection
- **Live WebSocket stream** from backend to React frontend
- **Dark industrial UI** with FPS counter and per-class counts

---

## Project Structure

```
SENTINEL/
├── START_SENTINEL.bat       # Windows one-click launcher
├── backend/
│   ├── main.py              # FastAPI app + WebSocket endpoints
│   ├── detector.py          # YOLO + ByteTrack pipeline
│   ├── tracker.py           # Tracker wrapper
│   ├── speed.py             # Speed estimation
│   ├── alert.py             # Sound alert + CSV logging
│   ├── config.py            # Use case definitions + constants
│   ├── requirements.txt     # Python dependencies
│   └── logs/                # Auto-created, stores detections.csv
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── main.jsx
│   │   └── components/
│   │       ├── VideoFeed.jsx
│   │       ├── Controls.jsx
│   │       ├── Stats.jsx
│   │       └── AlertLog.jsx
│   ├── index.html
│   ├── vite.config.mjs
│   └── package.json
└── README.md
```

---

## Requirements

### System
- Windows 10/11 (tested), Linux/Mac compatible
- Python 3.10+
- Node.js 18+
- Webcam (optional, for live feed)

### Python dependencies
See `backend/requirements.txt`

### Node dependencies
See `frontend/package.json`

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/sentinel-detection.git
cd sentinel-detection
```

### 2. Backend setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Download YOLO model
```bash
python -c "import urllib.request; urllib.request.urlretrieve('https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11n.pt', 'yolo11n.pt'); print('Downloaded')"
```

### 4. Frontend setup
```bash
cd ../frontend
npm install
```

---

## Running

### Option A — One click (Windows)
Double-click `START_SENTINEL.bat` from the root folder.

### Option B — Manual
**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

Open **http://localhost:3000**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/use-cases` | List all use cases |
| POST | `/use-case/{name}` | Switch detection mode |
| GET | `/logs` | Get detection log entries |
| POST | `/reset` | Reset stats and tracker |
| POST | `/upload` | Upload video file |
| WS | `/ws/stream` | Live webcam WebSocket stream |
| WS | `/ws/video/{file_id}` | Uploaded video WebSocket stream |

---

## Detection Modes

| Mode | Classes Detected |
|------|-----------------|
| Traffic | car, bus, truck, motorcycle, bicycle, traffic light, stop sign |
| Security | person, backpack, handbag, suitcase |
| Wildlife | bird, cat, dog, horse, sheep, cow, elephant, bear, zebra, giraffe |
| Retail | person, bottle, cup, backpack |
| Airport/Railway | person, suitcase, backpack, airplane, train |

---

## Performance (CPU)

| Setting | FPS |
|---------|-----|
| YOLO only (no tracking) | ~25 FPS |
| YOLO + ByteTrack (every frame) | ~3 FPS |
| YOLO + ByteTrack (every 3rd frame) | ~10-15 FPS |

> For 30+ FPS, a NVIDIA GPU with CUDA is recommended.

---

## License

MIT License — free to use, modify and distribute.
