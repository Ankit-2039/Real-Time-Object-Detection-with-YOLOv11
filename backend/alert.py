import csv
import os
import threading
from datetime import datetime

LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "detections.csv")

# Ensure CSV exists with headers
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "track_id", "class", "confidence", "speed_kmh", "bbox"])


def log_detection(track_id: int, class_name: str, confidence: float, speed: float, bbox: list):
    """Append a detection event to CSV log."""
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            track_id,
            class_name,
            round(confidence, 3),
            round(speed, 2) if speed else 0.0,
            bbox
        ])


def beep_alert():
    """Play a non-blocking beep sound using pygame."""
    def _beep():
        try:
            import pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            # Generate a simple beep using pygame Sound from buffer
            import numpy as np
            sample_rate = 44100
            duration = 0.15  # seconds
            freq = 880  # Hz
            t = numpy_beep(sample_rate, duration, freq)
            sound = pygame.sndarray.make_sound(t)
            sound.play()
            pygame.time.wait(int(duration * 1000))
        except Exception:
            pass  # Silently fail if audio not available

    def numpy_beep(sample_rate, duration, freq):
        import numpy as np
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
        stereo = np.column_stack([wave, wave])
        return stereo

    thread = threading.Thread(target=_beep, daemon=True)
    thread.start()


def get_logs(limit: int = 100) -> list:
    """Return last N log entries as list of dicts."""
    rows = []
    if not os.path.exists(LOG_FILE):
        return rows
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows[-limit:]