# app/routes/auth_routes.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from app.supabase_client import supabase
import bcrypt
import random
import os
import smtplib
from email.mime.text import MIMEText

router = APIRouter()

# Store OTP temporarily
otp_store = {}   # {email: {"otp": "123456", "expires": datetime}}

# ----------------------------
# MODELS
# ----------------------------

class SendOtpModel(BaseModel):
    email: EmailStr

class VerifyOtpModel(BaseModel):
    email: EmailStr
    otp: str

class RegisterModel(BaseModel):
    email: EmailStr
    password: str
    name: str
    city: str
    role: str   # "citizen" or "authority"

class LoginModel(BaseModel):
    email: EmailStr
    password: str


# ----------------------------
# EMAIL SENDER
# ----------------------------

def send_email_otp(receiver_email: str, otp: str):
    sender = os.getenv("GMAIL_USER")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender or not app_password:
        print("⚠ Missing Gmail SMTP credentials")
        return False

    msg = MIMEText(
        f"Your RoadSense OTP is: {otp}\n\nThis OTP is valid for 2 minutes."
    )
    msg["Subject"] = "RoadSense OTP Verification"
    msg["From"] = sender
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, [receiver_email], msg.as_string())

        print(f"📨 OTP sent to {receiver_email}")
        return True

    except Exception as e:
        print("🚨 Email send error:", e)
        return False


# ----------------------------
# SEND REGISTER OTP
# ----------------------------

@router.post("/auth/send-register-otp")
async def send_register_otp(data: SendOtpModel):
    code = str(random.randint(100000, 999999))

    otp_store[data.email] = {
        "otp": code,
        "expires": datetime.utcnow() + timedelta(minutes=2)
    }

    print(f"[OTP FOR {data.email}] = {code}")
    send_email_otp(data.email, code)

    return {"message": "OTP sent"}


# ----------------------------
# VERIFY REGISTER OTP
# ----------------------------

@router.post("/auth/verify-register-otp")
async def verify_register_otp(data: VerifyOtpModel):
    entry = otp_store.get(data.email)

    if not entry:
        raise HTTPException(400, "OTP not generated")
    if datetime.utcnow() > entry["expires"]:
        raise HTTPException(400, "OTP expired")
    if entry["otp"] != data.otp:
        raise HTTPException(400, "Invalid OTP")

    return {"message": "OTP verified"}


# ----------------------------
# REGISTER (AUTO-APPROVAL ENABLED)
# ----------------------------

@router.post("/auth/register")
async def register(data: RegisterModel):

    hashed_pw = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt()).decode()

    # AUTO APPROVE ALL USERS (citizen & authority)
    approved_value = True

    try:
        res = supabase.table("users").insert({
            "email": data.email,
            "password": hashed_pw,
            "name": data.name,
            "city": data.city,
            "role": data.role,
            "approved": approved_value
        }).execute()

        if not res.data:
            raise HTTPException(500, "Registration failed")

        return {
            "message": "Registered successfully",
            "approved": True
        }

    except Exception as e:
        err = str(e)
        if "duplicate" in err or "23505" in err:
            raise HTTPException(400, "Email already registered")
        raise HTTPException(500, f"Registration error: {err}")


# ----------------------------
# LOGIN (AUTO-APPROVAL MODE)
# ----------------------------

@router.post("/auth/login")
async def login(data: LoginModel):
    res = supabase.table("users").select("*").eq("email", data.email).execute()

    if not res.data:
        raise HTTPException(400, "Invalid email or password")

    user = res.data[0]

    if not bcrypt.checkpw(data.password.encode(), user["password"].encode()):
        raise HTTPException(400, "Invalid email or password")

    return {
        "message": "Login successful",
        "token": "roadsense-session-token",
        "email": user["email"],
        "role": user["role"],
        "name": user["name"],
        "city": user["city"]
    }
