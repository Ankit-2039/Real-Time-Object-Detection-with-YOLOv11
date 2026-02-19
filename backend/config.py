"""
config.py — Use case definitions and COCO class mappings
"""

# Full COCO class map: id -> name
COCO_CLASSES = {
    0: "person", 1: "bicycle", 2: "car", 3: "motorcycle", 4: "airplane",
    5: "bus", 6: "train", 7: "truck", 8: "boat", 9: "traffic light",
    10: "fire hydrant", 11: "stop sign", 12: "parking meter", 13: "bench",
    14: "bird", 15: "cat", 16: "dog", 17: "horse", 18: "sheep", 19: "cow",
    20: "elephant", 21: "bear", 22: "zebra", 23: "giraffe", 24: "backpack",
    25: "umbrella", 26: "handbag", 28: "suitcase", 29: "frisbee",
    39: "bottle", 41: "cup", 62: "tv", 63: "laptop", 67: "cell phone",
    73: "clock",
}

# Use case presets: name -> { coco_id: label }
USE_CASES = {
    "traffic": {
        2: "car", 5: "bus", 7: "truck", 3: "motorcycle",
        1: "bicycle", 9: "traffic light", 11: "stop sign",
    },
    "security": {
        0: "person", 24: "backpack", 26: "handbag", 28: "suitcase",
    },
    "wildlife": {
        14: "bird", 15: "cat", 16: "dog", 17: "horse",
        18: "sheep", 19: "cow", 20: "elephant", 21: "bear",
        22: "zebra", 23: "giraffe",
    },
    "retail": {
        0: "person", 39: "bottle", 41: "cup", 24: "backpack",
    },
    "airport": {
        0: "person", 28: "suitcase", 24: "backpack", 4: "airplane",
        6: "train",  # railway too
    },
}

# Distinct BGR colors per class id (auto-generated, consistent)
def get_color(class_id: int) -> tuple:
    palette = [
        (0, 255, 0), (255, 165, 0), (0, 0, 255), (0, 255, 255),
        (255, 0, 255), (255, 255, 0), (128, 0, 255), (0, 128, 255),
        (255, 128, 0), (0, 255, 128), (128, 255, 0), (255, 0, 128),
    ]
    return palette[class_id % len(palette)]

DEFAULT_USE_CASE = "traffic"
CONF_THRESHOLD = 0.5
ALERT_SPEED_THRESHOLD = 80.0   # km/h
TARGET_FPS = 30
JPEG_QUALITY = 85               # higher = better box visibility
FRAME_WIDTH = 640               # smaller = faster inference on CPU