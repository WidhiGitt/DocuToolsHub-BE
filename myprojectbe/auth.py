from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from supabase import create_client
import jwt
import time
import os

router = APIRouter(prefix="/auth", tags=["Auth"])

# Load ENV
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("SUPABASE_URL atau SUPABASE_KEY belum di-set!")

if not SECRET_KEY:
    raise Exception("SECRET_KEY belum di-set!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserAuth(BaseModel):
    email: str
    password: str


def create_token(data: dict):
    payload = {
        **data,
        "exp": int(time.time()) + 60 * 60 * 24
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


@router.post("/register")
def register(user: UserAuth):
    email = user.email.strip().lower()
    password = user.password

    hashed_pw = pwd_context.hash(password)

    check = supabase.table("users") \
        .select("*") \
        .eq("email", email) \
        .execute()

    if check.data and len(check.data) > 0:
        raise HTTPException(status_code=400, detail="Email sudah terdaftar.")

    supabase.table("users").insert({
        "email": email,
        "password": hashed_pw
    }).execute()

    return {"message": "Register berhasil"}


@router.post("/login")
def login(user: UserAuth):
    email = user.email.strip().lower()
    password = user.password

    result = supabase.table("users") \
        .select("*") \
        .eq("email", email) \
        .limit(1) \
        .execute()

    if not result.data or len(result.data) == 0:
        raise HTTPException(status_code=404, detail="Email tidak ditemukan.")

    user_db = result.data[0]

    if not pwd_context.verify(password, user_db["password"]):
        raise HTTPException(status_code=400, detail="Password salah.")

    token = create_token({"email": email})

    return {"token": token, "message": "Login berhasil"}
