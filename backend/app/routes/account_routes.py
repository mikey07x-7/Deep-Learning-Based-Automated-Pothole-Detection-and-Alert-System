# app/routes/account_routes.py
from fastapi import APIRouter, HTTPException
from app.supabase_client import supabase

router = APIRouter()

@router.get("/api/account")
async def get_account(email: str):
    try:
        res = supabase.table("users").select("*").eq("email", email).execute()

        if not res.data:
            raise HTTPException(404, "Account not found")

        return res.data[0]

    except Exception as e:
        raise HTTPException(500, f"Failed to fetch account: {e}")
