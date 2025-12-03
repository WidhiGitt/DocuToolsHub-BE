import os
from supabase import create_client

# Supabase ENV (baik di local .env ataupun Fly secrets)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("SUPABASE_URL atau SUPABASE_KEY tidak ditemukan!")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase():
    return supabase
