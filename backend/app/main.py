# app/main.py

import uvicorn
import threading
import time
import logging
import asyncio
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime

# -------------------------
# Import routers
# -------------------------
from .routes.auth_routes import router as auth_router
from .routes.detections_routes import router as detections_router
from .websocket_server import router as ws_router, broadcast
from .routes.account_routes import router as account_router

from fastapi.staticfiles import StaticFiles

# Serve local detection images folder

# -------------------------
# Core modules
# -------------------------
from .supabase_client import supabase
from .utils import write_detection_local
from .model_infer import PotholeModel
from .detection_worker import DetectionWorker

# -------------------------
# CORS
# -------------------------
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="RoadSense Backend API")
app.mount(
    "/local-images",
    StaticFiles(directory="E:/pothole-system/backend/backend_output_images"),
    name="local-images"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Include Routes
# -------------------------
app.include_router(auth_router)
app.include_router(detections_router)
app.include_router(ws_router)
app.include_router(account_router)
# -------------------------
# Logging Setup
# -------------------------
logger = logging.getLogger("roadsense")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

from .supabase_client import supabase

def get_public_url(path: str):
    return supabase.storage.from_("detections").get_public_url(path)

# =====================================================
# SHARED GLOBAL STATE
# =====================================================
from .state import current_gps


class GPSUpdate(BaseModel):
    lat: float
    lon: float


@app.post("/api/gps")
async def update_gps(gps: GPSUpdate):
    current_gps["lat"] = gps.lat
    current_gps["lon"] = gps.lon
    return {"ok": True, "gps": gps}


# =====================================================
# MODEL + WORKER GLOBALS
# =====================================================
model: PotholeModel | None = None
worker: DetectionWorker | None = None

_detection_thread = None
_detection_running = False
_detection_thread_lock = threading.Lock()


# =====================================================
# STARTUP → Load model
# =====================================================
@app.on_event("startup")
async def startup_event():
    global model, worker
    try:
        model = PotholeModel()
        worker = DetectionWorker(model=model)
        logger.info("PotholeModel loaded on startup.")
    except Exception as e:
        logger.exception("Failed loading model: %s", e)


# =====================================================
# SHUTDOWN
# =====================================================
@app.on_event("shutdown")
async def shutdown_event():
    global _detection_running, worker
    _detection_running = False
    if worker:
        try:
            worker.stop()
        except:
            pass
    logger.info("Shutdown completed.")


# =====================================================
# HEALTH CHECK
# =====================================================
@app.get("/health")
async def health():
    return {
        "ok": True,
        "model_loaded": model is not None,
        "detection_running": _detection_running,
        "gps": current_gps,
    }


# =====================================================
# GEOJSON ENDPOINT
# =====================================================
@app.get("/api/detections.geojson")
async def detections_geojson():
    res = supabase.table("detections").select("*").execute()
    rows = res.data or []

    # Sort newest → oldest
    rows.sort(key=lambda x: x.get("timestamp") or "", reverse=True)

    features = []

    for row in rows:
        lat = row.get("latitude")
        lon = row.get("longitude")
        if lat is None or lon is None:
            continue

        public_url = supabase.storage.from_("detections").get_public_url(row["filename"])
        if isinstance(public_url, dict):
            public_url = public_url.get("publicURL") or public_url.get("public_url")

        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {
                "id": row.get("id"),
                "filename": row.get("filename"),
                "confidence": row.get("confidence"),
                "timestamp": row.get("timestamp"),
                "status": row.get("status"),
                "public_url": public_url,
            }
        })

    return {"type": "FeatureCollection", "features": features}


# =====================================================
# REPORT — Citizen uploads a manual pothole report
# =====================================================
@app.post("/api/report")
async def api_report(
    latitude: str = Form(...),
    longitude: str = Form(...),
    confidence: str = Form(...),
    description: str = Form(None),
    file: UploadFile = File(...)
):
    contents = await file.read()
    filename = f"{int(time.time())}_{file.filename}"

    supabase.storage.from_("detections").upload(
        filename, contents, {"content-type": file.content_type}
    )

    pub_resp = supabase.storage.from_("detections").get_public_url(filename)
    if isinstance(pub_resp, dict):
        public_url = pub_resp.get("publicURL") or pub_resp.get("public_url")
    else:
        public_url = pub_resp

    record = {
        "filename": filename,
        "latitude": float(latitude),
        "longitude": float(longitude),
        "confidence": float(confidence),
        "description": description,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "not_fixed",
    }

    supabase.table("detections").insert(record).execute()
    write_detection_local(record)

    await broadcast(record)

    return {"ok": True, "public_url": public_url}


# =====================================================
# Detection Worker Thread
# =====================================================
def _worker_thread(sync_broadcast):
    global _detection_running

    try:
        _detection_running = True
        if worker is None:
            logger.error("Worker not loaded.")
            return

        worker.process_video(websocket_broadcast=sync_broadcast)

    except Exception as e:
        logger.exception("Worker thread error: %s", e)

    finally:
        _detection_running = False
        logger.info("Detection thread stopped.")


# =====================================================
# START DETECTION
# =====================================================
@app.post("/start-detection")
async def start_detection():
    global _detection_thread, _detection_running

    if worker is None:
        raise HTTPException(503, "Worker or model not loaded.")

    loop = asyncio.get_event_loop()

    def sync_broadcast(record):
        asyncio.run_coroutine_threadsafe(broadcast(record), loop)

    with _detection_thread_lock:
        if _detection_running:
            return {"ok": False, "message": "Already running"}

        _detection_thread = threading.Thread(
            target=_worker_thread,
            args=(sync_broadcast,),
            daemon=True,
        )
        _detection_thread.start()

    return {"ok": True, "message": "Detection started."}


# =====================================================
# STOP DETECTION
# =====================================================
@app.post("/stop-detection")
async def stop_detection():
    global _detection_running, worker
    _detection_running = False
    if worker:
        worker.stop()
    return {"ok": True, "message": "Stopping detection…"}


# =====================================================
# RUNNER
# =====================================================
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
