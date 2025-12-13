# backend/app/utils.py
import csv
import os
from datetime import datetime
import secrets
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
import time
import json

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
OTP_EXPIRY = int(os.getenv("OTP_EXPIRY_SECONDS", "120"))

USERS_CSV = os.path.join(os.path.dirname(__file__), "..", "users_local.csv")
DETECTIONS_CSV = os.path.join(os.path.dirname(__file__), "..", "detections_local.csv")


def send_otp_email(to_email: str, otp: str):
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        raise RuntimeError("Gmail credentials missing")

    msg = EmailMessage()
    msg["Subject"] = "Your RoadSense OTP"
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg.set_content(f"Your OTP for RoadSense is: {otp}\nThis will expire in {OTP_EXPIRY} seconds.")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


def write_user_local(user_dict: dict):
    fieldnames = ["email", "password_hash", "name", "city", "role", "approved", "created_at"]
    exists = os.path.isfile(USERS_CSV)
    with open(USERS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "email": user_dict["email"],
            "password_hash": user_dict["password_hash"],
            "name": user_dict.get("name", ""),
            "city": user_dict.get("city", ""),
            "role": user_dict.get("role", "citizen"),
            "approved": user_dict.get("approved", False),
            "created_at": datetime.utcnow().isoformat()
        })


def write_detection_local(det: dict):
    fieldnames = ["filename","latitude","longitude","confidence","timestamp","fixed_by","fixed_at","status"]
    exists = os.path.isfile(DETECTIONS_CSV)
    with open(DETECTIONS_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow({
            "filename": det["filename"],
            "latitude": det["latitude"],
            "longitude": det["longitude"],
            "confidence": det["confidence"],
            "timestamp": det["timestamp"],
            "fixed_by": det.get("fixed_by", ""),
            "fixed_at": det.get("fixed_at", ""),
            "status": det.get("status", "not_fixed")
        })


# OTP store - simple in-memory; for production use Redis or a DB table
OTP_STORE = {}  # {email: {"otp": "1234", "expiry": 12345678}}

def generate_and_store_otp(email: str):
    otp = str(secrets.randbelow(1000000)).zfill(6)
    expiry = time.time() + OTP_EXPIRY
    OTP_STORE[email] = {"otp": otp, "expiry": expiry}
    return otp

def verify_otp(email: str, otp: str):
    entry = OTP_STORE.get(email)
    if not entry:
        return False
    if time.time() > entry["expiry"]:
        del OTP_STORE[email]
        return False
    if entry["otp"] == otp:
        del OTP_STORE[email]
        return True
    return False
