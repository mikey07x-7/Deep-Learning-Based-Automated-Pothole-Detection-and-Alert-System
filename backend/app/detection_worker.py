# app/detection_worker.py

import cv2
import time
import math
import numpy as np
import uuid
from datetime import datetime
import pytz
from pathlib import Path
import logging
import traceback

from .model_infer import PotholeModel
from .supabase_client import supabase
from .utils import write_detection_local

from app.state import current_gps

logger = logging.getLogger(__name__)

VIDEO_PATH = Path(__file__).parent.parent / "video.mp4"
OUTPUT_DIR = Path(__file__).parent.parent / "backend_output_images"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

IST = pytz.timezone("Asia/Kolkata")

# Save every 5 seconds (suitable for 30s video)
SAVE_INTERVAL_SECONDS = 5  


# --------------------------
# Utility: Draw bounding boxes
# --------------------------
def draw_detections(frame, detections):
    """Draw all bounding boxes & confidence on frame."""
    out = frame.copy()
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det["confidence"]
        cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(out, f"{conf:.2f}", (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    return out


# --------------------------
# Worker Class
# --------------------------
class DetectionWorker:

    def __init__(self, model: PotholeModel, min_conf=0.15):
        """Lower min_conf so more frames qualify."""
        self.model = model
        self.min_conf = float(min_conf)

        self.prev_lat = None
        self.prev_lon = None

        self.running = False
        self.sim_increment = 0.0005

        self.last_saved_time = 0  # Timestamp of last saved image

    # --------------------------
    def stop(self):
        logger.info("DetectionWorker stop requested")
        self.running = False

    # --------------------------
    def process_video(self, websocket_broadcast=None):
        cap = cv2.VideoCapture(str(VIDEO_PATH))

        fps = cap.get(cv2.CAP_PROP_FPS) or 25
        # Run YOLO around ~5 FPS
        frame_skip = int(fps // 6) or 1

        self.running = True
        logger.info(f"Starting video processing (frame_skip={frame_skip})")

        frame_idx = 0

        try:
            while self.running and cap.isOpened():

                # ---------- GPS OR SIMULATED ----------
                lat = current_gps["lat"]
                lon = current_gps["lon"]

                if lat is None or lon is None:
                    if self.prev_lat is None:
                        lat, lon = 12.9716, 77.5946
                    else:
                        lat = self.prev_lat + self.sim_increment
                        lon = self.prev_lon + self.sim_increment

                    logger.info(f"Simulated GPS → {lat:.6f}, {lon:.6f}")
                # ---------------------------------------

                ret, frame = cap.read()
                if not ret:
                    logger.info("End of video or cannot read frame")
                    break

                frame_idx += 1
                if frame_idx % frame_skip != 0:
                    continue

                # ---------- YOLO INFERENCE ----------
                try:
                    detections = self.model.infer_frame(frame, conf=self.min_conf)
                except Exception:
                    logger.exception("Inference failed")
                    continue

                if len(detections) == 0:
                    continue  # skip empty frames

                # ---------- SAVE ONLY EVERY X SECONDS ----------
                now = time.time()
                if now - self.last_saved_time < SAVE_INTERVAL_SECONDS:
                    continue  # too soon to save again

                self.last_saved_time = now
                self.prev_lat, self.prev_lon = lat, lon

                # ---------- BUILD UNIQUE FILENAME ----------
                local_time = datetime.now(IST)
                timestamp = local_time.isoformat()

                fname = f"{local_time:%Y%m%d_%H%M%S_%f}_{lat:.5f}_{lon:.5f}.jpg"
                save_path = OUTPUT_DIR / fname

                # ---------- SAVE FULL ANNOTATED FRAME ----------
                annotated = draw_detections(frame, detections)
                cv2.imwrite(str(save_path), annotated)

                # ---------- UPLOAD AND RECORD ----------
                self.upload_and_record(
                    save_path=save_path,
                    lat=lat, lon=lon,
                    detections=detections, timestamp=timestamp,
                    websocket_broadcast=websocket_broadcast
                )

                time.sleep(0.005)

        except Exception as e:
            logger.exception(f"Worker crashed: {e}")

        finally:
            cap.release()
            self.running = False
            logger.info("process_video exiting")

    # --------------------------
    def upload_and_record(self, save_path, lat, lon, detections, timestamp, websocket_broadcast):
        """Upload image + insert detection event row."""
        try:
            with open(save_path, "rb") as f:
                content = f.read()

            bucket = supabase.storage.from_("detections")

            # Upload unique filename
            bucket.upload(str(save_path.name), content, {"content-type": "image/jpeg"})

            pub = bucket.get_public_url(str(save_path.name))
            public_url = pub["publicURL"] if isinstance(pub, dict) else pub

            logger.info(f"Uploaded {save_path.name}")

            # Insert one DB row representing this whole frame
            record = {
                "filename": save_path.name,
                "latitude": lat,
                "longitude": lon,
                "confidence": float(max(d["confidence"] for d in detections)),
                "timestamp": timestamp,
                "status": "not_fixed",
                "detection_count": len(detections),
                "image_url": public_url
            }

            supabase.table("detections").insert(record).execute()
            write_detection_local(record)

            if websocket_broadcast:
                websocket_broadcast(record)

        except Exception as e:
            logger.error(f"Upload/record error: {e}")
            traceback.print_exc()
