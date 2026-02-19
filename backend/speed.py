"""
Speed estimation using pixel displacement between frames.
Assumes a calibration factor (pixels per meter) which can be tuned per camera.
"""

from collections import defaultdict

# Calibration: pixels per meter (tune based on camera height/angle)
PIXELS_PER_METER = 8.0
# FPS used for speed calculation (updated dynamically from detector)
DEFAULT_FPS = 25.0


class SpeedEstimator:
    def __init__(self, fps: float = DEFAULT_FPS, pixels_per_meter: float = PIXELS_PER_METER):
        self.fps = fps
        self.pixels_per_meter = pixels_per_meter
        # track_id -> list of (frame_number, centroid_y)
        self._history: dict[int, list] = defaultdict(list)
        self._speeds: dict[int, float] = {}
        self.frame_count = 0

    def update_fps(self, fps: float):
        self.fps = max(fps, 1.0)

    def update(self, track_id: int, bbox: list) -> float:
        """
        Update tracker with new bbox and return estimated speed in km/h.
        bbox: [x1, y1, x2, y2]
        """
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2

        history = self._history[track_id]
        history.append((self.frame_count, cy))

        # Keep only last 10 frames for rolling average
        if len(history) > 10:
            history.pop(0)

        speed_kmh = 0.0
        if len(history) >= 2:
            frame_diff = history[-1][0] - history[0][0]
            pixel_diff = abs(history[-1][1] - history[0][1])

            if frame_diff > 0:
                meters = pixel_diff / self.pixels_per_meter
                seconds = frame_diff / self.fps
                speed_ms = meters / seconds
                speed_kmh = speed_ms * 3.6

        self._speeds[track_id] = speed_kmh
        self.frame_count += 1
        return round(speed_kmh, 2)

    def get_speed(self, track_id: int) -> float:
        return self._speeds.get(track_id, 0.0)

    def remove_track(self, track_id: int):
        self._history.pop(track_id, None)
        self._speeds.pop(track_id, None)