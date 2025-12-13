# app/routes/detections_routes.py

from fastapi import APIRouter, HTTPException
from ..supabase_client import supabase

router = APIRouter()


# -----------------------------------------------------
# Helper: Generate Supabase Public URL
# -----------------------------------------------------
def get_public_url(path: str):
    return supabase.storage.from_("detections").get_public_url(path)


# -----------------------------------------------------
# Helper: Parse metadata from filename
# -----------------------------------------------------
def parse_filename(filename: str):
    if filename.endswith(".jpg"):
        filename = filename[:-4]  # remove ".jpg"

    parts = filename.split("_")
    if len(parts) != 5:
        return None  # invalid filename format

    raw_date, raw_time, raw_conf, lat, lon = parts

    # Convert into cleaned & human readable fields
    date = f"{raw_date[0:4]}-{raw_date[4:6]}-{raw_date[6:8]}"
    time = f"{raw_time[0:2]}:{raw_time[2:4]}:{raw_time[4:6]}"
    confidence = float(raw_conf) / 1_000_000

    return {
        "date": date,
        "time": time,
        "confidence": confidence,
        "latitude": float(lat),
        "longitude": float(lon),
    }


# -----------------------------------------------------
# GET ALL DETECTIONS (Dashboard)
# -----------------------------------------------------
@router.get("/api/detections")
async def get_detections(order: str = "desc"):
    try:
        res = (
            supabase.table("detections")
            .select("*")
            .order("timestamp", desc=(order == "desc"))
            .execute()
        )

        detections = res.data or []

        for d in detections:
            img_path = d.get("image_path")

            if img_path:
                # public URL
                d["image_url"] = get_public_url(img_path)

                # filename = last part in case path includes folder
                filename = img_path.split("/")[-1]

                # add parsed metadata
                meta = parse_filename(filename)
                if meta:
                    d.update(meta)
            else:
                d["image_url"] = None

        return {"detections": detections}

    except Exception as e:
        raise HTTPException(500, f"Failed loading detections: {e}")


# -----------------------------------------------------
# GET RECENT DETECTIONS (Home)
# -----------------------------------------------------
@router.get("/api/recent-detections")
async def recent_detections():

    res = (
        supabase.table("detections")
        .select("*")
        .order("timestamp", desc=True)
        .limit(20)
        .execute()
    )

    detections = res.data or []

    for d in detections:
        img_path = d.get("image_path")

        if img_path:
            d["image_url"] = get_public_url(img_path)
            filename = img_path.split("/")[-1]

            meta = parse_filename(filename)
            if meta:
                d.update(meta)
        else:
            d["image_url"] = None

    return {"detections": detections}


# -----------------------------------------------------
# MARK DETECTION AS FIXED
# -----------------------------------------------------
@router.post("/api/detections/fix")
async def mark_as_fixed(data: dict):

    detection_id = data.get("id")

    if not detection_id:
        raise HTTPException(400, "Missing detection ID")

    supabase.table("detections") \
        .update({"status": "fixed"}) \
        .eq("id", detection_id) \
        .execute()

    return {"message": "Updated successfully"}
