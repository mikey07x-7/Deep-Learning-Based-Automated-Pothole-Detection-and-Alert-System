# backend/app/auth.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from .schemas import RegisterRequest, OTPRequest, OTPVerifyRequest, LoginRequest
from .supabase_client import supabase
from .utils import send_otp_email, generate_and_store_otp, verify_otp, write_user_local
from passlib.hash import bcrypt
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])
HEAD_EMAIL = os.getenv("HEAD_AUTH_EMAIL")
HEAD_PASS = os.getenv("HEAD_AUTH_PASSWORD")

@router.post("/send-register-otp")
async def send_register_otp(req: OTPRequest, background_tasks: BackgroundTasks):
    otp = generate_and_store_otp(req.email)
    # send email in background
    background_tasks.add_task(send_otp_email, req.email, otp)
    return {"ok": True, "message": "OTP sent (check email)"}

@router.post("/verify-register-otp")
async def verify_register_otp(data: OTPVerifyRequest, reg: RegisterRequest=None):
    # This endpoint expects OTP verification plus registration details in request body (some clients call separately)
    if not verify_otp(data.email, data.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    # If verification passed, create user record in Supabase and local CSV
    # In actual usage, registration details should be present in the request - here for brevity assume later call
    return {"ok": True}

@router.post("/register")
async def register(req: RegisterRequest):
    # register user after OTP verification already done
    # if role==authority -> set approved=False in supabase (head must approve)
    approved = True if req.role == "citizen" else False
    if req.email == HEAD_EMAIL:
        # head is auto-approved
        approved = True

    # hash password
    pwd_hash = bcrypt.hash(req.password)
    # Insert into Supabase table 'users' (create this table with columns below)
    data = {
        "email": req.email,
        "password_hash": pwd_hash,
        "name": req.name,
        "city": req.city,
        "role": req.role,
        "approved": approved,
        "created_at": datetime.utcnow().isoformat()
    }
    # local csv
    write_user_local({"email": req.email, "password_hash": pwd_hash, "name": req.name, "city": req.city, "role": req.role, "approved": approved})
    # Save to Supabase
    supabase.table("users").insert(data).execute()

    return {"ok": True, "approved": approved}

@router.post("/send-forgot-otp")
async def send_forgot_otp(req: OTPRequest, background_tasks: BackgroundTasks):
    otp = generate_and_store_otp(req.email)
    background_tasks.add_task(send_otp_email, req.email, otp)
    return {"ok": True}

@router.post("/verify-forgot-otp")
async def verify_forgot(req: OTPVerifyRequest):
    if not verify_otp(req.email, req.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    return {"ok": True}

@router.post("/reset-password")
async def reset_password(email: str, new_password: str):
    # hash and update supabase
    pwd_hash = bcrypt.hash(new_password)
    supabase.table("users").update({"password_hash": pwd_hash}).eq("email", email).execute()
    # update local CSV - naive approach: append new entry; better to rewrite csv in production
    write_user_local({"email": email, "password_hash": pwd_hash, "name": "", "city": "", "role": "citizen", "approved": True})
    return {"ok": True}
