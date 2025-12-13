# backend/app/schemas.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    city: str
    role: str  # "citizen" or "authority"

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ReportRequest(BaseModel):
    latitude: float
    longitude: float
    confidence: float
    description: Optional[str] = None
