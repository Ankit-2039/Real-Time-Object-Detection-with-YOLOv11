"""
tracker.py — Wrapper around YOLO's built-in tracker (ByteTrack)
Much faster than DeepSORT on CPU, no extra dependencies.
YOLO handles both detection + tracking in a single call.
"""


class Track:
    """Normalised track object from YOLO result."""
    def __init__(self, track_id, cls_id, conf, bbox):
        self.track_id = int(track_id)
        self.det_class = int(cls_id)
        self.det_conf = float(conf)
        self._bbox = bbox  # [x1, y1, x2, y2]

    def to_ltrb(self):
        return self._bbox

    def is_confirmed(self):
        return True  # YOLO only returns confirmed tracks


class Tracker:
    """
    Stateless wrapper — YOLO model runs tracking internally.
    Call update() with the YOLO result object directly.
    """

    def __init__(self, embedder=None):
        pass  # No init needed, YOLO manages state

    def parse_results(self, results, target_classes: dict) -> list:
        """
        Parse YOLO tracking results into Track objects.
        Args:
            results: YOLO model output (single frame)
            target_classes: {coco_id: label}
        Returns:
            list of Track objects
        """
        tracks = []
        if results.boxes is None or results.boxes.id is None:
            return tracks

        for i, box in enumerate(results.boxes):
            cls_id = int(box.cls[0])
            if cls_id not in target_classes:
                continue

            track_id = int(results.boxes.id[i])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            tracks.append(Track(track_id, cls_id, conf, [x1, y1, x2, y2]))

        return tracks

    def reset(self):
        pass  # YOLO tracker resets via persist=False on next call