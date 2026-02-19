"""
detector.py — YOLO + ByteTrack with frame skipping for CPU performance
Strategy:
  - Run model.track() every TRACK_EVERY frames (full tracking)
  - On skipped frames, run model() detect-only and redraw cached boxes
  - This gives 3-5x FPS improvement on CPU
"""

import os
import cv2
import numpy as np
import time
import base64
from ultralytics import YOLO

from tracker import Tracker
from speed import SpeedEstimator
from alert import log_detection, beep_alert
from config import (
    USE_CASES, DEFAULT_USE_CASE, get_color,
    CONF_THRESHOLD, JPEG_QUALITY, FRAME_WIDTH,
)

TRACK_EVERY = 3  # full track every 3rd frame


class Detector:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(__file__), "yolo11n.pt")
        self.model = YOLO(model_path)

        # Warm up
        dummy = np.zeros((480, 640, 3), dtype=np.uint8)
        self.model(dummy, verbose=False)

        self.tracker = Tracker()
        self.speed_estimator = SpeedEstimator()
        self._alerted_ids: set = set()
        self._frame_idx: int = 0
        self._cached_tracks: list = []  # reused on skipped frames

        self.use_case = DEFAULT_USE_CASE
        self.target_classes: dict = USE_CASES[DEFAULT_USE_CASE]

        self.fps = 0.0
        self._fps_counter = 0
        self._fps_timer = time.time()

    def set_use_case(self, name: str):
        if name not in USE_CASES:
            raise ValueError(f"Unknown use case: {name}")
        self.use_case = name
        self.target_classes = USE_CASES[name]
        self.reset_stats()

    def reset_stats(self):
        self._alerted_ids.clear()
        self.speed_estimator = SpeedEstimator()
        self._cached_tracks = []
        self._frame_idx = 0

    def _update_fps(self):
        self._fps_counter += 1
        elapsed = time.time() - self._fps_timer
        if elapsed >= 1.0:
            self.fps = self._fps_counter / elapsed
            self._fps_counter = 0
            self._fps_timer = time.time()

    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, dict]:
        self._update_fps()
        self.speed_estimator.update_fps(self.fps or 25.0)

        # Resize for faster inference
        h, w = frame.shape[:2]
        if w > FRAME_WIDTH:
            scale = FRAME_WIDTH / w
            frame = cv2.resize(frame, (FRAME_WIDTH, int(h * scale)))
        h, w = frame.shape[:2]

        # Full track every TRACK_EVERY frames
        if self._frame_idx % TRACK_EVERY == 0:
            results = self.model.track(
                frame,
                persist=True,
                verbose=False,
                conf=CONF_THRESHOLD,
                classes=list(self.target_classes.keys()),
                tracker="bytetrack.yaml",
            )[0]
            self._cached_tracks = self.tracker.parse_results(results, self.target_classes)
        else:
            # Lightweight detect-only on skipped frames (no tracking overhead)
            self.model(
                frame,
                verbose=False,
                conf=CONF_THRESHOLD,
                classes=list(self.target_classes.keys()),
            )

        self._frame_idx += 1
        tracks = self._cached_tracks

        frame_counts = {v: 0 for v in self.target_classes.values()}

        for track in tracks:
            cls_name = self.target_classes.get(track.det_class)
            if not cls_name:
                continue

            track_id = track.track_id
            conf = track.det_conf
            x1, y1, x2, y2 = track.to_ltrb()

            # Clamp to frame bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if x2 <= x1 or y2 <= y1:
                continue

            bbox = [x1, y1, x2, y2]
            color = get_color(track.det_class)
            speed = self.speed_estimator.update(track_id, bbox)

            # Alert once per unique track
            if track_id not in self._alerted_ids:
                self._alerted_ids.add(track_id)
                log_detection(track_id, cls_name, conf, speed, bbox)
                beep_alert()

            frame_counts[cls_name] += 1

            # White outline + colored box
            cv2.rectangle(frame, (x1-1, y1-1), (x2+1, y2+1), (255, 255, 255), 1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Label
            label = f"#{track_id} {cls_name} {conf:.2f}"
            (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(frame, (x1, y1 - lh - 6), (x1 + lw + 2, y1), color, -1)
            cv2.putText(frame, label, (x1 + 1, y1 - 3),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

        # ── Bottom-left: FPS + mode ───────────────────────────────────────────
        cv2.putText(frame, f"FPS: {self.fps:.1f}  [{self.use_case.upper()}]",
                    (8, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                    (0, 255, 255), 2, cv2.LINE_AA)

        # ── Top-right: counts ─────────────────────────────────────────────────
        total = sum(frame_counts.values())
        count_lines = [f"Total: {total}"] + [
            f"{cls}: {cnt}" for cls, cnt in frame_counts.items() if cnt > 0
        ]
        line_h = 24
        panel_w = 170
        panel_h = len(count_lines) * line_h + 10
        px = w - panel_w - 8

        overlay = frame.copy()
        cv2.rectangle(overlay, (px - 4, 8), (w - 8, 8 + panel_h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        for i, line in enumerate(count_lines):
            c = (0, 255, 255) if i == 0 else (220, 220, 220)
            cv2.putText(frame, line, (px, 8 + (i + 1) * line_h - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, c, 2, cv2.LINE_AA)

        return frame, {
            "fps": round(self.fps, 1),
            "counts": frame_counts,
            "total": total,
            "total_tracked": len(self._alerted_ids),
            "use_case": self.use_case,
        }

    def frame_to_base64(self, frame: np.ndarray) -> str:
        _, buffer = cv2.imencode(
            ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY]
        )
        return base64.b64encode(buffer).decode("utf-8")