"""
main.py — FastAPI backend
Endpoints:
  WS  /ws/stream          — live webcam stream
  POST /upload            — upload video file, returns stream via WS
  WS  /ws/video/{file_id} — stream uploaded video
  GET  /logs              — return CSV log entries
  POST /reset             — reset stats
  GET  /health            — health check
"""

import asyncio
import os
import uuid
import cv2
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import aiofiles

from detector import Detector
from alert import get_logs
from config import USE_CASES

app = FastAPI(title="YOLO Traffic Monitor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global detector instance (shared across streams)
detector = Detector()


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Logs ──────────────────────────────────────────────────────────────────────
@app.get("/logs")
async def logs(limit: int = 100):
    return JSONResponse(content=get_logs(limit))


# ── Reset stats ───────────────────────────────────────────────────────────────
@app.post("/reset")
async def reset():
    detector.reset_stats()
    return {"message": "Stats reset"}


# ── Use case switch ───────────────────────────────────────────────────────────
@app.get("/use-cases")
async def list_use_cases():
    return {"use_cases": list(USE_CASES.keys()), "current": detector.use_case}


@app.post("/use-case/{name}")
async def set_use_case(name: str):
    try:
        detector.set_use_case(name)
        return {"message": f"Switched to {name}", "classes": list(USE_CASES[name].values())}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# ── Upload video ──────────────────────────────────────────────────────────────
@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in [".mp4", ".avi", ".mov", ".mkv"]:
        return JSONResponse(status_code=400, content={"error": "Unsupported format"})

    file_id = str(uuid.uuid4())
    dest = os.path.join(UPLOAD_DIR, f"{file_id}{ext}")

    async with aiofiles.open(dest, "wb") as f:
        content = await file.read()
        await f.write(content)

    return {"file_id": file_id, "filename": file.filename}


# ── WebSocket: Webcam stream ──────────────────────────────────────────────────
@app.websocket("/ws/stream")
async def webcam_stream(websocket: WebSocket):
    await websocket.accept()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        await websocket.send_json({"error": "Webcam not accessible"})
        await websocket.close()
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            annotated, stats = detector.process_frame(frame)
            b64 = detector.frame_to_base64(annotated)

            await websocket.send_json({
                "frame": b64,
                "stats": stats,
            })
            await asyncio.sleep(0.01)  # ~max 60fps cap

    except WebSocketDisconnect:
        pass
    finally:
        cap.release()


# ── WebSocket: Video file stream ──────────────────────────────────────────────
@app.websocket("/ws/video/{file_id}")
async def video_stream(websocket: WebSocket, file_id: str):
    await websocket.accept()

    # Find uploaded file
    matched = None
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(file_id):
            matched = os.path.join(UPLOAD_DIR, fname)
            break

    if not matched:
        await websocket.send_json({"error": "File not found"})
        await websocket.close()
        return

    cap = cv2.VideoCapture(matched)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_delay = 1.0 / fps

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                await websocket.send_json({"done": True})
                break

            annotated, stats = detector.process_frame(frame)
            b64 = detector.frame_to_base64(annotated)

            await websocket.send_json({
                "frame": b64,
                "stats": stats,
            })
            await asyncio.sleep(frame_delay)

    except WebSocketDisconnect:
        pass
    finally:
        cap.release()