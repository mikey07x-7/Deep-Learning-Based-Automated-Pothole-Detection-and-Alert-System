# app/model_infer.py
from ultralytics import YOLO
import cv2
import numpy as np
import torch
from pathlib import Path
from PIL import Image
import logging

logger = logging.getLogger(__name__)

MODEL_PATH = Path(__file__).parent.parent / "pothole.pt"


class PotholeModel:
    def __init__(self, model_path=MODEL_PATH, device=None, conf=0.5, imgsz=640):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.conf = float(conf)
        self.imgsz = int(imgsz)

        logger.info(f"Loading YOLO model from {model_path} on device={self.device}")
        self.model = YOLO(str(model_path))

        # Warmup
        try:
            dummy = np.zeros((self.imgsz, self.imgsz, 3), dtype=np.uint8)
            self.model.predict(dummy, imgsz=self.imgsz, conf=self.conf, device=self.device, verbose=False)
            logger.info("Model warmup complete")
        except Exception as e:
            logger.warning(f"WARMUP FAILED: {e}")

    # --------------------------------------------------
    def infer_frame(self, frame, conf=None, iou=0.45):
        """
        Runs YOLO inference and returns:
        [
            { "bbox": [x1,y1,x2,y2], "confidence": float, "class": int }
        ]
        """

        conf = conf or self.conf
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.model.predict(
            rgb,
            imgsz=self.imgsz,
            conf=conf,
            iou=iou,
            device=self.device,
            verbose=False
        )[0]

        out = []

        if result.boxes is not None:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                out.append({
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "confidence": float(box.conf[0]),
                    "class": int(box.cls[0]),
                })

        return out


# --------------------------------------------------
def save_detection_crop(frame, bbox, save_path):
    """
    Saves the detected bounding box region as an image.
    """
    x1, y1, x2, y2 = bbox
    crop = frame[y1:y2, x1:x2]
    image = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB))
    image.save(save_path)
